from lnder_service.customization.role_profile import role_profile
from lnder_service.customization.user import custom_field as user_cf

def after_migrate():
    #Role
    role_profile.create_api_service_user_role()
    role_profile.create_api_service_user_role_profile()
    
    #User
    user_cf.create_custom_fields()