frappe.provide('custom_reports');

class ModernReportTheme {
    constructor() {
        this.reportConfigs = {
            'sales-performance': { title: 'أداء المبيعات', icon: 'chart-line', cards: ['total_sales', 'invoice_count', 'avg_invoice', 'total_profit'] },
            'brand-sales-detail': { title: 'تفصيلي مبيعات العلامة التجارية', icon: 'tag', cards: ['brand_total', 'brand_items', 'brand_invoices', 'brand_avg'] },
            'customer-statement': { title: 'كشف حساب العميل', icon: 'user', cards: ['opening', 'total_debit', 'total_credit', 'closing'] },
            'supplier-statement': { title: 'كشف حساب المورد', icon: 'truck', cards: ['opening', 'total_debit', 'total_credit', 'closing'] },
            'item-movement': { title: 'كشف حركة الصنف', icon: 'box', cards: ['total_in', 'total_out', 'balance_qty', 'balance_value'] },
            'item-profitability': { title: 'ربحية الأصناف', icon: 'trending-up', cards: ['total_revenue', 'total_cost', 'gross_profit', 'profit_margin'] },
            'employee-salary': { title: 'مرتبات الموظفين', icon: 'users', cards: ['total_salary', 'employee_count', 'avg_salary', 'total_deductions'] },
            'employee-advance': { title: 'سلف الموظفين', icon: 'wallet', cards: ['total_advance', 'employee_count', 'total_returned', 'remaining'] },
            'stock-inventory': { title: 'جرد المخزون', icon: 'package', cards: ['total_items', 'total_value', 'low_stock', 'reorder_needed'] },
            'low-stock-items': { title: 'أصناف قاربت على الانتهاء', icon: 'alert-circle', cards: ['low_count', 'critical_count', 'total_value', 'reorder_value'] },
            'vat-report': { title: 'ضريبة القيمة المضافة', icon: 'percent', cards: ['total_vat', 'total_sales', 'total_purchases', 'net_vat'] },
            'customer-profitability': { title: 'ربحية العميل', icon: 'user-check', cards: ['total_sales', 'total_cost', 'total_profit', 'avg_margin'] },
            'period-comparison': { title: 'مقارنة الفترات', icon: 'git-compare', cards: ['period1_sales', 'period2_sales', 'variance', 'variance_pct'] },
            'dashboard': { title: 'لوحة التحكم', icon: 'layout-dashboard', cards: ['total_sales', 'total_purchases', 'total_customers', 'total_items'] },
            'cash-report': { title: 'كشف الخزينة', icon: 'banknote', cards: ['opening', 'total_in', 'total_out', 'closing'] },
            'bank-statement': { title: 'كشف حساب البنك', icon: 'landmark', cards: ['opening', 'total_in', 'total_out', 'closing'] },
            'purchase-analysis': { title: 'تحليل المشتريات', icon: 'shopping-cart', cards: ['total_purchases', 'invoice_count', 'avg_invoice', 'total_tax'] },
            'ar-aging': { title: 'عمر الديون - العملاء', icon: 'clock', cards: ['current', 'days_30', 'days_60', 'days_90'] },
            'ap-aging': { title: 'عمر الديون - الموردين', icon: 'clock', cards: ['current', 'days_30', 'days_60', 'days_90'] },
            'expense-report': { title: 'المصروفات', icon: 'receipt', cards: ['total_expense', 'voucher_count', 'avg_expense', 'top_account'] },
            'gross-profit-detail': { title: 'تفصيلي ربحية الصنف', icon: 'pie-chart', cards: ['total_revenue', 'total_cost', 'gross_profit', 'profit_margin'] },
            'stock-balance': { title: 'رصيد المخزون', icon: 'warehouse', cards: ['total_items', 'total_value', 'low_stock', 'reorder_needed'] }
        };

        this.init();
    }

    init() {
        if (!this.isCustomReportPage()) return;

        this.applyTheme();
        this.addCustomClasses();
        this.enhanceFilters();
        this.setupSummaryCards();
        this.enhanceTable();
        this.setupPagination();
    }

    isCustomReportPage() {
        const route = frappe.get_route();
        if (!route || route.length < 2) return false;

        const reportName = route[route.length - 1];
        return reportName && Object.keys(this.reportConfigs).some(key => 
            reportName.toLowerCase().includes(key.replace(/-/g, ''))
        );
    }

    getCurrentReportConfig() {
        const route = frappe.get_route();
        if (!route) return null;

        const reportName = route[route.length - 1];
        return Object.entries(this.reportConfigs).find(([key]) => 
            reportName.toLowerCase().includes(key.replace(/-/g, ''))
        )?.[1] || null;
    }

