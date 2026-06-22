import frappe
import json
from datetime import datetime

class BaseCustomReport:
    """Base class for all custom reports with safety and performance."""

    report_name = ""
    title = ""
    icon = "file-text"

    def execute(self, filters=None):
        """Main entry point - returns columns and data."""
        try:
            columns = self.get_columns()
            data = self.get_data(filters or {})
            summary = self.get_summary(data, filters)

            # Cache the result
            self._cache_result(filters, columns, data, summary)

            return columns, data, None, None, summary
        except Exception as e:
            frappe.log_error(f"{self.report_name} Error: {str(e)}", "Custom Report Error")
            frappe.msgprint(f"Error loading report: {str(e)}", indicator="red", alert=True)
            return [], []

    def get_columns(self):
        """Override in child class."""
        raise NotImplementedError

    def get_data(self, filters):
        """Override in child class."""
        raise NotImplementedError

    def get_summary(self, data, filters):
        """Auto-calculate summary cards from data."""
        return []

    def build_conditions(self, filters, allowed_fields):
        """Build safe WHERE conditions from filters."""
        conditions = []
        values = []

        for field, value in filters.items():
            if value and field in allowed_fields:
                if isinstance(value, list):
                    # Date range or list
                    if len(value) == 2 and all(isinstance(v, str) for v in value):
                        conditions.append(f"{field} BETWEEN %s AND %s")
                        values.extend(value)
                else:
                    conditions.append(f"{field} = %s")
                    values.append(value)

        return " AND ".join(conditions) if conditions else "1=1", values

    def calculate_running_balance(self, data, debit_col="debit", credit_col="credit"):
        """Calculate running balance in Python (safer than MySQL variables)."""
        balance = 0
        for row in data:
            debit = float(row.get(debit_col, 0) or 0)
            credit = float(row.get(credit_col, 0) or 0)
            balance += debit - credit
            row["balance"] = balance
        return data

    def _cache_result(self, filters, columns, data, summary):
        """Cache report result for 5 minutes."""
        try:
            cache_key = f"custom_report:{self.report_name}:{json.dumps(filters, default=str)}"
            frappe.cache().set_value(cache_key, {
                "columns": columns,
                "data": data,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }, expires_in_sec=300)
        except Exception:
            pass

    @staticmethod
    def safe_sql(query, values=None, as_dict=True, limit=1000):
        """Execute SQL with safety limits."""
        if limit and "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"
        return frappe.db.sql(query, values or (), as_dict=as_dict)
