import frappe, requests, json
from lnder_service.lnder_service.doctype.api_service_log.api_service_log import create_log
from frappe.model.document import Document

class RequestController(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flags = frappe._dict()

    def process_request(self):
        method_name = self.get_method(api_method=self.api_method)
        if method_name and hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                response = method(payload = self.payload)
                return response
            else:
                frappe.log_error(title="Invalid Method",message=f"Method '{method_name}' is not callable.")
                raise "Invalid Method"
        else:
            frappe.log_error(title="Invalid Method",message=f"Method '{method_name}' not found for API method '{self.api_method}'.")
            raise "Invalid Method"
    
    def make_request(self, endpoint, method, headers=None, data=None):
        try:

            headers = headers or {}
            data = data or {}
            
            if method.upper() == "GET":
                response = requests.get(endpoint, headers=headers, params=data)
            elif method.upper() in ("POST", "PUT", "PATCH", "DELETE"):
                response = requests.request(method.upper(), endpoint, headers=headers, data=data)
            else:
                raise f"Unsupported HTTP method: {method}"

            create_log(
                service=self.doctype,
                tenant=self.tenant,
                api_method=self.api_method,
                api_endpoint=endpoint,
                api_request_header=headers,
                api_request_data=data,
                api_response=response.text,
                api_response_status_code=response.status_code
            )

            return response

        except requests.exceptions.RequestException as e:
            frappe.log_error(title="Request Failed", message=str(e))
            raise f"Request Failed: {method}"