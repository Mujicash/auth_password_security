from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    password_expiration = fields.Integer(
        related="company_id.password_expiration",
        readonly=False
    )
    password_minimum = fields.Integer(
        related="company_id.password_minimum",
        readonly=False
    )
    password_history = fields.Integer(
        related="company_id.password_history",
        readonly=False
    )
    password_lower = fields.Integer(
        related="company_id.password_lower",
        readonly=False
    )
    password_upper = fields.Integer(
        related="company_id.password_upper",
        readonly=False
    )
    password_numeric = fields.Integer(
        related="company_id.password_numeric",
        readonly=False
    )
    password_special = fields.Integer(
        related="company_id.password_special",
        readonly=False
    )
    test_password_expiration = fields.Boolean(
        related="company_id.test_password_expiration",
        readonly=False
    )
    session_duration = fields.Integer(
        related="company_id.session_duration",
        readonly=False
    )
    day_alert_expire = fields.Integer(
        related="company_id.day_alert_expire",
        readonly=False
    )