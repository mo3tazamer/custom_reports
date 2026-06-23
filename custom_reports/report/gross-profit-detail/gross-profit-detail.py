import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class GrossProfitDetailReport(BaseCustomReport):
    report_name = "gross-profit-detail"
    title = "Gross Profit Detail"
    icon = "pie-chart"

    def get_columns(self):
        return [{"fieldname":"posting_date","label":"التاريخ","fieldtype":"Date","width":120},{"fieldname":"name","label":"رقم الفاتورة","fieldtype":"Link","options":"Sales Invoice","width":140},{"fieldname":"customer","label":"العميل","fieldtype":"Link","options":"Customer","width":180},{"fieldname":"item_code","label":"الصنف","fieldtype":"Link","options":"Item","width":150},{"fieldname":"item_name","label":"إسم الصنف","fieldtype":"Data","width":200},{"fieldname":"qty","label":"الكمية","fieldtype":"Float","width":100},{"fieldname":"buying_rate","label":"سعر الشراء","fieldtype":"Currency","width":120},{"fieldname":"selling_rate","label":"سعر البيع","fieldtype":"Currency","width":120},{"fieldname":"profit_per_unit","label":"الربح للقطعة","fieldtype":"Currency","width":130},{"fieldname":"total_profit","label":"إجمالي الربح","fieldtype":"Currency","width":130}]

    def get_data(self, filters):
        conditions = []; values = []
        if filters.get("item"): conditions.append("sii.item_code = %s"); values.append(filters["item"])
        if filters.get("customer"): conditions.append("si.customer = %s"); values.append(filters["customer"])
        if filters.get("from_date"): conditions.append("si.posting_date >= %s"); values.append(filters["from_date"])
        if filters.get("to_date"): conditions.append("si.posting_date <= %s"); values.append(filters["to_date"])
        if filters.get("company"): conditions.append("si.company = %s"); values.append(filters["company"])
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = "SELECT si.posting_date, si.name, si.customer, sii.item_code, sii.item_name, sii.qty, sii.rate as selling_rate, COALESCE((SELECT AVG(valuation_rate) FROM `tabStock Ledger Entry` sle WHERE sle.item_code = sii.item_code AND sle.warehouse = sii.warehouse AND sle.posting_date <= si.posting_date ORDER BY sle.posting_date DESC LIMIT 1), sii.rate * 0.7) as buying_rate, sii.rate - COALESCE((SELECT AVG(valuation_rate) FROM `tabStock Ledger Entry` sle2 WHERE sle2.item_code = sii.item_code AND sle2.warehouse = sii.warehouse AND sle2.posting_date <= si.posting_date ORDER BY sle2.posting_date DESC LIMIT 1), sii.rate * 0.7) as profit_per_unit, (sii.rate - COALESCE((SELECT AVG(valuation_rate) FROM `tabStock Ledger Entry` sle3 WHERE sle3.item_code = sii.item_code AND sle3.warehouse = sii.warehouse AND sle3.posting_date <= si.posting_date ORDER BY sle3.posting_date DESC LIMIT 1), sii.rate * 0.7)) * sii.qty as total_profit FROM `tabSales Invoice` si INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name WHERE si.docstatus = 1 AND " + where_clause + " ORDER BY si.posting_date DESC LIMIT 1000"
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data: return []
        total_revenue = sum(float(row.get("selling_rate", 0) or 0) * float(row.get("qty", 0) or 0) for row in data)
        total_cost = sum(float(row.get("buying_rate", 0) or 0) * float(row.get("qty", 0) or 0) for row in data)
        total_profit = sum(float(row.get("total_profit", 0) or 0) for row in data)
        margin = (total_profit / total_revenue * 100) if total_revenue else 0
        return [{"label": "إجمالي الإيرادات", "value": "%.2f" % total_revenue, "indicator": "Green"}, {"label": "إجمالي التكلفة", "value": "%.2f" % total_cost, "indicator": "Red"}, {"label": "مجمل الربح", "value": "%.2f" % total_profit, "indicator": "Green"}, {"label": "نسبة الربح", "value": "%.2f%%" % margin, "indicator": "Blue"}]

def execute(filters=None):
    return GrossProfitDetailReport().execute(filters)
