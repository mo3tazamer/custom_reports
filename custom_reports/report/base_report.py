import frappe
import json

class BaseCustomReport:
    report_name = ""
    title = ""
    icon = "file-text"

    def execute(self, filters=None):
        try:
            columns = self.get_columns()
            data = self.get_data(filters or {})
            summary = self.get_summary(data, filters)
            return columns, data, None, None, summary
        except Exception as e:
            frappe.log_error(f"{self.report_name} Error: {str(e)}")
            frappe.msgprint(f"Error: {str(e)}", indicator="red", alert=True)
            return [], []

    def get_columns(self):
        raise NotImplementedError

    def get_data(self, filters):
        raise NotImplementedError

    def get_summary(self, data, filters):
        return []

    def calculate_running_balance(self, data, debit_col="debit", credit_col="credit"):
        balance = 0
        for row in data:
            debit = float(row.get(debit_col, 0) or 0)
            credit = float(row.get(credit_col, 0) or 0)
            balance += debit - credit
            row["balance"] = balance
        return data

    def safe_sql(self, query, values=None, as_dict=True, limit=1000):
        if limit and "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"
        return frappe.db.sql(query, values or (), as_dict=as_dict)
