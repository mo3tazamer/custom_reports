import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class ExpenseReportReport(BaseCustomReport):
    report_name = "expense-report"
    title = "Expense Report"
    icon = "receipt"

    def get_columns(self):
        return [{"fieldname":"posting_date","label":"التاريخ","fieldtype":"Date","width":120},{"fieldname":"account","label":"الحساب","fieldtype":"Link","options":"Account","width":180},{"fieldname":"debit","label":"المبلغ","fieldtype":"Currency","width":130},{"fieldname":"voucher_type","label":"نوع القيد","fieldtype":"Data","width":130},{"fieldname":"voucher_no","label":"رقم القيد","fieldtype":"Dynamic Link","options":"voucher_type","width":140},{"fieldname":"cost_center","label":"مركز التكلفة","fieldtype":"Link","options":"Cost Center","width":150},{"fieldname":"remarks","label":"البيان","fieldtype":"Data","width":250}]

    def get_data(self, filters):
        conditions = []; values = []
        if filters.get("account"): conditions.append("account = %s"); values.append(filters["account"])
        if filters.get("cost_center"): conditions.append("cost_center = %s"); values.append(filters["cost_center"])
        if filters.get("from_date"): conditions.append("posting_date >= %s"); values.append(filters["from_date"])
        if filters.get("to_date"): conditions.append("posting_date <= %s"); values.append(filters["to_date"])
        if filters.get("company"): conditions.append("company = %s"); values.append(filters["company"])
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = "SELECT posting_date, account, debit, voucher_type, voucher_no, cost_center, remarks FROM `tabGL Entry` WHERE debit > 0 AND account LIKE '%%Expense%%' AND " + where_clause + " ORDER BY posting_date DESC LIMIT 1000"
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data: return []
        total = sum(float(row.get("debit", 0) or 0) for row in data)
        count = len(data)
        avg = total / count if count > 0 else 0
        return [{"label": "إجمالي المصروفات", "value": "%.2f" % total, "indicator": "Red"}, {"label": "عدد القيود", "value": str(count), "indicator": "Blue"}, {"label": "متوسط المصروف", "value": "%.2f" % avg, "indicator": "Orange"}]

def execute(filters=None):
    return ExpenseReportReport().execute(filters)
