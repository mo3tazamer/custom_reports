import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class CustomerStatementReport(BaseCustomReport):
    report_name = "customer-statement"
    title = "Customer Statement"
    icon = "user"

    def get_columns(self):
        return [{"fieldname":"posting_date","label":"التاريخ","fieldtype":"Date","width":120},{"fieldname":"voucher_type","label":"نوع القيد","fieldtype":"Data","width":130},{"fieldname":"voucher_no","label":"رقم القيد","fieldtype":"Dynamic Link","options":"voucher_type","width":140},{"fieldname":"debit","label":"مدين","fieldtype":"Currency","width":120},{"fieldname":"credit","label":"دائن","fieldtype":"Currency","width":120},{"fieldname":"balance","label":"الرصيد","fieldtype":"Currency","width":130},{"fieldname":"remarks","label":"البيان","fieldtype":"Data","width":250}]

    def get_data(self, filters):
        conditions = []; values = []
        if filters.get("customer"): conditions.append("party = %s"); values.append(filters["customer"])
        if filters.get("from_date"): conditions.append("posting_date >= %s"); values.append(filters["from_date"])
        if filters.get("to_date"): conditions.append("posting_date <= %s"); values.append(filters["to_date"])
        if filters.get("company"): conditions.append("company = %s"); values.append(filters["company"])
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = "SELECT posting_date, voucher_type, voucher_no, debit, credit, 0 as balance, remarks FROM `tabGL Entry` WHERE party_type = 'Customer' AND " + where_clause + " ORDER BY posting_date, creation LIMIT 1000"
        data = self.safe_sql(query, tuple(values), limit=1000)
        return self.calculate_running_balance(data, "debit", "credit")

    def get_summary(self, data, filters):
        if not data: return []
        total_debit = sum(float(row.get("debit", 0) or 0) for row in data)
        total_credit = sum(float(row.get("credit", 0) or 0) for row in data)
        closing = float(data[-1].get("balance", 0)) if data else 0
        return [{"label": "إجمالي المدين", "value": "%.2f" % total_debit, "indicator": "Red"}, {"label": "إجمالي الدائن", "value": "%.2f" % total_credit, "indicator": "Green"}, {"label": "الرصيد الختامي", "value": "%.2f" % closing, "indicator": "Blue"}]

def execute(filters=None):
    return CustomerStatementReport().execute(filters)