    applyTheme() {
        document.body.classList.add('custom-reports-active');

        const config = this.getCurrentReportConfig();
        if (!config) return;

        // Add report header
        const pageHead = document.querySelector('.page-head');
        if (pageHead && !pageHead.querySelector('.custom-report-header')) {
            const header = document.createElement('div');
            header.className = 'custom-report-header';
            header.innerHTML = `
                <h2><i class="fa fa-${config.icon}"></i> ${config.title}</h2>
                <p>تم إنشاؤه بواسطة Custom Reports</p>
            `;
            pageHead.insertBefore(header, pageHead.firstChild);
        }
    }

    addCustomClasses() {
        // Add numeric class to currency/number columns
        document.querySelectorAll('.report-wrapper td').forEach(td => {
            const text = td.textContent.trim();
            if (/^[\d,]+\.?\d*$/.test(text.replace(/,/g, ''))) {
                td.classList.add('numeric');
                const val = parseFloat(text.replace(/,/g, ''));
                if (val > 0) td.classList.add('positive');
                if (val < 0) td.classList.add('negative');
            }
        });
    }

    enhanceFilters() {
        const filterSection = document.querySelector('.filter-section');
        if (filterSection && !filterSection.classList.contains('cr-filters')) {
            filterSection.classList.add('cr-filters');
        }
    }

    setupSummaryCards() {
        const config = this.getCurrentReportConfig();
        if (!config || !config.cards) return;

        const reportWrapper = document.querySelector('.report-wrapper');
        if (!reportWrapper) return;

        // Remove existing cards
        const existing = reportWrapper.querySelector('.cr-summary-cards');
        if (existing) existing.remove();

        // Build cards from data
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'cr-summary-cards';

        config.cards.forEach((cardKey, index) => {
            const card = this.buildCard(cardKey, index);
            if (card) cardsContainer.appendChild(card);
        });

        reportWrapper.insertBefore(cardsContainer, reportWrapper.firstChild);
    }

    buildCard(key, index) {
        const cardData = this.getCardData(key);
        if (!cardData) return null;

        const div = document.createElement('div');
        div.className = 'cr-card';
        div.innerHTML = `
            <div class="cr-card-icon ${cardData.color}">
                <i class="fa fa-${cardData.icon}"></i>
            </div>
            <div class="cr-card-label">${cardData.label}</div>
            <div class="cr-card-value ${cardData.valueColor || ''}">${cardData.value}</div>
        `;
        return div;
    }

