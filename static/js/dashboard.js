// Initialize tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});

// Fetch and update dashboard stats
function updateDashboardStats() {
    fetch('/api/dashboard/stats/')
        .then(response => response.json())
        .then(data => {
            // Update stats cards
            document.getElementById('activeCampaigns').textContent = data.active_campaigns;
            document.getElementById('totalProspects').textContent = data.total_prospects;
            document.getElementById('openRate').textContent = data.open_rate + '%';
            document.getElementById('responseRate').textContent = data.response_rate + '%';
        })
        .catch(error => console.error('Error:', error));
}

// Initialize charts if they exist on the page
if (document.getElementById('campaignChart')) {
    const ctx = document.getElementById('campaignChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Will be populated with dates
            datasets: [{
                label: 'Opens',
                data: [], // Will be populated with open rates
                borderColor: '#34D399',
                tension: 0.4
            }, {
                label: 'Responses',
                data: [], // Will be populated with response rates
                borderColor: '#60A5FA',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Update stats every 5 minutes
setInterval(updateDashboardStats, 300000); 