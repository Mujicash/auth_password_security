from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    password_expiration = fields.Integer(
        string="Days",
        default=60,
        help="How many days until passwords expire",
    )
    password_lower = fields.Integer(
        string="Lowercase",
        default=1,
        help="Require number of lowercase letters",
    )
    password_upper = fields.Integer(
        string="Uppercase",
        default=1,
        help="Require number of uppercase letters",
    )
    password_numeric = fields.Integer(
        string="Numeric",
        default=1,
        help="Require number of numeric digits",
    )
    password_special = fields.Integer(
        string="Special",
        default=1,
        help="Require number of unique special characters",
    )
    password_history = fields.Integer(
        string="History",
        default=30,
        help="Disallow reuse of this many previous passwords - use negative number for infinite, or 0 to disable",
    )
    password_minimum = fields.Integer(
        string="Minimum Hours",
        default=24,
        help="Amount of hours until a user may change password again",
    )
    test_password_expiration = fields.Boolean(
        string="Test Expiration",
        default=False,
        help="If enabled, the expiration time will change from days to minutes."
    )
    session_duration = fields.Integer(
        string="Session Duration",
        default=5,
        help="Time of day when user sessions expire (between 1 and 24, in the user's time zone)."
    )
    day_alert_expire = fields.Integer(
        string="Password alert about to expire",
        default=7,
        help="Number of days before password expiration in which alerts will be sent to users."
    )
