import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class SalesPerformanceReport(BaseCustomReport):
    report_name = "sales-performance"
    title = "Sales Performance"
    icon = "chart-line"

    def get_columns(self):
        return [{"fieldname":"posting_date","label":"التاريخ","fieldtype":"Date","width":120},{"fieldname":"customer","label":"اسم العميل","fieldtype":"Link","options":"Customer","width":180},{"fieldname":"name","label":"رقم الفاتورة","fieldtype":"Link","options":"Sales Invoice","width":140},{"fieldname":"grand_total","label":"إجمالي الفاتورة","fieldtype":"Currency","width":150},{"fieldname":"total_qty","label":"عدد المنتجات","fieldtype":"Float","width":120},{"fieldname":"sales_person","label":"مندوب المبيعات","fieldtype":"Link","options":"Sales Person","width":150},{"fieldname":"cost_center","label":"مركز التكلفة","fieldtype":"Link","options":"Cost Center","width":150},{"fieldname":"territory","label":"المنطقة","fieldtype":"Link","options":"Territory","width":120}]

    def get_data(self, filters):
        conditions = []; values = []
        if filters.get("customer"): conditions.append("si.customer = %s"); values.append(filters["customer"])
        if filters.get("sales_person"): conditions.append("si.sales_person = %s"); values.append(filters["sales_person"])
        if filters.get("cost_center"): conditions.append("si.cost_center = %s"); values.append(filters["cost_center"])
        if filters.get("brand"): conditions.append("sii.brand = %s"); values.append(filters["brand"])
        if filters.get("item"): conditions.append("sii.item_code = %s"); values.append(filters["item"])
        if filters.get("from_date"): conditions.append("si.posting_date >= %s"); values.append(filters["from_date"])
        if filters.get("to_date"): conditions.append("si.posting_date <= %s"); values.append(filters["to_date"])
        if filters.get("company"): conditions.append("si.company = %s"); values.append(filters["company"])
        if filters.get("territory"): conditions.append("si.territory = %s"); values.append(filters["territory"])
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        if filters.get("brand"):
            query = "SELECT si.posting_date, si.customer, si.name, SUM(sii.amount) as grand_total, SUM(sii.qty) as total_qty, si.sales_person, si.cost_center, si.territory FROM `tabSales Invoice` si INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name WHERE si.docstatus = 1 AND " + where_clause + " GROUP BY si.name HAVING SUM(sii.qty) > 0 ORDER BY si.posting_date DESC LIMIT 1000"
        else:
            query = "SELECT si.posting_date, si.customer, si.name, si.grand_total, (SELECT COUNT(*) FROM `tabSales Invoice Item` sii2 WHERE sii2.parent = si.name) as total_qty, si.sales_person, si.cost_center, si.territory FROM `tabSales Invoice` si WHERE si.docstatus = 1 AND " + where_clause + " ORDER BY si.posting_date DESC LIMIT 1000"
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data: return []
        total_sales = sum(float(row.get("grand_total", 0) or 0) for row in data)
        invoice_count = len(data)
        avg_invoice = total_sales / invoice_count if invoice_count > 0 else 0
        return [{"label": "إجمالي المبيعات", "value": "%.2f" % total_sales, "indicator": "Green"}, {"label": "عدد الفواتير", "value": str(invoice_count), "indicator": "Blue"}, {"label": "متوسط الفاتورة", "value": "%.2f" % avg_invoice, "indicator": "Orange"}]

def execute(filters=None):
    return SalesPerformanceReport().execute(filters)
