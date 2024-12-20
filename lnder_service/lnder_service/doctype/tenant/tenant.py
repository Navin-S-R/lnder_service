# Copyright (c) 2024, hello@aerele.in and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

API_SERVICE = ["Signzy Connector"]

class Tenant(Document):
	@frappe.whitelist()
	def get_api(self):
		existing_api_list = [row.api_method for row in self.tenant_api]

		api_list = []
		for service in API_SERVICE:
			if api_service := frappe.get_all("API Endpoint Detail",{
				"parent" : service,
				"api_method" : ["not in",existing_api_list]
				},["api_method","cost_per_call"]):
				api_list.extend(api_service)

		if api_list:
			self.extend("tenant_api",api_list)