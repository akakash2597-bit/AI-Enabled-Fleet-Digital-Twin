/**
 * Chart.js Integration Module for Fleet Telemetry & Health Monitoring
 * Handles rendering of sensor time-series and health score metrics.
 */

class FleetCharts {
    /**
     * Initializes the Fleet Health Breakdown Doughnut Chart.
     */
    static initHealthDonutChart(canvasId, operational = 3, warning = 1, critical = 1) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Operational (Normal)', 'Warning (Degraded)', 'Critical (High Risk)'],
                datasets: [{
                    data: [operational, warning, critical],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    borderColor: '#111827',
                    borderWidth: 3,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1f2937',
                        titleColor: '#f9fafb',
                        bodyColor: '#9ca3af',
                        borderColor: '#374151',
                        borderWidth: 1,
                        padding: 10
                    }
                }
            }
        });
    }

    /**
     * Initializes the Fleet Multi-Sensor Telemetry Trends Line Chart on Dashboard.
     */
    static initFleetTelemetryChart(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        // Sample aggregated operating cycles
        const hours = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00'];
        const coolantTemp = [78.2, 79.0, 77.5, 82.1, 85.4, 91.0, 89.2, 86.0, 83.5, 80.1];
        const oilPressure = [3.4, 3.3, 3.5, 3.1, 2.9, 2.7, 2.8, 3.0, 3.2, 3.3];
        const engineRpmDiv100 = [7.5, 7.8, 7.4, 8.2, 8.8, 9.2, 8.5, 8.0, 7.7, 7.5];

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: hours,
                datasets: [
                    {
                        label: 'Coolant Temp (°C)',
                        data: coolantTemp,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.08)',
                        tension: 0.35,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Oil Pressure (bar)',
                        data: oilPressure,
                        borderColor: '#3b82f6',
                        backgroundColor: 'transparent',
                        borderDash: [5, 5],
                        tension: 0.35,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Engine RPM (x100)',
                        data: engineRpmDiv100,
                        borderColor: '#f59e0b',
                        backgroundColor: 'transparent',
                        tension: 0.35,
                        yAxisID: 'y'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af', font: { family: 'Inter' } }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' },
                        title: { display: true, text: 'Temp (°C) / RPM (x100)', color: '#6b7280' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: { color: '#60a5fa' },
                        title: { display: true, text: 'Oil Pres (bar)', color: '#60a5fa' }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1f2937',
                        borderColor: '#374151',
                        borderWidth: 1,
                        padding: 12
                    }
                }
            }
        });
    }

    /**
     * Initializes the Historical Telemetry Chart for an individual vehicle.
     */
    static initVehicleDetailChart(canvasId, telemetryData) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        let labels = [];
        let coolTemps = [];
        let oilPressures = [];
        let rpms = [];

        if (telemetryData && telemetryData.length > 0) {
            labels = telemetryData.map(d => d.timestamp ? d.timestamp.split(' ')[1] : '');
            coolTemps = telemetryData.map(d => d.coolant_temp_c || d.engine_temp_c || 78);
            oilPressures = telemetryData.map(d => d.oil_pressure_psi || 3.2);
            rpms = telemetryData.map(d => (d.engine_rpm || 750) / 10);
        } else {
            labels = ['T-5', 'T-4', 'T-3', 'T-2', 'T-1', 'Now'];
            coolTemps = [76, 77, 78, 80, 82, 81];
            oilPressures = [3.5, 3.4, 3.3, 3.2, 3.1, 3.2];
            rpms = [75, 78, 76, 80, 82, 79];
        }

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Coolant Temp (°C)',
                        data: coolTemps,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Oil Pressure (bar)',
                        data: oilPressures,
                        borderColor: '#3b82f6',
                        backgroundColor: 'transparent',
                        tension: 0.3
                    },
                    {
                        label: 'Engine RPM (/10)',
                        data: rpms,
                        borderColor: '#f59e0b',
                        backgroundColor: 'transparent',
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af' }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#9ca3af' } },
                    tooltip: {
                        backgroundColor: '#1f2937',
                        borderColor: '#374151',
                        borderWidth: 1
                    }
                }
            }
        });
    }
}

window.FleetCharts = FleetCharts;
