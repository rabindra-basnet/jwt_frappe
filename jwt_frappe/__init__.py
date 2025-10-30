# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from datetime import datetime, timedelta

__version__ = "1.0.2"

def get_expiry_in_seconds(session_expiry):
    hours, minutes = map(int, session_expiry.split(":"))
    return hours * 3600 + minutes * 60

def on_session_creation(login_manager):
    from .utils.auth import get_bearer_token

    if not (frappe.form_dict.use_jwt and cint(frappe.form_dict.use_jwt)):
        return

    settings = frappe.get_cached_doc("System Settings")
    expires_in = get_expiry_in_seconds(settings.session_expiry)

    # Generate JWT token data
    token_data = get_bearer_token(user=login_manager.user, expires_in=expires_in)

    # Set response data
    frappe.local.response.update({
        "token": token_data["access_token"],
        "token_type": token_data["token_type"],
        "expires_in": token_data["expires_in"],
        # "refresh_token": token_data["refresh_token"]
    })

    # Set refresh token cookie
    # expires = datetime.now() + timedelta(seconds=expires_in)
    # frappe.local.cookie_manager.set_cookie(
    #     key="refresh_token",
    #     value=token_data["refresh_token"],
    #     expires=expires,
    #     secure=True,
    #     httponly=True,
    #     samesite="None"
    # )

    frappe.flags.jwt_clear_cookies = True