import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class ItemProfitabilityReport(BaseCustomReport):
    report_name = "item_profitability"
    title = "Item Profitability"
    icon = "trending-up"

    def get_columns(self):
        return [
        {"fieldname": "item_code", "label": "الصنف", "fieldtype": "Link", "options": "Item", "width": 150},
        {"fieldname": "item_name", "label": "إسم الصنف", "fieldtype": "Data", "width": 200},
        {"fieldname": "buying_rate", "label": "سعر الشراء", "fieldtype": "Currency", "width": 120},
        {"fieldname": "selling_rate", "label": "سعر البيع", "fieldtype": "Currency", "width": 120},
        {"fieldname": "profit_per_unit", "label": "الربح للقطعة", "fieldtype": "Currency", "width": 130},
        {"fieldname": "profit_margin_pct", "label": "نسبة الربح", "fieldtype": "Percent", "width": 120},
        {"fieldname": "total_qty", "label": "عدد الوحدات", "fieldtype": "Float", "width": 120},
        {"fieldname": "total_buying", "label": "إجمالي سعر الشراء", "fieldtype": "Currency", "width": 150},
        {"fieldname": "total_selling", "label": "إجمالي سعر البيع", "fieldtype": "Currency", "width": 150},
        {"fieldname": "total_profit", "label": "الربحية", "fieldtype": "Currency", "width": 130},
    ]

    def get_data(self, filters):
        conditions = []
        values = []

        if filters.get("item"):
            conditions.append("sii.item_code = %s")
            values.append(filters["item"])
        if filters.get("customer"):
            conditions.append("si.customer = %s")
            values.append(filters["customer"])
        if filters.get("brand"):
            conditions.append("sii.brand = %s")
            values.append(filters["brand"])
        if filters.get("from_date"):
            conditions.append("si.posting_date >= %s")
            values.append(filters["from_date"])
        if filters.get("to_date"):
            conditions.append("si.posting_date <= %s")
            values.append(filters["to_date"])
        if filters.get("company"):
            conditions.append("si.company = %s")
            values.append(filters["company"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = (
            "SELECT sii.item_code, sii.item_name, "
            "AVG(sii.valuation_rate) as buying_rate, "
            "AVG(sii.rate) as selling_rate, "
            "AVG(sii.rate) - AVG(sii.valuation_rate) as profit_per_unit, "
            "((AVG(sii.rate) - AVG(sii.valuation_rate)) / NULLIF(AVG(sii.rate), 0)) * 100 as profit_margin_pct, "
            "SUM(sii.qty) as total_qty, "
            "SUM(sii.valuation_rate * sii.qty) as total_buying, "
            "SUM(sii.amount) as total_selling, "
            "SUM(sii.amount) - SUM(sii.valuation_rate * sii.qty) as total_profit "
            "FROM `tabSales Invoice` si "
            "INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name "
            "WHERE si.docstatus = 1 AND " + where_clause + " "
            "GROUP BY sii.item_code "
            "HAVING SUM(sii.qty) > 0 "
            "ORDER BY total_profit DESC LIMIT 1000"
        )

        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data:
            return []

        total_revenue = sum(float(row.get("total_selling", 0) or 0) for row in data)
        total_cost = sum(float(row.get("total_buying", 0) or 0) for row in data)
        total_profit = sum(float(row.get("total_profit", 0) or 0) for row in data)
        total_qty = sum(float(row.get("total_qty", 0) or 0) for row in data)
        margin = (total_profit / total_revenue * 100) if total_revenue else 0

        return [
            {"label": "إجمالي الإيرادات", "value": "%.2f" % total_revenue, "indicator": "Green"},
            {"label": "إجمالي التكلفة", "value": "%.2f" % total_cost, "indicator": "Red"},
            {"label": "مجمل الربح", "value": "%.2f" % total_profit, "indicator": "Green"},
            {"label": "نسبة الربح", "value": "%.2f%%" % margin, "indicator": "Blue"},
        ]

def execute(filters=None):
    return ItemProfitabilityReport().execute(filters)
