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
        "views/res_config_settings_views.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "application": False,
    "auto_install": False,
}
