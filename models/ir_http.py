import werkzeug
import werkzeug.exceptions
import werkzeug.routing
import logging

from odoo import api, http, models
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.service import security

_logger = logging.getLogger(__name__)

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @staticmethod
    def _logout_and_reset_env():
        """
        Close the current session and update the environment.
        """
        request.session.logout(keep_db=True)
        request.env = api.Environment(request.env.cr, None, request.session.context)

    @classmethod
    def _authenticate(cls, endpoint):
        auth = 'none' if http.is_cors_preflight(request, endpoint) else endpoint.routing['auth']

        try:
            if request.session.uid is not None:
                user = request.env['res.users'].browse(request.session.uid)

                # Check if the user is not public and not admin
                if not user._is_public() and not user._is_admin():
                    # If the password has expired, log out and prepare to reset the password.
                    if user._password_has_expired():
                        user._revoke_all_devices()
                        user.sudo().action_expire_password()
                        cls._logout_and_reset_env()

                    # Check if the session has expired
                    elif user._session_has_expired():
                        user._revoke_all_devices()
                        cls._logout_and_reset_env()

                    # Old authentication process
                    elif not security.check_session(request.session, request.env):
                        cls._logout_and_reset_env()

            getattr(cls, f'_auth_method_{auth}')()
        except (AccessDenied, http.SessionExpiredException, werkzeug.exceptions.HTTPException):
            raise
        except Exception:
            _logger.info("Exception during request Authentication.", exc_info=True)
            raise AccessDenied()
