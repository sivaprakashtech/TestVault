/**
 * Dashboard JavaScript - Charts & Data Loading
 * QA Test Management System (TestVault)
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
    loadTrendChart();
    loadModuleStats();
    loadRecentActivity();
});

/**
 * Chart.js global configuration for our theme
 */
function getChartDefaults() {
    const style = getComputedStyle(document.documentElement);
    return {
        textColor: style.getPropertyValue('--text-secondary').trim(),
        gridColor: style.getPropertyValue('--border-secondary').trim(),
        success: style.getPropertyValue('--color-success').trim() || '#3fb950',
        danger: style.getPropertyValue('--color-danger').trim() || '#f85149',
        blocked: style.getPropertyValue('--color-blocked').trim() || '#bc8cff',
        accent: style.getPropertyValue('--accent-primary').trim() || '#58a6ff'
    };
}

/**
 * Load dashboard statistics
 */
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();

        document.getElementById('totalCases').textContent = data.total_cases || 0;
        document.getElementById('passedCount').textContent = data.passed || 0;
        document.getElementById('failedCount').textContent = data.failed || 0;
        document.getElementById('blockedCount').textContent = data.blocked || 0;
        document.getElementById('notExecCount').textContent = data.not_executed || 0;

        // Render priority chart
        renderPriorityChart(data.priority_distribution || []);

        // Render severity chart
        renderSeverityChart(data.severity_distribution || []);
    } catch (error) {
        console.error('Failed to load dashboard stats:', error);
    }
}

/**
 * Load and render execution trend chart
 */
async function loadTrendChart() {
    try {
        const response = await fetch('/api/dashboard/trend');
        const data = await response.json();

        const colors = getChartDefaults();
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => {
                    const date = new Date(d.exec_date);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                }),
                datasets: [
                    {
                        label: 'Passed',
                        data: data.map(d => d.passed),
                        borderColor: colors.success,
                        backgroundColor: colors.success + '20',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    },
                    {
                        label: 'Failed',
                        data: data.map(d => d.failed),
                        borderColor: colors.danger,
                        backgroundColor: colors.danger + '20',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    },
                    {
                        label: 'Blocked',
                        data: data.map(d => d.blocked),
                        borderColor: colors.blocked,
                        backgroundColor: colors.blocked + '20',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 3,
                        pointHoverRadius: 5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'index' },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: colors.textColor, padding: 16, usePointStyle: true, pointStyle: 'circle' }
                    }
                },
                scales: {
                    x: {
                        grid: { color: colors.gridColor, drawBorder: false },
                        ticks: { color: colors.textColor, font: { size: 11 } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: colors.gridColor, drawBorder: false },
                        ticks: { color: colors.textColor, font: { size: 11 }, stepSize: 1 }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Failed to load trend data:', error);
    }
}

/**
 * Render priority distribution doughnut chart
 */
function renderPriorityChart(data) {
    const ctx = document.getElementById('priorityChart');
    if (!ctx || !data.length) return;

    const colorMap = {
        'Critical': '#f85149',
        'High': '#f0883e',
        'Medium': '#d29922',
        'Low': '#8b949e'
    };

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.priority),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: data.map(d => colorMap[d.priority] || '#8b949e'),
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: getChartDefaults().textColor,
                        padding: 16,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            }
        }
    });
}

/**
 * Render severity distribution chart
 */
function renderSeverityChart(data) {
    const ctx = document.getElementById('severityChart');
    if (!ctx || !data.length) return;

    const colorMap = {
        'Blocker': '#f85149',
        'Critical': '#f0883e',
        'Major': '#d29922',
        'Minor': '#58a6ff',
        'Trivial': '#8b949e'
    };

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.severity),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: data.map(d => colorMap[d.severity] || '#8b949e'),
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: getChartDefaults().textColor,
                        padding: 16,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            }
        }
    });
}

/**
 * Load module-wise stats
 */
async function loadModuleStats() {
    try {
        const response = await fetch('/api/dashboard/module-stats');
        const data = await response.json();

        const colors = getChartDefaults();
        const ctx = document.getElementById('moduleChart');
        if (!ctx || !data.length) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.module),
                datasets: [{
                    label: 'Pass %',
                    data: data.map(d => d.pass_percentage),
                    backgroundColor: colors.success + '80',
                    borderColor: colors.success,
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: colors.gridColor, drawBorder: false },
                        ticks: { color: colors.textColor, callback: v => v + '%' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: colors.textColor, font: { size: 11 } }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Failed to load module stats:', error);
    }
}

/**
 * Load recent activity
 */
async function loadRecentActivity() {
    try {
        const response = await fetch('/api/dashboard/recent-activity');
        const data = await response.json();

        // Render recent cases
        const casesContainer = document.getElementById('recentCases');
        if (casesContainer && data.recent_cases) {
            if (data.recent_cases.length === 0) {
                casesContainer.innerHTML = '<li class="activity-item"><div class="activity-content"><span class="activity-title" style="color:var(--text-tertiary)">No test cases yet</span></div></li>';
            } else {
                casesContainer.innerHTML = data.recent_cases.map(tc => `
                    <li class="activity-item">
                        <div class="activity-dot created"></div>
                        <div class="activity-content">
                            <span class="activity-title">${tc.test_id} - ${tc.title}</span>
                            <span class="activity-meta">${tc.priority} · ${tc.creator_name || 'Unknown'}</span>
                        </div>
                    </li>
                `).join('');
            }
        }

        // Render recent executions
        const execContainer = document.getElementById('recentExecutions');
        if (execContainer && data.recent_executions) {
            if (data.recent_executions.length === 0) {
                execContainer.innerHTML = '<li class="activity-item"><div class="activity-content"><span class="activity-title" style="color:var(--text-tertiary)">No executions yet</span></div></li>';
            } else {
                execContainer.innerHTML = data.recent_executions.map(exec => `
                    <li class="activity-item">
                        <div class="activity-dot ${exec.result.toLowerCase().replace(' ', '-')}"></div>
                        <div class="activity-content">
                            <span class="activity-title">${exec.test_id} - ${exec.test_title}</span>
                            <span class="activity-meta">${exec.result} · ${exec.executor_name || 'Unknown'}</span>
                        </div>
                    </li>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Failed to load recent activity:', error);
    }
}
