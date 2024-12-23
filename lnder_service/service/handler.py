import frappe, json
from frappe.utils import cint

class TenantAPIHandler:
    def __init__(self, tenant):
        self.tenant = tenant
        self.tenant_cache_key = f"api_details:{tenant}"
        self.credits_cache_key = f"credits:{tenant}"

    def handle_api_call(self, api_method, payload=None):
        # Request parameters
        self.api_method = api_method
        self.payload = payload
        
        # Validate API method
        valid_api_details = self.get_valid_apis()

        if api_method not in valid_api_details:
            return self.generate_response(403, "failed", "Tenant is not signed to use this service")

        # Get API cost and service name
        self.api_cost = valid_api_details[api_method]["cost"]
        self.service_name = valid_api_details[api_method]["service"]
        
        # Initialize tenant's credits
        self.initialize_credits()

        # Deduct credits and handle insufficient balance
        if not self.deduct_credits():
            return self.generate_response(402, "failed", "Insufficient credits")

        # Process API request
        response_payload = self.process_api_request()

        # sync credits to db
        if response_payload.get("status_code") != 500:
            frappe.enqueue(self.sync_credits_to_db, queue="short")

        return response_payload

    def get_valid_apis(self):
        # Fetch tenant APIs from cache or database
        cached_apis = frappe.cache().hget(self.tenant_cache_key, self.tenant)
        if not cached_apis:
            return self.fetch_and_cache_apis()
        return cached_apis

    def fetch_and_cache_apis(self):
        # Fetch APIs from the database
        tenant_api_list = frappe.get_all(
            "Tenant API",
            filters={"parent": self.tenant},
            fields=["api_method", "cost_per_call", "is_enabled", "service_name"]
        )
        valid_apis = {
            row["api_method"]: {"cost": row["cost_per_call"], "service": row["service_name"]}
            for row in tenant_api_list if row["is_enabled"]
        }
        frappe.cache().hset(self.tenant_cache_key, self.tenant, valid_apis)
        return valid_apis

    def initialize_credits(self):
        # Initialize credits if not already in cache
        cached_credits = frappe.cache.get(self.credits_cache_key)
        if cached_credits is None or not cached_credits.isdigit():
            db_credits = frappe.get_value("Tenant", {"name": self.tenant}, "available_credits") or 0
            frappe.cache.set(self.credits_cache_key, cint(db_credits))

    def deduct_credits(self):
        # Deduct credits and rollback if insufficient
        remaining_credits = frappe.cache.decrby(self.credits_cache_key, self.api_cost)
        if remaining_credits < 0:
            frappe.cache.incrby(self.credits_cache_key, self.api_cost)  # Rollback in case of negative balance
            return False
        return True

    def sync_credits_to_db(self):
        # Update credits in the database
        frappe.db.sql("""
            UPDATE `tabTenant`
            SET available_credits = available_credits - %s
            WHERE name = %s
        """, (self.api_cost, self.tenant))

    def process_api_request(self):
        try:
            connector = frappe.get_doc(self.service_name)
            connector.tenant = self.tenant
            connector.api_method = self.api_method
            if isinstance(self.payload, str):
                self.payload = json.loads(self.payload)
            connector.payload = self.payload
            response = connector.process_request()
            status = "success" if response.status_code == 200 else "failed"
            return self.generate_response(response.status_code, status, response.reason, response.json())

        except Exception as e:
            frappe.log_error("API Request Error", f"Failed to process API request: {str(e)}")
            return self.generate_response(500, "failed", "Internal server error")

    @staticmethod
    def generate_response(status_code, status, message, api_response=None):
        frappe.response.http_status_code = status_code
        return {
            "status_code": status_code,
            "status": status,
            "message": message,
            "api_response": api_response
        }


@frappe.whitelist()
def execute_api_handler(tenant, api_method, payload=None):
    handler = TenantAPIHandler(tenant)
    return handler.handle_api_call(api_method=api_method, payload=payload)
