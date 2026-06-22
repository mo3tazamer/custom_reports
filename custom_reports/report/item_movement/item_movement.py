import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class ItemMovementReport(BaseCustomReport):
    report_name = "item_movement"
    title = "Item Movement"
    icon = "box"

    def get_columns(self):
        return [
            {"fieldname": "posting_date", "label": "التاريخ", "fieldtype": "Date", "width": 120},
            {"fieldname": "voucher_type", "label": "نوع الحركة", "fieldtype": "Data", "width": 130},
            {"fieldname": "voucher_no", "label": "رقم المستند", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 140},
            {"fieldname": "warehouse", "label": "المخزن", "fieldtype": "Link", "options": "Warehouse", "width": 150},
            {"fieldname": "actual_qty", "label": "الكمية", "fieldtype": "Float", "width": 100},
            {"fieldname": "qty_after_transaction", "label": "الرصيد", "fieldtype": "Float", "width": 100},
            {"fieldname": "valuation_rate", "label": "سعر التكلفة", "fieldtype": "Currency", "width": 120},
            {"fieldname": "stock_value", "label": "القيمة", "fieldtype": "Currency", "width": 130},
        ]

    def get_data(self, filters):
        conditions = []
        values = []
        if filters.get("item"):
            conditions.append("item_code = %s")
            values.append(filters["item"])
        if filters.get("warehouse"):
            conditions.append("warehouse = %s")
            values.append(filters["warehouse"])
        if filters.get("from_date"):
            conditions.append("posting_date >= %s")
            values.append(filters["from_date"])
        if filters.get("to_date"):
            conditions.append("posting_date <= %s")
            values.append(filters["to_date"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = (
            "SELECT posting_date, voucher_type, voucher_no, warehouse, "
            "actual_qty, qty_after_transaction, valuation_rate, stock_value "
            "FROM `tabStock Ledger Entry` "
            "WHERE " + where_clause + " "
            "ORDER BY posting_date DESC, creation DESC LIMIT 1000"
        )
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data:
            return []
        total_in = sum(float(row.get("actual_qty", 0) or 0) for row in data if float(row.get("actual_qty", 0) or 0) > 0)
        total_out = sum(abs(float(row.get("actual_qty", 0) or 0)) for row in data if float(row.get("actual_qty", 0) or 0) < 0)
        return [
            {"label": "إجمالي الوارد", "value": "%.2f" % total_in, "indicator": "Green"},
            {"label": "إجمالي الصادر", "value": "%.2f" % total_out, "indicator": "Red"},
        ]

def execute(filters=None):
    return ItemMovementReport().execute(filters)
