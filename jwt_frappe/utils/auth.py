import random

import frappe
import jwt
from frappe import _
from frappe.auth import LoginManager
from frappe.utils import cint, get_url, get_datetime
from frappe.utils.password import check_password, passlibctx, update_password


def get_linked_user(id_type, id):
    """
    Returns the user associated with the details
    :param id_type: either 'mobile' or 'email'
    :param id: the email/mobile
    """
    if id_type not in ("mobile", "sms", "email"):
        frappe.throw(f"Invalid id_type: {id_type}")

    if id_type in ("mobile", "sms"):
        id_type = "mobile_no"

    return frappe.db.get_value("User", {id_type: id})


def get_oath_client():
    client = frappe.db.get_value("OAuth Client", {})
    if not client:
        # Make one auto
        client = frappe.get_doc(
            frappe._dict(
                doctype="OAuth Client",
                app_name="default",
                scopes="all openid",
                redirect_urls=get_url(),
                default_redirect_uri=get_url(),
                grant_type="Implicit",
                response_type="Token",
            )
        )
        client.insert(ignore_permissions=True)
    else:
        client = frappe.get_doc("OAuth Client", client)

    return client


def get_bearer_token(user, expires_in=3600):
    import hashlib
    import jwt
    from frappe.oauth import calculate_at_hash
    from oauthlib.oauth2.rfc6749.tokens import random_token_generator

    client = get_oath_client()
    token = frappe._dict(
        {
            "access_token": random_token_generator(None),
            "expires_in": expires_in,
            "token_type": "Bearer",
            "scopes": client.scopes,
            "refresh_token": random_token_generator(None),
        }
    )
    bearer_token = frappe.new_doc("OAuth Bearer Token")
    bearer_token.client = client.name
    bearer_token.scopes = token["scopes"]
    bearer_token.access_token = token["access_token"]
    bearer_token.refresh_token = token.get("refresh_token")
    bearer_token.expires_in = token["expires_in"] or 3600
    bearer_token.user = user
    bearer_token.save(ignore_permissions=True)
    frappe.db.commit()

    # ID Token
    id_token_header = {"typ": "jwt", "alg": "HS256"}
    id_token = {
        "aud": "token_client",
        "exp": int(
            (
                frappe.db.get_value(
                    "OAuth Bearer Token", token.access_token, "expiration_time"
                )
                - frappe.utils.datetime.datetime(1970, 1, 1)
            ).total_seconds()
        ),
        "sub": frappe.db.get_value(
            "User Social Login",
            {"parent": bearer_token.user, "provider": "frappe"},
            "userid",
        ),
        "iss": "frappe_server_url",
        "at_hash": calculate_at_hash(token.access_token, hashlib.sha256),
    }
    id_token_encoded = jwt.encode(
        id_token, "client_secret", algorithm="HS256", headers=id_token_header
    )
    id_token_encoded = frappe.safe_decode(id_token_encoded)
    token.id_token = id_token_encoded
    frappe.flags.jwt = id_token_encoded
    return token

