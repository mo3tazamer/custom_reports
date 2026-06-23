import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class ApAgingReport(BaseCustomReport):
    report_name = "ap-aging"
    title = "AP Aging"
    icon = "clock"

    def get_columns(self):
        return [{"fieldname":"supplier","label":"المورد","fieldtype":"Link","options":"Supplier","width":180},{"fieldname":"current","label":"حالي","fieldtype":"Currency","width":120},{"fieldname":"days_30","label":"30 يوم","fieldtype":"Currency","width":120},{"fieldname":"days_60","label":"60 يوم","fieldtype":"Currency","width":120},{"fieldname":"days_90","label":"90+ يوم","fieldtype":"Currency","width":120},{"fieldname":"total","label":"الإجمالي","fieldtype":"Currency","width":130}]

    def get_data(self, filters):
        conditions = []; values = []
        if filters.get("supplier"): conditions.append("supplier = %s"); values.append(filters["supplier"])
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = "SELECT supplier, SUM(CASE WHEN DATEDIFF(CURDATE(), due_date) <= 0 THEN outstanding_amount ELSE 0 END) as current, SUM(CASE WHEN DATEDIFF(CURDATE(), due_date) BETWEEN 1 AND 30 THEN outstanding_amount ELSE 0 END) as days_30, SUM(CASE WHEN DATEDIFF(CURDATE(), due_date) BETWEEN 31 AND 60 THEN outstanding_amount ELSE 0 END) as days_60, SUM(CASE WHEN DATEDIFF(CURDATE(), due_date) > 60 THEN outstanding_amount ELSE 0 END) as days_90, SUM(outstanding_amount) as total FROM `tabPurchase Invoice` WHERE docstatus = 1 AND outstanding_amount > 0 AND " + where_clause + " GROUP BY supplier ORDER BY total DESC LIMIT 1000"
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data: return []
        total = sum(float(row.get("total", 0) or 0) for row in data)
        return [{"label": "إجمالي المديونية", "value": "%.2f" % total, "indicator": "Red"}]

def execute(filters=None):
    return ApAgingReport().execute(filters)
