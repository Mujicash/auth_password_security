# auth_password_security

Odoo module that enforces robust password policies and session expiration rules for enhanced user security.

## 🔐 Features

- Define minimum password length, complexity (uppercase, lowercase, digits, special characters), and history.
- Enforce password expiration after a configurable number of days.
- Block password reuse for a defined number of past passwords.
- Configure a cooldown time between password resets.
- Auto-logout inactive sessions based on system-defined delay.
- Settings are defined per company. 

## 🧩 Dependencies

This module depends on the following Odoo modules:

- `auth_signup`
- `auth_password_policy_signup`

## ⚙️ Configuration Settings

All settings are available under **Settings > General Settings**, and are configurable per company:

| Setting                      | Default | Description                                                                 |
|-----------------------------|---------|-----------------------------------------------------------------------------|
| `password_expiration`       | 60      | Days until passwords expire                                                |
| `password_length`           | 12      | Minimum number of characters in password *(linked to `minlength` param)*  |
| `password_lower`            | 1       | Minimum number of lowercase letters                                        |
| `password_upper`            | 1       | Minimum number of uppercase letters                                        |
| `password_numeric`          | 1       | Minimum number of digits                                                   |
| `password_special`          | 1       | Minimum number of special characters (e.g., !@#$)                          |
| `password_history`          | 30      | Prevent reuse of this many previous passwords                              |
| `password_minimum`          | 24      | Cooldown in hours before a user can reset password again                   |
| `session_duration`          | 5       | Hour of day (1–24) when user sessions are forcefully closed                |
| `day_alert_expire`          | 7       | Number of days before expiration when alert emails will be sent            |
| `test_password_expiration`  | False   | If enabled, expiration is measured in minutes (useful for testing)         |

> Password policy is enforced on password change or reset. Session expiration is checked during login or authenticated requests.