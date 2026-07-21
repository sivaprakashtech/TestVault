/**
 * Reports & Analytics - Chart rendering and interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDistributionCharts();
    loadTrendChart(7);
    initTrendButtons();
    initExportDropdown();
});

function getColors() {
    const s = getComputedStyle(document.documentElement);
    return {
        success: s.getPropertyValue('--color-success').trim() || '#3fb950',
        danger: s.getPropertyValue('--color-danger').trim() || '#f85149',
        warning: s.getPropertyValue('--color-warning').trim() || '#d29922',
        blocked: s.getPropertyValue('--color-blocked').trim() || '#bc8cff',
        accent: s.getPropertyValue('--accent-primary').trim() || '#58a6ff',
        text: s.getPropertyValue('--text-secondary').trim() || '#8b949e',
        grid: s.getPropertyValue('--border-secondary').trim() || 'rgba(255,255,255,0.04)'
    };
}

const chartOpts = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { position: 'bottom', labels: { padding: 12, usePointStyle: true, pointStyle: 'circle' } } }
};

async function loadDistributionCharts() {
    const c = getColors();

    // Execution Distribution
    const execData = await fetch('/reports/api/execution-distribution').then(r => r.json());
    const colorMap = { 'Passed': c.success, 'Failed': c.danger, 'Blocked': c.blocked, 'Not Run': '#6e7681' };
    if (execData.length) {
        new Chart(document.getElementById('execChart'), {
            type: 'doughnut',
            data: { labels: execData.map(d => d.result), datasets: [{ data: execData.map(d => d.count), backgroundColor: execData.map(d => colorMap[d.result] || c.accent), borderWidth: 0 }] },
            options: { ...chartOpts, cutout: '60%' }
        });
    }

    // Bug Severity
    const sevData = await fetch('/reports/api/bug-severity').then(r => r.json());
    const sevColors = { 'Critical': c.danger, 'High': '#f0883e', 'Medium': c.warning, 'Low': '#8b949e' };
    if (sevData.length) {
        new Chart(document.getElementById('bugSevChart'), {
            type: 'doughnut',
            data: { labels: sevData.map(d => d.severity), datasets: [{ data: sevData.map(d => d.count), backgroundColor: sevData.map(d => sevColors[d.severity] || c.accent), borderWidth: 0 }] },
            options: { ...chartOpts, cutout: '60%' }
        });
    }

    // Bug Status
    const statusData = await fetch('/reports/api/bug-status').then(r => r.json());
    const statusColors = { 'Open': c.danger, 'In Progress': c.warning, 'Fixed': c.accent, 'Retest': '#bc8cff', 'Closed': c.success, 'Rejected': '#6e7681' };
    if (statusData.length) {
        new Chart(document.getElementById('bugStatusChart'), {
            type: 'doughnut',
            data: { labels: statusData.map(d => d.status), datasets: [{ data: statusData.map(d => d.count), backgroundColor: statusData.map(d => statusColors[d.status] || c.accent), borderWidth: 0 }] },
            options: { ...chartOpts, cutout: '60%' }
        });
    }

    // Case Priority
    const priData = await fetch('/reports/api/case-priority').then(r => r.json());
    const priColors = { 'Critical': c.danger, 'High': '#f0883e', 'Medium': c.warning, 'Low': '#8b949e' };
    if (priData.length) {
        new Chart(document.getElementById('casePriorityChart'), {
            type: 'doughnut',
            data: { labels: priData.map(d => d.priority), datasets: [{ data: priData.map(d => d.count), backgroundColor: priData.map(d => priColors[d.priority] || c.accent), borderWidth: 0 }] },
            options: { ...chartOpts, cutout: '60%' }
        });
    }
}

let trendChartInstance = null;
async function loadTrendChart(days) {
    const c = getColors();
    const data = await fetch(`/reports/api/execution-trend?days=${days}`).then(r => r.json());

    if (trendChartInstance) trendChartInstance.destroy();
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;

    trendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.day ? d.day.substring(5) : ''),
            datasets: [
                { label: 'Passed', data: data.map(d => d.passed), borderColor: c.success, backgroundColor: c.success + '20', tension: 0.4, fill: true, pointRadius: 2 },
                { label: 'Failed', data: data.map(d => d.failed), borderColor: c.danger, backgroundColor: c.danger + '20', tension: 0.4, fill: true, pointRadius: 2 },
                { label: 'Blocked', data: data.map(d => d.blocked), borderColor: c.blocked, backgroundColor: c.blocked + '20', tension: 0.4, fill: true, pointRadius: 2 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: { legend: { position: 'bottom', labels: { color: c.text, padding: 14, usePointStyle: true } } },
            scales: {
                x: { grid: { color: c.grid }, ticks: { color: c.text, font: { size: 10 } } },
                y: { beginAtZero: true, grid: { color: c.grid }, ticks: { color: c.text, stepSize: 1 } }
            }
        }
    });
}

function initTrendButtons() {
    document.querySelectorAll('.trend-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.trend-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadTrendChart(parseInt(btn.dataset.days));
        });
    });
}

function initExportDropdown() {
    document.addEventListener('click', (e) => {
        const menu = document.getElementById('exportMenu');
        if (menu && !e.target.closest('.dropdown-export')) menu.classList.remove('active');
    });
}