    getCardData(key) {
        const dataMap = {
            'total_sales': { label: 'إجمالي المبيعات', icon: 'chart-line', color: 'primary', value: '0.00', valueColor: 'success' },
            'invoice_count': { label: 'عدد الفواتير', icon: 'file-text', color: 'info', value: '0' },
            'avg_invoice': { label: 'متوسط الفاتورة', icon: 'calculator', color: 'warning', value: '0.00' },
            'total_profit': { label: 'إجمالي الربح', icon: 'trending-up', color: 'success', value: '0.00', valueColor: 'success' },
            'brand_total': { label: 'إجمالي المبيعات', icon: 'tag', color: 'primary', value: '0.00' },
            'brand_items': { label: 'عدد المنتجات', icon: 'box', color: 'info', value: '0' },
            'brand_invoices': { label: 'عدد الفواتير', icon: 'file-text', color: 'warning', value: '0' },
            'brand_avg': { label: 'متوسط الفاتورة', icon: 'calculator', color: 'success', value: '0.00' },
            'opening': { label: 'الرصيد الافتتاحي', icon: 'arrow-right', color: 'primary', value: '0.00' },
            'total_debit': { label: 'إجمالي المدين', icon: 'arrow-up', color: 'danger', value: '0.00', valueColor: 'danger' },
            'total_credit': { label: 'إجمالي الدائن', icon: 'arrow-down', color: 'success', value: '0.00', valueColor: 'success' },
            'closing': { label: 'الرصيد الختامي', icon: 'balance-scale', color: 'primary', value: '0.00' },
            'total_in': { label: 'إجمالي الوارد', icon: 'arrow-down', color: 'success', value: '0.00' },
            'total_out': { label: 'إجمالي الصادر', icon: 'arrow-up', color: 'danger', value: '0.00' },
            'balance_qty': { label: 'الرصيد', icon: 'box', color: 'primary', value: '0' },
            'balance_value': { label: 'القيمة', icon: 'dollar-sign', color: 'warning', value: '0.00' },
            'total_revenue': { label: 'إجمالي الإيرادات', icon: 'chart-line', color: 'primary', value: '0.00' },
            'total_cost': { label: 'إجمالي التكلفة', icon: 'dollar-sign', color: 'danger', value: '0.00' },
            'gross_profit': { label: 'مجمل الربح', icon: 'trending-up', color: 'success', value: '0.00', valueColor: 'success' },
            'profit_margin': { label: 'نسبة الربح', icon: 'percent', color: 'info', value: '0%' },
            'total_salary': { label: 'إجمالي المرتبات', icon: 'dollar-sign', color: 'primary', value: '0.00' },
            'employee_count': { label: 'عدد الموظفين', icon: 'users', color: 'info', value: '0' },
            'avg_salary': { label: 'متوسط المرتب', icon: 'calculator', color: 'warning', value: '0.00' },
            'total_deductions': { label: 'إجمالي الاستقطاعات', icon: 'minus', color: 'danger', value: '0.00' },
            'total_advance': { label: 'إجمالي السلف', icon: 'wallet', color: 'primary', value: '0.00' },
            'total_returned': { label: 'المسترد', icon: 'rotate-ccw', color: 'success', value: '0.00' },
            'remaining': { label: 'المتبقي', icon: 'alert-circle', color: 'warning', value: '0.00' },
            'total_items': { label: 'عدد الأصناف', icon: 'package', color: 'primary', value: '0' },
            'total_value': { label: 'القيمة الإجمالية', icon: 'dollar-sign', color: 'warning', value: '0.00' },
            'low_stock': { label: 'أصناف منخفضة', icon: 'alert-triangle', color: 'danger', value: '0' },
            'reorder_needed': { label: 'تحتاج إعادة طلب', icon: 'refresh-cw', color: 'warning', value: '0' },
            'low_count': { label: 'أصناف منخفضة', icon: 'alert-triangle', color: 'danger', value: '0' },
            'critical_count': { label: 'أصناف حرجة', icon: 'alert-circle', color: 'danger', value: '0' },
            'reorder_value': { label: 'قيمة إعادة الطلب', icon: 'dollar-sign', color: 'warning', value: '0.00' },
            'total_vat': { label: 'إجمالي الضريبة', icon: 'percent', color: 'primary', value: '0.00' },
            'total_purchases': { label: 'إجمالي المشتريات', icon: 'shopping-cart', color: 'info', value: '0.00' },
            'net_vat': { label: 'صافي الضريبة', icon: 'calculator', color: 'success', value: '0.00' },
            'avg_margin': { label: 'متوسط الربح', icon: 'percent', color: 'info', value: '0%' },
            'period1_sales': { label: 'مبيعات الفترة 1', icon: 'chart-line', color: 'primary', value: '0.00' },
            'period2_sales': { label: 'مبيعات الفترة 2', icon: 'chart-line', color: 'info', value: '0.00' },
            'variance': { label: 'الفرق', icon: 'git-compare', color: 'warning', value: '0.00' },
            'variance_pct': { label: 'نسبة الفرق', icon: 'percent', color: 'success', value: '0%' },
            'total_customers': { label: 'عدد العملاء', icon: 'users', color: 'info', value: '0' },
            'total_expense': { label: 'إجمالي المصروفات', icon: 'receipt', color: 'danger', value: '0.00' },
            'voucher_count': { label: 'عدد القيود', icon: 'file-text', color: 'primary', value: '0' },
            'avg_expense': { label: 'متوسط المصروف', icon: 'calculator', color: 'warning', value: '0.00' },
            'top_account': { label: 'أكبر حساب', icon: 'award', color: 'success', value: '-' },
            'current': { label: 'حالي', icon: 'check', color: 'success', value: '0.00' },
            'days_30': { label: '30 يوم', icon: 'clock', color: 'warning', value: '0.00' },
            'days_60': { label: '60 يوم', icon: 'clock', color: 'danger', value: '0.00' },
            'days_90': { label: '90+ يوم', icon: 'alert-circle', color: 'danger', value: '0.00' }
        };

        return dataMap[key] || null;
    }

    enhanceTable() {
        const table = document.querySelector('.report-wrapper table');
        if (!table) return;

        // Add hover effect rows
        table.querySelectorAll('tbody tr').forEach(row => {
            row.addEventListener('mouseenter', () => {
                row.style.backgroundColor = 'rgba(124, 92, 196, 0.05)';
            });
            row.addEventListener('mouseleave', () => {
                row.style.backgroundColor = '';
            });
        });
    }

    setupPagination() {
        const pagination = document.querySelector('.pagination');
        if (!pagination) return;

        pagination.classList.add('cr-pagination');
        pagination.querySelectorAll('a, button, span').forEach(el => {
            el.classList.add('page-btn');
        });
    }
}

// Initialize on page load and route change
frappe.router.on('change', () => {
    setTimeout(() => new ModernReportTheme(), 100);
});

$(document).on('page-change', () => {
    setTimeout(() => new ModernReportTheme(), 100);
});
