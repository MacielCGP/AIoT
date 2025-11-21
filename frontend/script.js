document.addEventListener('DOMContentLoaded', () => {
    const socket = io('http://192.168.2.133:5000');
    const MAX_DATA_POINTS = 150;

    // --- Elementos da UI ---
    const motorIdEl = document.getElementById('motor-id');
    const timestampEl = document.getElementById('timestamp');
    const overallStatusEl = document.getElementById('overall-status');
    const statusIndicatorCircle = document.getElementById('status-indicator-circle');
    const alertContainer = document.getElementById('alert-container');

    // --- Configuração Padrão dos Gráficos para Tema Escuro ---
    const chartDefaultOptions = {
        responsive: true, maintainAspectRatio: false,
        animation: false,
        scales: {
            x: {
                ticks: { display: false },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
            },
            y: {
                beginAtZero: false,
                ticks: { color: '#e0e0e0' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
            }
        },
        plugins: {
            legend: {
                labels: { color: '#e0e0e0' }
            }
        }
    };

    // --- Funções Auxiliares de Gráfico ---
    function createChart(chartId, label, borderColor, bgColor) {
        const ctx = document.getElementById(chartId).getContext('2d');
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: label,
                    data: [],
                    borderColor: borderColor,
                    backgroundColor: bgColor,
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                }]
            },
            options: chartDefaultOptions
        });
    }

    function addDataToChart(chart, label, data) {
        if (chart.data.labels.length >= MAX_DATA_POINTS) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(data);
    }

    // --- Inicialização dos Gráficos ---
    const correnteChart = createChart('corrente-chart', 'Corrente (A)', '#00aaff', 'rgba(0, 170, 255, 0.1)');
    const vibracaoChart = createChart('vibracao-chart', 'Vibração (mm/s)', '#ffc107', 'rgba(255, 193, 7, 0.1)');

    // --- Funções de Atualização da UI ---
    function updateComponentCard(statusElId, statusText) {
        const statusEl = document.getElementById(statusElId);
        statusEl.innerText = statusText;
        
        statusEl.className = 'status-indicator-span'; // Reset class
        if (statusText.includes('Incipiente')) {
            statusEl.classList.add('status-warning');
        } else if (statusText.includes('Desenvolvida')) {
            statusEl.classList.add('status-fault');
        } else {
            statusEl.classList.add('status-healthy');
        }
    }

    function updateHealthData(data) {
        const now = data.timestamp ? new Date(data.timestamp) : new Date();
        
        motorIdEl.innerText = data.motor_id || '--';
        timestampEl.innerText = now.toLocaleString('pt-BR');

        if (data.overall_status) {
            overallStatusEl.innerText = data.overall_status;
            
            const statusKey = data.overall_status;
            const statusMap = {
                'Saudável': 'healthy',
                'Atenção': 'warning',
                'Falha': 'fault'
            };
            const statusType = statusMap[statusKey] || 'nodata';

            // Atualiza a cor do círculo
            statusIndicatorCircle.className = `status-${statusType}`;
            
            // Reseta classes de cor do texto e adiciona a nova
            overallStatusEl.classList.remove('text-healthy', 'text-warning', 'text-fault', 'text-nodata');
            overallStatusEl.classList.add(`text-${statusType}`);
        }

        const indicators = data.health_indicators;
        if (indicators) {
            if (indicators.rolling_bearing) {
                document.getElementById('gamma-value').innerText = `${indicators.rolling_bearing.gamma_degradation_percent}%`;
                updateComponentCard('bearing-status', indicators.rolling_bearing.status);
            }
            if (indicators.stator_winding) {
                document.getElementById('alpha-value').innerText = `${indicators.stator_winding.alpha_degradation_percent}%`;
                updateComponentCard('stator-status', indicators.stator_winding.status);
            }
            if (indicators.rotor_bars) {
                document.getElementById('rotor-value').innerText = indicators.rotor_bars.broken_bars_count;
                updateComponentCard('rotor-status', indicators.rotor_bars.status);
            }
        }
    }

    // --- Otimização de Gráfico com requestAnimationFrame ---
    const sensorDataQueue = [];
    let isUpdateScheduled = false;

    function processQueue() {
        if (sensorDataQueue.length === 0) {
            isUpdateScheduled = false;
            return;
        }

        const dataToProcess = [...sensorDataQueue];
        sensorDataQueue.length = 0;

        dataToProcess.forEach(data => {
            const now = data.timestamp ? new Date(data.timestamp) : new Date();
            const chartTimestamp = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

            if (data.corrente !== undefined) {
                addDataToChart(correnteChart, chartTimestamp, data.corrente);
            }
            if (data.vibracao !== undefined) {
                addDataToChart(vibracaoChart, chartTimestamp, data.vibracao);
            }
        });

        if (dataToProcess.length > 0) {
            correnteChart.update('none');
            vibracaoChart.update('none');
        }

        requestAnimationFrame(processQueue);
    }

    function scheduleUpdate(data) {
        sensorDataQueue.push(data);
        if (!isUpdateScheduled) {
            isUpdateScheduled = true;
            requestAnimationFrame(processQueue);
        }
    }

    // --- Lógica de Alertas ---
    function showAlert(alert) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${alert.type.toLowerCase()}`;
        alertDiv.textContent = alert.message;

        alertContainer.appendChild(alertDiv);

        // Animação de entrada
        setTimeout(() => {
            alertDiv.classList.add('show');
        }, 100);

        // Animação de saída
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 500);
        }, 5000);
    }

    // --- Lógica do WebSocket ---
    socket.on('connect', () => console.log('Conectado ao servidor WebSocket!'));
    socket.on('disconnect', () => console.log('Desconectado do servidor WebSocket.'));

    socket.on('health_update', (data) => {
        updateHealthData(data);
        scheduleUpdate(data);
    });

    socket.on('sensor_update', (data) => {
        scheduleUpdate(data);
    });

    socket.on('health_alert', (alert) => {
        showAlert(alert);
    });
});
