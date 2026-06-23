import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class PurchaseAnalysisReport(BaseCustomReport):
    report_name = "purchase-analysis"
    title = "Purchase Analysis"
    icon = "shopping-cart"

    def get_columns(self):
        return [{"fieldname":"posting_date","label":"التاريخ","fieldtype":"Date","width":120},{"fieldname":"supplier","label":"المورد","fieldtype":"Link","options":"Supplier","width":180},{"fieldname":"name","label":"رقم الفاتورة","fieldtype":"Link","options":"Purchase Invoice","width":140},{"fieldname":"grand_total","label":"إجمالي الفاتورة","fieldtype":"Currency","width":150},{"fieldname":"total_taxes_and_charges","label":"الضريبة","fieldtype":"Currency","width":120},{"fieldname":"total_qty","label":"عدد المنتجات","fieldtype":"Float","width":120},{"fieldname":"cost_center","label":"مركز التكلفة","fieldtype":"Link","options":"Cost Center","width":150}]

    def get_data(self, filters):
        conditions = []; values = []
        if filters.get("supplier"): conditions.append("supplier = %s"); values.append(filters["supplier"])
        if filters.get("cost_center"): conditions.append("cost_center = %s"); values.append(filters["cost_center"])
        if filters.get("from_date"): conditions.append("posting_date >= %s"); values.append(filters["from_date"])
        if filters.get("to_date"): conditions.append("posting_date <= %s"); values.append(filters["to_date"])
        if filters.get("company"): conditions.append("company = %s"); values.append(filters["company"])
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = "SELECT posting_date, supplier, name, grand_total, total_taxes_and_charges, (SELECT COUNT(*) FROM `tabPurchase Invoice Item` pii WHERE pii.parent = pi.name) as total_qty, cost_center FROM `tabPurchase Invoice` pi WHERE docstatus = 1 AND " + where_clause + " ORDER BY posting_date DESC LIMIT 1000"
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data: return []
        total = sum(float(row.get("grand_total", 0) or 0) for row in data)
        count = len(data)
        tax = sum(float(row.get("total_taxes_and_charges", 0) or 0) for row in data)
        avg = total / count if count > 0 else 0
        return [{"label": "إجمالي المشتريات", "value": "%.2f" % total, "indicator": "Blue"}, {"label": "عدد الفواتير", "value": str(count), "indicator": "Green"}, {"label": "إجمالي الضريبة", "value": "%.2f" % tax, "indicator": "Orange"}, {"label": "متوسط الفاتورة", "value": "%.2f" % avg, "indicator": "Purple"}]

def execute(filters=None):
    return PurchaseAnalysisReport().execute(filters)
