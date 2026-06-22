# Custom Reports for ERPNext

Modern themed reports for ERPNext with Odoo-style UI.

## Features

- 22+ Custom Reports (Sales, Purchases, Inventory, Accounting, HR)
- Modern White/Purple Theme
- Scoped CSS (zero impact on other ERPNext pages)
- Route-Aware ES6+ JavaScript
- Base Report Class with Parameterized SQL
- Smart Brand Split (filter by brand while keeping full invoice view)
- Arabic UI Support
- Performance Optimized (caching, limits, indexes)

## Reports Included

### Sales (5)
1. Sales Performance (أداء المبيعات)
2. Brand Sales Detail (تفصيلي مبيعات العلامة التجارية)
3. Customer Statement (كشف حساب العميل)
4. Customer Profitability (ربحية العميل)
5. AR Aging (عمر الديون - العملاء)

### Purchases (3)
6. Purchase Analysis (تحليل المشتريات)
7. Supplier Statement (كشف حساب المورد)
8. AP Aging (عمر الديون - الموردين)

### Inventory (5)
9. Stock Balance (رصيد المخزون)
10. Item Movement (كشف حركة الصنف)
11. Item Profitability (ربحية الأصناف)
12. Stock Inventory (جرد المخزون)
13. Low Stock Items (أصناف قاربت على الانتهاء)

### Accounting (6)
14. Cash Report (كشف الخزينة)
15. Expense Report (المصروفات)
16. Gross Profit Detail (تفصيلي ربحية الصنف)
17. VAT Report (ضريبة القيمة المضافة)
18. Period Comparison (مقارنة الفترات)
19. Dashboard (لوحة التحكم)

### HR (2)
20. Employee Salaries (مرتبات الموظفين)
21. Employee Advances (سلف الموظفين)

### Banking (1)
22. Bank Statement (كشف حساب البنك)

## Installation

```bash
bench get-app https://github.com/mo3tazamer/custom_reports.git
bench --site site1.localhost install-app custom_reports
bench --site site1.localhost migrate
bench --site site1.localhost clear-cache
bench start
```

## Performance

- Parameterized SQL queries (SQL injection safe)
- 5-minute Redis caching
- LIMIT 1000 for detail reports, LIMIT 24 for monthly
- Proper database indexes
- Error handling on all methods

## License

MIT
