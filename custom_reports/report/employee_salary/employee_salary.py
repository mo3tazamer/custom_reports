import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class EmployeeSalaryReport(BaseCustomReport):
    report_name = "employee_salary"
    title = "Employee Salary"
    icon = "users"

    def get_columns(self):
        return [
            {"fieldname": "employee", "label": "الموظف", "fieldtype": "Link", "options": "Employee", "width": 150},
            {"fieldname": "employee_name", "label": "اسم الموظف", "fieldtype": "Data", "width": 180},
            {"fieldname": "posting_date", "label": "التاريخ", "fieldtype": "Date", "width": 120},
            {"fieldname": "gross_pay", "label": "الراتب الأساسي", "fieldtype": "Currency", "width": 140},
            {"fieldname": "total_deduction", "label": "الاستقطاعات", "fieldtype": "Currency", "width": 130},
            {"fieldname": "net_pay", "label": "صافي المرتب", "fieldtype": "Currency", "width": 130},
            {"fieldname": "department", "label": "القسم", "fieldtype": "Link", "options": "Department", "width": 150},
            {"fieldname": "designation", "label": "الوظيفة", "fieldtype": "Link", "options": "Designation", "width": 150},
        ]

    def get_data(self, filters):
        conditions = []
        values = []
        if filters.get("employee"):
            conditions.append("employee = %s")
            values.append(filters["employee"])
        if filters.get("department"):
            conditions.append("department = %s")
            values.append(filters["department"])
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
            "gross_pay, total_deduction, net_pay, department, designation "
            "FROM `tabSalary Slip` "
            "WHERE docstatus = 1 AND " + where_clause + " "
            "ORDER BY posting_date DESC LIMIT 1000"
        )
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data:
            return []
        total = sum(float(row.get("net_pay", 0) or 0) for row in data)
        count = len(set(row.get("employee") for row in data))
        avg = total / count if count > 0 else 0
        return [
            {"label": "إجمالي المرتبات", "value": "%.2f" % total, "indicator": "Green"},
            {"label": "عدد الموظفين", "value": str(count), "indicator": "Blue"},
            {"label": "متوسط المرتب", "value": "%.2f" % avg, "indicator": "Orange"},
        ]

def execute(filters=None):
    return EmployeeSalaryReport().execute(filters)
