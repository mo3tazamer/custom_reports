import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class LowStockItemsReport(BaseCustomReport):
    report_name = "low_stock_items"
    title = "Low Stock Items"
    icon = "alert-circle"

    def get_columns(self):
        return [
            {"fieldname": "item_code", "label": "الصنف", "fieldtype": "Link", "options": "Item", "width": 150},
            {"fieldname": "item_name", "label": "إسم الصنف", "fieldtype": "Data", "width": 200},
            {"fieldname": "warehouse", "label": "المخزن", "fieldtype": "Link", "options": "Warehouse", "width": 150},
            {"fieldname": "actual_qty", "label": "الكمية الحالية", "fieldtype": "Float", "width": 130},
            {"fieldname": "reorder_level", "label": "مستوى إعادة الطلب", "fieldtype": "Float", "width": 150},
            {"fieldname": "shortage", "label": "النقص", "fieldtype": "Float", "width": 100},
            {"fieldname": "valuation_rate", "label": "سعر التكلفة", "fieldtype": "Currency", "width": 120},
            {"fieldname": "reorder_value", "label": "قيمة إعادة الطلب", "fieldtype": "Currency", "width": 150},
        ]

    def get_data(self, filters):
        conditions = []
        values = []
        if filters.get("warehouse"):
            conditions.append("b.warehouse = %s")
            values.append(filters["warehouse"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = (
            "SELECT b.item_code, i.item_name, b.warehouse, "
            "b.actual_qty, i.reorder_level, "
            "i.reorder_level - b.actual_qty as shortage, "
            "b.valuation_rate, "
            "(i.reorder_level - b.actual_qty) * b.valuation_rate as reorder_value "
            "FROM `tabBin` b "
            "INNER JOIN `tabItem` i ON i.name = b.item_code "
            "WHERE " + where_clause + " AND b.actual_qty <= i.reorder_level AND i.reorder_level > 0 "
            "ORDER BY shortage DESC LIMIT 1000"
        )
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data:
            return []
        total_items = len(data)
        total_value = sum(float(row.get("reorder_value", 0) or 0) for row in data)
        critical = sum(1 for row in data if float(row.get("actual_qty", 0) or 0) == 0)
        return [
            {"label": "أصناف منخفضة", "value": str(total_items), "indicator": "Red"},
            {"label": "أصناف حرجة", "value": str(critical), "indicator": "Red"},
            {"label": "قيمة إعادة الطلب", "value": "%.2f" % total_value, "indicator": "Orange"},
        ]

def execute(filters=None):
    return LowStockItemsReport().execute(filters)
