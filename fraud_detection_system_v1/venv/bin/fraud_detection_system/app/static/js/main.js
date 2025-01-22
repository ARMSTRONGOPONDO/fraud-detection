document.addEventListener('DOMContentLoaded', () => {
    // Initialize WebSocket connection
    const socket = io('http://127.0.0.1:5000'); // Ensure this matches Flask-SocketIO server address

    const transactionFeed = document.getElementById('transaction-feed');
    const startConsumerButton = document.getElementById('start-consumer');
    const stopConsumerButton = document.getElementById('stop-consumer');

    // Handle WebSocket events
    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });

    socket.on('transaction_update', (data) => {
        console.log('Received transaction update:', data); // This should log the data received from the backend
        if (data.user_id && data.amount && data.type) {
            const transaction = document.createElement('div');
            transaction.className = 'transaction';
            transaction.textContent = `User ${data.user_id} made a ${data.type} transaction of $${data.amount}`;
            transactionFeed.appendChild(transaction);
        } else {
            console.warn('Invalid transaction data received:', data);
        }
    });
    

    // Handle Kafka consumer start
    startConsumerButton.addEventListener('click', () => {
        fetch('/kafka/start_consumer', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log('Start Consumer Response:', data);
                alert(data.message); // Show success message
            })
            .catch(error => {
                console.error('Error starting Kafka consumer:', error);
                alert('Error starting Kafka consumer');
            });
    });

    // Handle Kafka consumer stop
    stopConsumerButton.addEventListener('click', () => {
        fetch('/kafka/stop_consumer', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log('Stop Consumer Response:', data);
                alert(data.message); // Show success message
            })
            .catch(error => {
                console.error('Error stopping Kafka consumer:', error);
                alert('Error stopping Kafka consumer');
            });
    });
});
