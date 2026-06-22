import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class BrandSalesDetailReport(BaseCustomReport):
    report_name = "brand-sales-detail"
    title = "Brand Sales Detail"
    icon = "tag"

    def get_columns(self):
        return [{"fieldname":"posting_date","label":"التاريخ","fieldtype":"Date","width":120},{"fieldname":"name","label":"رقم الفاتورة","fieldtype":"Link","options":"Sales Invoice","width":140},{"fieldname":"customer","label":"اسم العميل","fieldtype":"Link","options":"Customer","width":180},{"fieldname":"item_code","label":"الصنف","fieldtype":"Link","options":"Item","width":150},{"fieldname":"item_name","label":"إسم الصنف","fieldtype":"Data","width":200},{"fieldname":"brand","label":"العلامة التجارية","fieldtype":"Link","options":"Brand","width":150},{"fieldname":"qty","label":"الكمية","fieldtype":"Float","width":100},{"fieldname":"rate","label":"سعر البيع","fieldtype":"Currency","width":120},{"fieldname":"amount","label":"المبلغ","fieldtype":"Currency","width":130}]

    def get_data(self, filters):
        conditions = []; values = []
        if filters.get("brand"): conditions.append("sii.brand = %s"); values.append(filters["brand"])
        if filters.get("sales_person"): conditions.append("si.sales_person = %s"); values.append(filters["sales_person"])
        if filters.get("cost_center"): conditions.append("si.cost_center = %s"); values.append(filters["cost_center"])
        if filters.get("customer"): conditions.append("si.customer = %s"); values.append(filters["customer"])
        if filters.get("item"): conditions.append("sii.item_code = %s"); values.append(filters["item"])
        if filters.get("from_date"): conditions.append("si.posting_date >= %s"); values.append(filters["from_date"])
        if filters.get("to_date"): conditions.append("si.posting_date <= %s"); values.append(filters["to_date"])
        if filters.get("company"): conditions.append("si.company = %s"); values.append(filters["company"])
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = "SELECT si.posting_date, si.name, si.customer, sii.item_code, sii.item_name, sii.brand, sii.qty, sii.rate, sii.amount FROM `tabSales Invoice` si INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name WHERE si.docstatus = 1 AND " + where_clause + " ORDER BY si.posting_date DESC LIMIT 1000"
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data: return []
        total = sum(float(row.get("amount", 0) or 0) for row in data)
        total_qty = sum(float(row.get("qty", 0) or 0) for row in data)
        invoice_count = len(set(row.get("name") for row in data))
        return [{"label": "إجمالي المبيعات", "value": "%.2f" % total, "indicator": "Green"}, {"label": "عدد المنتجات", "value": "%.0f" % total_qty, "indicator": "Blue"}, {"label": "عدد الفواتير", "value": str(invoice_count), "indicator": "Orange"}]

def execute(filters=None):
    return BrandSalesDetailReport().execute(filters)
