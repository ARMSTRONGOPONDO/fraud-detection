document.addEventListener('DOMContentLoaded', () => {
    const socket = io('http://127.0.0.1:5000');
    const userQueryForm = document.getElementById("user-query-form");
    const transactionFeed = document.getElementById("transaction-feed");
    const fraudChartCtx = document.getElementById("fraudChart").getContext("2d");
    const startConsumerButton = document.getElementById('start-consumer');
    const stopConsumerButton = document.getElementById('stop-consumer');
    const userLocationForm = document.getElementById("user-location-form");

    let currentUserId = null;
    const transactions = [];
    let currentUserLocation = null;
    let customTimeStart = null;
    let customTimeEnd = null;
    let dailyTransactionLimit = null;
    let largeTransactionAmount = null;


    userLocationForm.addEventListener("submit", function (event) {
        event.preventDefault();
        currentUserId = parseInt(document.getElementById("userId").value);
        currentUserLocation = document.getElementById("userLocation").value;
        customTimeStart = document.getElementById("customTimeStart").value;
        customTimeEnd = document.getElementById("customTimeEnd").value;
        dailyTransactionLimit = parseInt(document.getElementById("dailyTransactionLimit").value);
        largeTransactionAmount = parseFloat(document.getElementById("largeTransactionAmount").value);
        renderTransactions();
    });


    // WebSocket events
    socket.on('connect', () => console.log('Connected to server'));
    socket.on('disconnect', () => console.log('Disconnected from server'));

    // Fetch and render transactions based on User ID
    userQueryForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        currentUserId = parseInt(document.getElementById("query-user-id").value);

        if (!isNaN(currentUserId)) {
            try {
                const response = await fetch(`/api/get_transactions?user_id=${currentUserId}`);
                if (!response.ok) throw new Error(`Error fetching transactions: ${response.statusText}`);

                const transactions = await response.json();
                renderTransactions(transactions.flagged_transactions);
            } catch (error) {
                console.error("Error fetching transactions:", error);
                alert("transactions fetched succefully.");
            }
        } else {
            alert("Please enter a valid User ID.");
        }
    });

    // Render transactions to the transaction feed
    function renderTransactions(transactions) {
        transactionFeed.innerHTML = ""; // Clear existing transactions
    
        if (!transactions || transactions.length === 0) {
            transactionFeed.innerHTML = "<li class='list-group-item'>No transactions found for this user.</li>";
            return;
        }
    
        let normalCount = 0;
        let fraudCount = 0;
    
        transactions.forEach((txn) => {
            const listItem = document.createElement("li");
            listItem.className = "list-group-item";
    
            // Access nested properties
            const transaction = txn.transaction;
            const ruleTriggered = txn.rule_triggered;
    
            const amount = transaction.amount.toFixed(2);
            const location = transaction.location;
            const flaggedAt = new Date(txn.flagged_at).toLocaleString();
            const transactionType = transaction.type;
    
            listItem.innerHTML = `
                <b>Transaction ID:</b> ${txn.id}<br>
                <b>User:</b> ${txn.user_id} | <b>Location:</b> ${location}<br>
                <b>Type:</b> ${transactionType} | <b>Amount:</b> $${amount}<br>
                <b>Flagged At:</b> ${flaggedAt}<br>
                <b>Rule Triggered:</b> ${ruleTriggered.type} (Threshold: ${ruleTriggered.threshold}, Max Transactions: ${ruleTriggered.max_transactions})
            `;
    
            // Adding fraud/normal badge
            const isFraud = ruleTriggered.type === "custom_rule"; // Customize as needed
            listItem.innerHTML += isFraud
                ? `<span class='badge bg-danger'>Fraud</span>`
                : `<span class='badge bg-success'>Normal</span>`;
    
            isFraud ? fraudCount++ : normalCount++;
            transactionFeed.appendChild(listItem);
        });
    
        // Update all charts
        updateFraudChart(normalCount, fraudCount);
        updateTransactionTypeChart(transactions);
        updateTransactionFrequencyChart(transactions);
    }
    (() => {
        const transactionTypeCtx = document.getElementById("transactionTypeChart").getContext("2d");
    
        const transactionTypeChart = new Chart(transactionTypeCtx, {
            type: "bar",
            data: {
                labels: [], // Placeholder for transaction types
                datasets: [{
                    label: "Transaction Type Breakdown",
                    data: [], // Placeholder for transaction counts
                    backgroundColor: ["#2196f3", "#ff9800", "#9c27b0", "#3f51b5"],
                }],
            },
            options: {
                responsive: true,
                plugins: { legend: { position: "top" } },
            },
        });
    
        function updateTransactionTypeChart(transactions) {
            const typeCounts = {};
            transactions.forEach((txn) => {
                const type = txn.transaction.type;
                typeCounts[type] = (typeCounts[type] || 0) + 1;
            });
    
            // Update chart data
            transactionTypeChart.data.labels = Object.keys(typeCounts);
            transactionTypeChart.data.datasets[0].data = Object.values(typeCounts);
            transactionTypeChart.update();
        }
    
        // Expose the updateTransactionTypeChart function globally
        window.updateTransactionTypeChart = updateTransactionTypeChart;
    })();
    
    (() => {
        const transactionFrequencyCtx = document.getElementById("transactionFrequencyChart").getContext("2d");
    
        const transactionFrequencyChart = new Chart(transactionFrequencyCtx, {
            type: "line",
            data: {
                labels: [], // Placeholder for timestamps
                datasets: [{
                    label: "Transaction Frequency",
                    data: [], // Placeholder for transaction counts
                    borderColor: "#4caf50",
                    fill: false,
                }],
            },
            options: {
                responsive: true,
                plugins: { legend: { position: "top" } },
                scales: {
                    x: { title: { display: true, text: "Time" } },
                    y: { title: { display: true, text: "Number of Transactions" } },
                },
            },
        });
    
        function updateTransactionFrequencyChart(transactions) {
            const frequencyCounts = {};
    
            transactions.forEach((txn) => {
                const date = new Date(txn.transaction.timestamp).toLocaleDateString();
                frequencyCounts[date] = (frequencyCounts[date] || 0) + 1;
            });
    
            // Update chart data
            transactionFrequencyChart.data.labels = Object.keys(frequencyCounts);
            transactionFrequencyChart.data.datasets[0].data = Object.values(frequencyCounts);
            transactionFrequencyChart.update();
        }
    
        // Expose the updateTransactionFrequencyChart function globally
        window.updateTransactionFrequencyChart = updateTransactionFrequencyChart;
    })();
    

    // Update the fraud chart
    (() => {
        const fraudChartCtx = document.getElementById("fraudChart").getContext("2d");

        const fraudChart = new Chart(fraudChartCtx, {
            type: "bar",
            data: {
                labels: ["Normal", "Fraud"],
                datasets: [{
                    label: "Transaction Status",
                    data: [0, 0],
                    backgroundColor: ["#4caf50", "#f44336"],
                }],
            },
            options: {
                responsive: true,
                plugins: { legend: { position: "top" } },
            },
        });

        function updateFraudChart(normalCount, fraudCount) {
            fraudChart.data.datasets[0].data = [normalCount, fraudCount];
            fraudChart.update();
        }

        // Expose the updateFraudChart function globally
        window.updateFraudChart = updateFraudChart;
    })();




    // Kafka Consumer Control Buttons
    startConsumerButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/kafka/start_consumer', { method: 'POST' });
            const data = await response.json();
            alert(data.message);
        } catch (error) {
            console.error('Error starting Kafka consumer:', error);
            alert('Error starting Kafka consumer');
        }
    });

    stopConsumerButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/kafka/stop_consumer', { method: 'POST' });
            const data = await response.json();
            alert(data.message);
        } catch (error) {
            console.error('Error stopping Kafka consumer:', error);
            alert('Error stopping Kafka consumer');
        }
    });

    document.getElementById('user-location-form').addEventListener('submit', function (event) {
        event.preventDefault();
    
        const ruleData = {
            userId: parseInt(document.getElementById('userId').value), // Convert to integer
            userLocation: document.getElementById('userLocation').value,
            customTimeStart: document.getElementById('customTimeStart').value,
            customTimeEnd: document.getElementById('customTimeEnd').value,
            dailyTransactionLimit: parseInt(document.getElementById('dailyTransactionLimit').value), // Convert to integer
            largeTransactionAmount: parseFloat(document.getElementById('largeTransactionAmount').value) // Convert to float
        };
    
        fetch('/api/set_user_rules', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(ruleData),
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message || 'Rules saved successfully!');
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });


});
