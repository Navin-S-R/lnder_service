# Copyright (c) 2024, hello@aerele.in and contributors
# For license information, please see license.txt

import frappe, json
from lnder_service.service.request_controller import RequestController



class SignzyConnector(RequestController):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if hasattr(self, "doctype") and self.doctype == "Signzy Connector":
			self.get_api_endpoints()
			self.get_headers()

	def get_method(self, api_method):
		return {
			"Verify Aadhaar OCR" : "verify_aadhaar_ocr",
			"Verify Aadhaar" : "verify_aadhaar"
		}.get(api_method, None)

	def get_api_endpoints(self):
		self.api_endpoints = {url.api_method:self.url+url.url_endpoint for url in self.api_endpoint_detail}


	def get_headers(self):
		self.headers = {
			'Authorization': self.get_password("authorization"),
			'Content-Type': 'application/json'
		}
	
	def verify_aadhaar(self, payload):
		def validate_aadhaar_input(pattern: str, value: str) -> bool:
			import re
			return bool(re.match(pattern, value))

		endpoint = self.api_endpoints.get(self.api_method)
		aadhaar_no = payload.get('aadhaar_number')
		api_payload = json.dumps({"uid": aadhaar_no})
		if not endpoint:
			frappe.log_error(title="EndPoint Not Found",message=f"Endpoint for '{self.api_method}' is not available.")
			raise "EndPoint Not Found"

		if not aadhaar_no:
			raise "Aadhaar number is required"

		# Validate the Aadhaar number format
		if not validate_aadhaar_input(pattern=r"^\d{12}$", value=aadhaar_no):
			raise "Aadhaar Number is not in valid format"

		return self.make_request(endpoint=endpoint, method="POST", headers=self.headers, data=api_payload)
