document.addEventListener('DOMContentLoaded', function() {
    // Performance Chart
    const ctx = document.getElementById('performanceChart').getContext('2d');
    const performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Will be populated with dates
            datasets: [
                {
                    label: 'Opens',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                },
                {
                    label: 'Clicks',
                    data: [],
                    borderColor: 'rgb(153, 102, 255)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Campaign Performance Over Time'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Function to update chart data
    function updateChartData(campaignId) {
        fetch(`/campaigns/analytics/${campaignId}/data/`)
            .then(response => response.json())
            .then(data => {
                const timelineData = data.timeline_data;
                const dates = [...new Set(timelineData.map(item => item.timestamp__date))];
                
                performanceChart.data.labels = dates;
                performanceChart.data.datasets[0].data = dates.map(date => {
                    const openEvent = timelineData.find(item => 
                        item.timestamp__date === date && item.event_type === 'opened'
                    );
                    return openEvent ? openEvent.count : 0;
                });
                performanceChart.data.datasets[1].data = dates.map(date => {
                    const clickEvent = timelineData.find(item => 
                        item.timestamp__date === date && item.event_type === 'clicked'
                    );
                    return clickEvent ? clickEvent.count : 0;
                });
                
                performanceChart.update();
            });
    }

    // Update chart data initially and set up refresh interval
    if (currentCampaignId) {
        updateChartData(currentCampaignId);
        setInterval(() => updateChartData(currentCampaignId), 300000); // Refresh every 5 minutes
    }
}); 