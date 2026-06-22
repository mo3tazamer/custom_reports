frappe.provide('custom_reports');
class ModernReportTheme {
    constructor() { this.init(); }
    init() { if (!this.isCustomReportPage()) return; document.body.classList.add('custom-reports-active'); }
    isCustomReportPage() {
        const route = frappe.get_route();
        if (!route || route.length < 2) return false;
        const name = route[route.length - 1].toLowerCase();
        const reports = ['sales-performance','brand-sales','item-profitability','customer-statement','supplier-statement','cash-report','bank-statement','ar-aging','ap-aging','stock-balance','stock-inventory','low-stock','item-movement','purchase-analysis','vat-report','expense-report','gross-profit','period-comparison','dashboard','employee-salary','employee-advance','customer-profitability'];
        return reports.some(r => name.includes(r.replace(/-/g, '')));
    }
}
frappe.router.on('change', () => { setTimeout(() => new ModernReportTheme(), 100); });
$(document).on('page-change', () => { setTimeout(() => new ModernReportTheme(), 100); });
