import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class VatReportReport(BaseCustomReport):
    report_name = "vat-report"
    title = "VAT Report"
    icon = "percent"

    def get_columns(self):
        return [{"fieldname":"month","label":"الشهر","fieldtype":"Data","width":120},{"fieldname":"total_sales","label":"إجمالي المبيعات","fieldtype":"Currency","width":150},{"fieldname":"total_purchases","label":"إجمالي المشتريات","fieldtype":"Currency","width":150},{"fieldname":"output_vat","label":"ضريبة المبيعات","fieldtype":"Currency","width":150},{"fieldname":"input_vat","label":"ضريبة المشتريات","fieldtype":"Currency","width":150},{"fieldname":"net_vat","label":"صافي الضريبة","fieldtype":"Currency","width":150}]

    def get_data(self, filters):
        conditions = []; values = []
        if filters.get("from_date"): conditions.append("posting_date >= %s"); values.append(filters["from_date"])
        if filters.get("to_date"): conditions.append("posting_date <= %s"); values.append(filters["to_date"])
        if filters.get("company"): conditions.append("company = %s"); values.append(filters["company"])
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sales_query = "SELECT DATE_FORMAT(posting_date, '%%Y-%%m') as month, SUM(grand_total) as total_sales, SUM(total_taxes_and_charges) as output_vat FROM `tabSales Invoice` WHERE docstatus = 1 AND " + where_clause + " GROUP BY DATE_FORMAT(posting_date, '%%Y-%%m')"
        purchase_query = "SELECT DATE_FORMAT(posting_date, '%%Y-%%m') as month, SUM(grand_total) as total_purchases, SUM(total_taxes_and_charges) as input_vat FROM `tabPurchase Invoice` WHERE docstatus = 1 AND " + where_clause + " GROUP BY DATE_FORMAT(posting_date, '%%Y-%%m')"
        sales_data = {r["month"]: r for r in self.safe_sql(sales_query, tuple(values), limit=24)}
        purchase_data = {r["month"]: r for r in self.safe_sql(purchase_query, tuple(values), limit=24)}
        all_months = sorted(set(list(sales_data.keys()) + list(purchase_data.keys())), reverse=True)
        result = []
        for month in all_months:
            s = sales_data.get(month, {})
            p = purchase_data.get(month, {})
            result.append({"month": month, "total_sales": s.get("total_sales", 0) or 0, "total_purchases": p.get("total_purchases", 0) or 0, "output_vat": s.get("output_vat", 0) or 0, "input_vat": p.get("input_vat", 0) or 0, "net_vat": (s.get("output_vat", 0) or 0) - (p.get("input_vat", 0) or 0)})
        return result

    def get_summary(self, data, filters):
        if not data: return []
        total_sales = sum(float(row.get("total_sales", 0) or 0) for row in data)
        total_purchases = sum(float(row.get("total_purchases", 0) or 0) for row in data)
        net_vat = sum(float(row.get("net_vat", 0) or 0) for row in data)
        return [{"label": "إجمالي المبيعات", "value": "%.2f" % total_sales, "indicator": "Green"}, {"label": "إجمالي المشتريات", "value": "%.2f" % total_purchases, "indicator": "Blue"}, {"label": "صافي الضريبة", "value": "%.2f" % net_vat, "indicator": "Orange"}]

def execute(filters=None):
    return VatReportReport().execute(filters)
