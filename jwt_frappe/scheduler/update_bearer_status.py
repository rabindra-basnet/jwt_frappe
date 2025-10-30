import frappe
from frappe.utils import now_datetime

def status_bearer_token():
    """Revoke expired OAuth Bearer Tokens by setting status to 'Revoked'"""
    current_timestamp = int(now_datetime().timestamp())

    # Fetch active tokens with creation and expiry info
    active_tokens = frappe.get_all(
        "OAuth Bearer Token",
        filters={"status": "Active"},
        fields=["name", "creation", "expires_in"]
    )

    for token in active_tokens:
        # Convert creation time to timestamp
        creation_ts = int(frappe.utils.get_datetime(token.creation).timestamp())
        expiry_ts = creation_ts + int(token.expires_in)  # expires_in is duration in seconds

        if expiry_ts < current_timestamp:
            frappe.db.set_value("OAuth Bearer Token", token.name, "status", "Revoked")

    frappe.db.commit()
