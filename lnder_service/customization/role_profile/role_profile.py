import frappe

def create_api_service_user_role():
    if not frappe.db.exists("Role", "API Service User"):
        frappe.get_doc({
                "doctype" : "Role",
                "role_name" : "API Service User",
                "desk_access": 1
            }).insert(ignore_permissions=True)

def create_api_service_user_role_profile():
    if not frappe.db.exists("Role Profile", "API Service User"):
        frappe.get_doc({
                "doctype" : "Role Profile",
                "role_profile" : "API Service User",
                "roles" : [
                    {
                        "role": "API Service User"
                    }
                ]
            }).insert(ignore_permissions=True)