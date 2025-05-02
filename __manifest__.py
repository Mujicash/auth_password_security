{
    "name": "Password Security & Session Control",
    "summary": """
        Enforce password policies: complexity, expiration, history, and session auto-logout.
    """,
    "version": "16.0.1.0.0",
    "author": "Andre Mujica",
    "website": "https://github.com/Mujicash/auth_password_security",
    "category": "Authentication",
    "depends": [
        "auth_signup",
        "auth_password_policy_signup",
    ],
    "license": "LGPL-3",
    "data": [
        "data/email_template_password_expire_notification.xml",
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
        "security/ir.model.access.csv",
        "security/res_users_pass_history_security.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "application": False,
    "auto_install": False,
}
