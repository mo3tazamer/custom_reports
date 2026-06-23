import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class CustomerProfitabilityReport(BaseCustomReport):
    report_name = "customer_profitability"
    title = "Customer Profitability"
    icon = "user-check"

    def get_columns(self):
        return [
            {"fieldname": "customer", "label": "العميل", "fieldtype": "Link", "options": "Customer", "width": 180},
            {"fieldname": "total_sales", "label": "إجمالي المبيعات", "fieldtype": "Currency", "width": 150},
            {"fieldname": "total_cost", "label": "إجمالي التكلفة", "fieldtype": "Currency", "width": 150},
            {"fieldname": "total_profit", "label": "إجمالي الربح", "fieldtype": "Currency", "width": 150},
            {"fieldname": "profit_margin", "label": "نسبة الربح", "fieldtype": "Percent", "width": 120},
            {"fieldname": "invoice_count", "label": "عدد الفواتير", "fieldtype": "Int", "width": 120},
        ]

    def get_data(self, filters):
        conditions = []
        values = []
        if filters.get("customer"):
            conditions.append("si.customer = %s")
            values.append(filters["customer"])
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
            "SELECT si.customer, "
            "SUM(si.grand_total) as total_sales, "
            "SUM(sii.valuation_rate * sii.qty) as total_cost, "
            "SUM(si.grand_total) - SUM(sii.valuation_rate * sii.qty) as total_profit, "
            "((SUM(si.grand_total) - SUM(sii.valuation_rate * sii.qty)) / NULLIF(SUM(si.grand_total), 0)) * 100 as profit_margin, "
            "COUNT(DISTINCT si.name) as invoice_count "
            "FROM `tabSales Invoice` si "
            "INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name "
            "WHERE si.docstatus = 1 AND " + where_clause + " "
            "GROUP BY si.customer ORDER BY total_profit DESC LIMIT 1000"
        )
        return self.safe_sql(query, tuple(values), limit=1000)

    def get_summary(self, data, filters):
        if not data:
            return []
        total_sales = sum(float(row.get("total_sales", 0) or 0) for row in data)
        total_cost = sum(float(row.get("total_cost", 0) or 0) for row in data)
        total_profit = sum(float(row.get("total_profit", 0) or 0) for row in data)
        margin = (total_profit / total_sales * 100) if total_sales else 0
        return [
            {"label": "إجمالي المبيعات", "value": "%.2f" % total_sales, "indicator": "Green"},
            {"label": "إجمالي التكلفة", "value": "%.2f" % total_cost, "indicator": "Red"},
            {"label": "إجمالي الربح", "value": "%.2f" % total_profit, "indicator": "Green"},
            {"label": "نسبة الربح", "value": "%.2f%%" % margin, "indicator": "Blue"},
        ]

def execute(filters=None):
    return CustomerProfitabilityReport().execute(filters)
