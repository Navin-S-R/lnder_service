from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def create_custom_fields():
    make_user_property_setter()

def make_user_property_setter():
    make_property_setter(
        doctype="User",
        fieldname="email",
        property="options",
        value="",
        property_type="Small Text",
        validate_fields_for_doctype=False,
    )
    make_property_setter(
        doctype="User",
        fieldname="send_welcome_email",
        property="default",
        value=0,
        property_type="Small Text",
        validate_fields_for_doctype=False,
    )
    make_property_setter(
        doctype="User",
        fieldname="send_welcome_email",
        property="hidden",
        value=1,
        property_type="Check",
        validate_fields_for_doctype=False,
    )