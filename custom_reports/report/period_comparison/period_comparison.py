import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class PeriodComparisonReport(BaseCustomReport):
    report_name = "period_comparison"
    title = "Period Comparison"
    icon = "git-compare"

    def get_columns(self):
        return [
            {"fieldname": "metric", "label": "البيان", "fieldtype": "Data", "width": 200},
            {"fieldname": "period1", "label": "الفترة 1", "fieldtype": "Currency", "width": 150},
            {"fieldname": "period2", "label": "الفترة 2", "fieldtype": "Currency", "width": 150},
            {"fieldname": "variance", "label": "الفرق", "fieldtype": "Currency", "width": 130},
            {"fieldname": "variance_pct", "label": "نسبة الفرق", "fieldtype": "Percent", "width": 120},
        ]

    def get_data(self, filters):
        p1_from = filters.get("period1_from")
        p1_to = filters.get("period1_to")
        p2_from = filters.get("period2_from")
        p2_to = filters.get("period2_to")
        company = filters.get("company")

        if not all([p1_from, p1_to, p2_from, p2_to]):
            return []

        p1_sales = frappe.db.sql(
            "SELECT COALESCE(SUM(grand_total), 0) as total FROM `tabSales Invoice` "
            "WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s AND company = %s",
            (p1_from, p1_to, company), as_dict=True)[0].total

        p2_sales = frappe.db.sql(
            "SELECT COALESCE(SUM(grand_total), 0) as total FROM `tabSales Invoice` "
            "WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s AND company = %s",
            (p2_from, p2_to, company), as_dict=True)[0].total

        p1_purchases = frappe.db.sql(
            "SELECT COALESCE(SUM(grand_total), 0) as total FROM `tabPurchase Invoice` "
            "WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s AND company = %s",
            (p1_from, p1_to, company), as_dict=True)[0].total

        p2_purchases = frappe.db.sql(
            "SELECT COALESCE(SUM(grand_total), 0) as total FROM `tabPurchase Invoice` "
            "WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s AND company = %s",
            (p2_from, p2_to, company), as_dict=True)[0].total

        data = [
            self.make_row("المبيعات", p1_sales, p2_sales),
            self.make_row("المشتريات", p1_purchases, p2_purchases),
        ]
        return data

    def make_row(self, metric, p1, p2):
        variance = p2 - p1
        variance_pct = (variance / p1 * 100) if p1 else 0
        return {
            "metric": metric,
            "period1": p1,
            "period2": p2,
            "variance": variance,
            "variance_pct": variance_pct
        }

    def get_summary(self, data, filters):
        if not data:
            return []
        sales_row = next((r for r in data if r["metric"] == "المبيعات"), {})
        return [
            {"label": "مبيعات الفترة 1", "value": "%.2f" % (sales_row.get("period1", 0) or 0), "indicator": "Blue"},
            {"label": "مبيعات الفترة 2", "value": "%.2f" % (sales_row.get("period2", 0) or 0), "indicator": "Green"},
        ]

def execute(filters=None):
    return PeriodComparisonReport().execute(filters)
