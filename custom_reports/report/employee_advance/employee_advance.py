import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class EmployeeAdvanceReport(BaseCustomReport):
    report_name = "employee_advance"
    title = "Employee Advance"
    icon = "wallet"

    def get_columns(self):
        return [
            {"fieldname": "employee", "label": "الموظف", "fieldtype": "Link", "options": "Employee", "width": 150},
            {"fieldname": "employee_name", "label": "اسم الموظف", "fieldtype": "Data", "width": 180},
            {"fieldname": "posting_date", "label": "التاريخ", "fieldtype": "Date", "width": 120},
            {"fieldname": "advance_amount", "label": "مبلغ السلفة", "fieldtype": "Currency", "width": 140},
            {"fieldname": "paid_amount", "label": "المبلغ المدفوع", "fieldtype": "Currency", "width": 150},
            {"fieldname": "claimed_amount", "label": "المبلغ المسترد", "fieldtype": "Currency", "width": 150},
            {"fieldname": "remaining", "label": "المتبقي", "fieldtype": "Currency", "width": 130},
            {"fieldname": "status", "label": "الحالة", "fieldtype": "Data", "width": 120},
        ]

    def get_data(self, filters):
        conditions = []
        values = []
        if filters.get("employee"):
            conditions.append("employee = %s")
            values.append(filters["employee"])
        if filters.get("from_date"):
            conditions.append("posting_date >= %s")
            values.append(filters["from_date"])
        if filters.get("to_date"):
            conditions.append("posting_date <= %s")
            values.append(filters["to_date"])
        if filters.get("company"):
            conditions.append("company = %s")
            values.append(filters["company"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = (
            "SELECT employee, employee_name, posting_date, "
            "advance_amount, paid_amount, claimed_amount, "
            "advance_amount - claimed_amount as remaining, status "
            "FROM `tabEmployee Advance` "
            "WHERE docstatus = 1 AND " + where_clause + " "
            "ORDER BY posting_date DESC LIMIT 1000"
        )
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data:
            return []
        total = sum(float(row.get("advance_amount", 0) or 0) for row in data)
        returned = sum(float(row.get("claimed_amount", 0) or 0) for row in data)
        remaining = sum(float(row.get("remaining", 0) or 0) for row in data)
        return [
            {"label": "إجمالي السلف", "value": "%.2f" % total, "indicator": "Blue"},
            {"label": "المسترد", "value": "%.2f" % returned, "indicator": "Green"},
            {"label": "المتبقي", "value": "%.2f" % remaining, "indicator": "Red"},
        ]

def execute(filters=None):
    return EmployeeAdvanceReport().execute(filters)
