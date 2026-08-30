// Chart.js Visualization Engine
document.addEventListener('DOMContentLoaded', () => {
    if (!window.DASHBOARD_DATA) return;

    const { categoryBreakdown, paymentBreakdown } = window.DASHBOARD_DATA;

    const categoryColors = [
        '#0ea5e9', '#f59e0b', '#ec4899', '#10b981', '#6366f1',
        '#8b5cf6', '#14b8a6', '#f97316', '#eab308', '#64748b'
    ];

    // 1. Category Donut Chart
    const catCanvas = document.getElementById('categoryChart');
    if (catCanvas && categoryBreakdown && categoryBreakdown.length > 0) {
        new Chart(catCanvas, {
            type: 'doughnut',
            data: {
                labels: categoryBreakdown.map(c => c.category),
                datasets: [{
                    data: categoryBreakdown.map(c => c.amount),
                    backgroundColor: categoryColors.slice(0, categoryBreakdown.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const val = context.raw;
                                const formatted = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(val);
                                return ` ${context.label}: ${formatted}`;
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // 2. Payment Method Chart
    const payCanvas = document.getElementById('paymentChart');
    if (payCanvas && paymentBreakdown && paymentBreakdown.length > 0) {
        const paymentColors = {
            'UPI': '#9333ea',
            'Bank Transfer': '#2563eb',
            'Credit/Debit Card': '#059669',
            'Cash': '#d97706'
        };

        new Chart(payCanvas, {
            type: 'pie',
            data: {
                labels: paymentBreakdown.map(p => p.method),
                datasets: [{
                    data: paymentBreakdown.map(p => p.amount),
                    backgroundColor: paymentBreakdown.map(p => paymentColors[p.method] || '#64748b'),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            font: {
                                size: 11,
                                family: 'Plus Jakarta Sans'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const val = context.raw;
                                const formatted = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(val);
                                return ` ${context.label}: ${formatted}`;
                            }
                        }
                    }
                }
            }
        });
    }
});
