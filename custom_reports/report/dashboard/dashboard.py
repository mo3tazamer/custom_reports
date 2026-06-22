import frappe
from custom_reports.custom_reports.report.base_report import BaseCustomReport

class DashboardReport(BaseCustomReport):
    report_name = "dashboard"
    title = "Dashboard"
    icon = "layout-dashboard"

    def get_columns(self):
        return [
            {"fieldname": "metric", "label": "البيان", "fieldtype": "Data", "width": 250},
            {"fieldname": "value", "label": "القيمة", "fieldtype": "Currency", "width": 150},
        ]

    def get_data(self, filters):
        company = filters.get("company", "")

        # Sales
        total_sales = frappe.db.sql(
            "SELECT COALESCE(SUM(grand_total), 0) FROM `tabSales Invoice` WHERE docstatus = 1 AND company = %s",
            (company,))[0][0] or 0

        # Purchases
        total_purchases = frappe.db.sql(
            "SELECT COALESCE(SUM(grand_total), 0) FROM `tabPurchase Invoice` WHERE docstatus = 1 AND company = %s",
            (company,))[0][0] or 0

        # Customers
        total_customers = frappe.db.sql(
            "SELECT COUNT(*) FROM `tabCustomer` WHERE disabled = 0")[0][0] or 0

        # Suppliers
        total_suppliers = frappe.db.sql(
            "SELECT COUNT(*) FROM `tabSupplier` WHERE disabled = 0")[0][0] or 0

        # Items
        total_items = frappe.db.sql(
            "SELECT COUNT(*) FROM `tabItem` WHERE disabled = 0")[0][0] or 0

        # Employees
        total_employees = frappe.db.sql(
            "SELECT COUNT(*) FROM `tabEmployee" WHERE status = 'Active'")[0][0] or 0

        # Cash/Bank Balance
        cash_balance = frappe.db.sql(
            "SELECT COALESCE(SUM(debit - credit), 0) FROM `tabGL Entry` WHERE account LIKE '%%Cash%%' AND company = %s",
            (company,))[0][0] or 0

        # AR (Accounts Receivable)
        ar_balance = frappe.db.sql(
            "SELECT COALESCE(SUM(debit - credit), 0) FROM `tabGL Entry` WHERE party_type = 'Customer' AND company = %s",
            (company,))[0][0] or 0

        # AP (Accounts Payable)
        ap_balance = frappe.db.sql(
            "SELECT COALESCE(SUM(credit - debit), 0) FROM `tabGL Entry` WHERE party_type = 'Supplier' AND company = %s",
            (company,))[0][0] or 0

        return [
            {"metric": "إجمالي المبيعات", "value": total_sales},
            {"metric": "إجمالي المشتريات", "value": total_purchases},
            {"metric": "عدد العملاء", "value": total_customers},
            {"metric": "عدد الموردين", "value": total_suppliers},
            {"metric": "عدد الأصناف", "value": total_items},
            {"metric": "عدد الموظفين", "value": total_employees},
            {"metric": "رصيد الخزينة", "value": cash_balance},
            {"metric": "ذمم العملاء", "value": ar_balance},
            {"metric": "ذمم الموردين", "value": ap_balance},
        ]

    def get_summary(self, data, filters):
        return []

def execute(filters=None):
    return DashboardReport().execute(filters)
