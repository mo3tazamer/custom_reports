import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class StockBalanceReport(BaseCustomReport):
    report_name = "stock_balance"
    title = "Stock Balance"
    icon = "warehouse"

    def get_columns(self):
        return [
            {"fieldname": "item_code", "label": "الصنف", "fieldtype": "Link", "options": "Item", "width": 150},
            {"fieldname": "item_name", "label": "إسم الصنف", "fieldtype": "Data", "width": 200},
            {"fieldname": "warehouse", "label": "المخزن", "fieldtype": "Link", "options": "Warehouse", "width": 150},
            {"fieldname": "actual_qty", "label": "الكمية", "fieldtype": "Float", "width": 100},
            {"fieldname": "valuation_rate", "label": "سعر التكلفة", "fieldtype": "Currency", "width": 120},
            {"fieldname": "stock_value", "label": "القيمة", "fieldtype": "Currency", "width": 130},
            {"fieldname": "reorder_level", "label": "مستوى إعادة الطلب", "fieldtype": "Float", "width": 150},
            {"fieldname": "status", "label": "الحالة", "fieldtype": "Data", "width": 120},
        ]

    def get_data(self, filters):
        conditions = []
        values = []
        if filters.get("warehouse"):
            conditions.append("b.warehouse = %s")
            values.append(filters["warehouse"])
        if filters.get("item"):
            conditions.append("b.item_code = %s")
            values.append(filters["item"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = (
            "SELECT b.item_code, i.item_name, b.warehouse, "
            "b.actual_qty, b.valuation_rate, "
            "b.actual_qty * b.valuation_rate as stock_value, "
            "i.reorder_level, "
            "CASE WHEN b.actual_qty <= i.reorder_level THEN 'منخفض' ELSE 'متوفر' END as status "
            "FROM `tabBin` b "
            "INNER JOIN `tabItem` i ON i.name = b.item_code "
            "WHERE " + where_clause + " AND b.actual_qty > 0 "
            "ORDER BY b.actual_qty ASC LIMIT 1000"
        )
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data:
            return []
        total_items = len(data)
        total_value = sum(float(row.get("stock_value", 0) or 0) for row in data)
        low_stock = sum(1 for row in data if row.get("status") == "منخفض")
        return [
            {"label": "عدد الأصناف", "value": str(total_items), "indicator": "Blue"},
            {"label": "القيمة الإجمالية", "value": "%.2f" % total_value, "indicator": "Green"},
            {"label": "أصناف منخفضة", "value": str(low_stock), "indicator": "Red"},
        ]

def execute(filters=None):
    return StockBalanceReport().execute(filters)
