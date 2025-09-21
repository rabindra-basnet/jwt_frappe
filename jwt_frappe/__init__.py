# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import cint

__version__ = "1.0.2"

def get_expiry_in_seconds(session_expiry):
    hours, minutes = map(int, session_expiry.split(":"))
    return hours * 3600 + minutes * 60

def on_session_creation(login_manager):
    from .utils.auth import get_bearer_token

    use_jwt = frappe.form_dict.use_jwt
    if frappe.form_dict.use_jwt and cint(frappe.form_dict.use_jwt):
      settings = frappe.get_cached_doc("System Settings")
      expires_in = get_expiry_in_seconds(settings.session_expiry)

      frappe.local.response["token"] = get_bearer_token(
            user=login_manager.user, expires_in=expires_in
        )["access_token"]
      frappe.local.response["token_type"] = get_bearer_token(
            user=login_manager.user, expires_in=expires_in
        )["token_type"]
      frappe.local.response["expires_in"] = get_bearer_token(
            user=login_manager.user, expires_in=expires_in
        )["expires_in"]

      frappe.flags.jwt_clear_cookies = True
