import frappe
from frappe.core.doctype.user.user import User

class CustomUser(User):
    def validate_email_type(self, email):
        self.email = self.email.strip()