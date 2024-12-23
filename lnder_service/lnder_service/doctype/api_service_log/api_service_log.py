# Copyright (c) 2024, hello@aerele.in and contributors
# For license information, please see license.txt

import frappe, json
from frappe.model.document import Document


class APIServiceLog(Document):
    pass

def create_log(
    service,
    tenant,
    api_method,
    api_endpoint,
    api_request_header=None,
    api_request_data=None,
    api_response=None,
    api_response_status_code=None,
):
    log_doc = frappe.new_doc("API Service Log")
    log_doc.service = service
    log_doc.tenant = tenant
    log_doc.api_method = api_method
    log_doc.url = api_endpoint

    if api_request_header:
        if isinstance(api_request_header, str):
            try:
                api_request_header = json.loads(api_request_header)
            except json.JSONDecodeError:
                log_doc.header = api_request_header
        if isinstance(api_request_header, dict):
            log_doc.header = json.dumps(api_request_header, indent=4)

    if api_request_data:
        if isinstance(api_request_data, str):
            try:
                api_request_data = json.loads(api_request_data)
            except json.JSONDecodeError:
                log_doc.payload = api_request_data
        if isinstance(api_request_data, dict):
            log_doc.payload = json.dumps(api_request_data, indent=4)

    if api_response:
        try:
            log_doc.response = json.loads(api_response)
        except json.JSONDecodeError:
            log_doc.response = api_response
        log_doc.response = json.dumps(log_doc.response, indent=4)

    log_doc.status_code = api_response_status_code
    log_doc.insert(ignore_permissions=True)