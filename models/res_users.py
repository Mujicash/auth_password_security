import re
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging
import pytz
from os import utime
from os.path import getmtime
from time import time

from odoo import api, http, models
from odoo.http import SessionExpiredException
_logger = logging.getLogger(__name__)

def delta_now(**kwargs):
    return datetime.now() + timedelta(**kwargs)


class ResUsers(models.Model):
    _inherit = "res.users"

    password_write_date = fields.Datetime(
        string="Last password update",
        default=fields.Datetime.now,
        readonly=True
    )
    password_history_ids = fields.One2many(
        string="Password History",
        comodel_name="res.users.pass.history",
        inverse_name="user_id",
        readonly=True,
    )

    def write(self, vals):
        if vals.get("password"):
            vals["password_write_date"] = fields.Datetime.now()
        return super(ResUsers, self).write(vals)

    @api.model
    def get_password_policy(self):
        data = super(ResUsers, self).get_password_policy()
        company_id = self.env.user.company_id
        data.update({
            "password_lower": company_id.password_lower,
            "password_upper": company_id.password_upper,
            "password_numeric": company_id.password_numeric,
            "password_special": company_id.password_special,
        })
        return data

    def _check_password_policy(self, passwords):
        result = super(ResUsers, self)._check_password_policy(passwords)

        for password in passwords:
            if not password:
                continue
            self._check_password(password)

        return result

    def password_match_message(self):
        self.ensure_one()
        company_id = self.company_id
        message = []
        if company_id.password_lower:
            message.append(
                _("\n* Lowercase letter (at least %s characters)")
                % str(company_id.password_lower)
            )
        if company_id.password_upper:
            message.append(
                _("\n* Uppercase letter (at least %s characters)")
                % str(company_id.password_upper)
            )
        if company_id.password_numeric:
            message.append(
                _("\n* Numeric digit (at least %s characters)")
                % str(company_id.password_numeric)
            )
        if company_id.password_special:
            message.append(
                _("\n* Special character (at least %s characters)")
                % str(company_id.password_special)
            )
        if message:
            message = [_("Must contain the following:")] + message

        params = self.env["ir.config_parameter"].sudo()
        minlength = params.get_param("auth_password_policy.minlength", default=0)
        if minlength:
            message = [
                _("\nPassword must be %d characters or more.\n") % int(minlength)
            ] + message
        return "\r".join(message)

    def _check_password(self, password):
        self._check_password_rules(password)
        self._check_password_history(password)
        return True

    def _check_password_rules(self, password):
        self.ensure_one()
        if not password:
            return True
        company_id = self.company_id
        params = self.env["ir.config_parameter"].sudo()
        minlength = params.get_param("auth_password_policy.minlength", default=0)
        password_regex = [
            "^",
            "(?=.*?[a-z]){" + str(company_id.password_lower) + ",}",
            "(?=.*?[A-Z]){" + str(company_id.password_upper) + ",}",
            "(?=.*?\\d){" + str(company_id.password_numeric) + ",}",
            r"(?=.*?[\W_]){" + str(company_id.password_special) + ",}",
            ".{%d,}$" % int(minlength),
        ]
        if not re.search("".join(password_regex), password):
            raise ValidationError(self.password_match_message())

        return True

    def _password_has_expired(self):
        self.ensure_one()
        if not self.password_write_date:
            return True

        if not self.company_id.password_expiration:
            return False

        if self.company_id.test_password_expiration:
            _logger.info("Expiration time calculated in minutes")
            time = (fields.Datetime.now() - self.password_write_date).total_seconds() / 60
        else:
            _logger.info("Expiration time calculated in days")
            time = (fields.Datetime.now() - self.password_write_date).days

        return time > self.company_id.password_expiration
    
    def _session_has_expired(self):
        """
        Check if the user's session has expired according to session_policy.session_duration
        :return: True if session has expired, False otherwise
        """
        self.ensure_one()

        if not self.login_date:
            return True

        # Get the session duration from the company settings
        session_duration = int(self.company_id.session_duration)
        _logger.info(f"Session duration: {session_duration}")
        
        if session_duration <= 0:
            return False

        # Check if session_duration is a valid hour (1-24)
        hour = max(1, min(session_duration, 24)) % 24
        user_tz = self.tz or 'UTC'
        tz = pytz.timezone(user_tz)

        # Current dates and login dates in the user's timezone
        current_time = pytz.utc.localize(fields.Datetime.now()).astimezone(tz)
        login_datetime = pytz.utc.localize(self.login_date).astimezone(tz)

        # Calculate the session expiration time
        session_expiration = login_datetime.replace(hour=hour, minute=0, second=0, microsecond=0)

        # If the login time is after the session expiration time, add a day to the expiration time
        if login_datetime > session_expiration:
            session_expiration += timedelta(days=1)

        return current_time > session_expiration


    def action_expire_password(self):
        expiration = delta_now(days=+1)
        for user in self:
            user.mapped("partner_id").signup_prepare(
                signup_type="reset", expiration=expiration
            )

    def _validate_pass_reset(self):
        """It provides validations before initiating a pass reset email
        :raises: UserError on invalidated pass reset attempt
        :return: True on allowed reset
        """
        for user in self:
            pass_min = user.company_id.password_minimum
            if pass_min <= 0:
                continue
            write_date = user.password_write_date
            if write_date and write_date + timedelta(hours=pass_min) > datetime.now():
                raise UserError(
                    _(
                        "Passwords can only be reset every %d hour(s). "
                        "Please contact an administrator for assistance."
                    )
                    % pass_min
                )
        return True

    def _check_password_history(self, password):
        """It validates proposed password against existing history
        :raises: UserError on reused password
        """
        crypt = self._crypt_context()
        for user in self:
            password_history = user.company_id.password_history
            if not password_history:  # disabled
                recent_passes = self.env["res.users.pass.history"]
            elif password_history < 0:  # unlimited
                recent_passes = user.password_history_ids
            else:
                recent_passes = user.password_history_ids[:password_history]
            if recent_passes.filtered(
                lambda r: crypt.verify(password, r.password_crypt)
            ):
                raise UserError(
                    _("Cannot use the most recent %d passwords")
                    % user.company_id.password_history
                )

    def _set_encrypted_password(self, uid, pw):
        """It saves password crypt history for history rules"""
        res = super(ResUsers, self)._set_encrypted_password(uid, pw)

        self.env["res.users.pass.history"].create(
            {
                "user_id": uid,
                "password_crypt": pw,
            }
        )
        return res

    def action_reset_password(self):
        """Disallow password resets inside of Minimum Hours"""
        if not self.env.context.get("install_mode") and not self.env.context.get(
            "create_user"
        ):
            if not self.env.user._is_admin():
                users = self.filtered(lambda user: user.active)
                users._validate_pass_reset()
        return super(ResUsers, self).action_reset_password()
    

    def action_send_password_expire(self):        
        users = self.env['res.users'].sudo().search([
            ('active', '=', True),
            ('partner_id.email', '!=', False)
        ], order='id asc')

        for user in users:
            password_expiration = int(user.company_id.password_expiration)
            days_before = int(user.company_id.day_alert_expire)

            delta_days = (user.password_write_date + timedelta(days=password_expiration) - datetime.today()).days

            if delta_days <= days_before:
                user._send_notification_password_expire(delta_days)

    def _send_notification_password_expire(self, delta_days):
        self.action_expire_password()
        template = self.env.ref('italtel_security.email_template_password_expire_notification', False)

        if not template:
            raise ValidationError('Email template not found: "Notify Password Expiration"')
        
        template.with_context({'day_remain': delta_days}).send_mail(self.id)
