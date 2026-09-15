"""Fake HR data for the STRETCH access desk. No real employees or systems."""

EMPLOYEES = {
    "alice": {"employee_id": "alice", "name": "Alice Kim", "department": "Sales", "manager": "bob", "role": "sales_rep"},
    "bob": {"employee_id": "bob", "name": "Bob Diaz", "department": "Sales", "manager": "carol", "role": "sales_manager"},
    "carol": {"employee_id": "carol", "name": "Carol Nguyen", "department": "Finance", "manager": "dave", "role": "finance_analyst"},
}

# What each role may self-serve. This is verification data the entitlement
# reader looks up; the writer still checks entitlement_policy.json as the
# final authority on what's privileged.
ROLE_ENTITLEMENTS = {
    "sales_rep": ["password_reset", "account_unlock", "vpn_access"],
    "sales_manager": ["password_reset", "account_unlock", "vpn_access", "software_install_standard"],
    "finance_analyst": ["password_reset", "account_unlock", "vpn_access"],
}
