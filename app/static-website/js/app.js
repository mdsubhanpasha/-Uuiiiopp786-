document.addEventListener('DOMContentLoaded', () => {
    fetchHealthTelemetry();
    setInterval(fetchHealthTelemetry, 15000);
});

async function fetchHealthTelemetry() {
    const startTime = performance.now();
    try {
        const response = await fetch('/health');
        const endTime = performance.now();
        const duration = (endTime - startTime).toFixed(1);

        if (response.ok) {
            const data = await response.json();
            document.getElementById('metric-status').textContent = data.status || 'UP';
            document.getElementById('metric-latency').textContent = `${duration}ms`;
            document.getElementById('health-json-output').textContent = JSON.stringify(data, null, 2);
        } else {
            document.getElementById('metric-status').textContent = 'DEGRADED';
            document.getElementById('metric-status').className = 'metric-value yellow-text';
        }
    } catch (error) {
        console.warn('Health telemetry check failed, displaying mock edge response:', error);
        // Fallback for direct static viewer
        const mockDuration = (Math.random() * 2 + 0.8).toFixed(1);
        document.getElementById('metric-status').textContent = 'UP (MOCK)';
        document.getElementById('metric-latency').textContent = `${mockDuration}ms`;
    }
}
