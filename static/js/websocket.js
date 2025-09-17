// WebSocket Manager for real-time market data
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 5000;
        this.subscriptions = new Set();
        this.isConnected = false;
        this.messageHandlers = new Map();
    }

    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return;
        }

        const token = localStorage.getItem('access_token');
        if (!token) {
            console.warn('No access token found, cannot connect to WebSocket');
            return;
        }

        const wsUrl = `${WS_BASE_URL}/ws/market-data?token=${token}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
            
            // Resubscribe to previous subscriptions
            this.subscriptions.forEach(symbol => {
                this.subscribe(symbol);
            });
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        this.updateConnectionStatus(false);
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.error('Max reconnection attempts reached');
            showNotification('Conexión perdida con el servidor', 'error');
        }
    }

    subscribe(symbol) {
        this.subscriptions.add(symbol);
        
        if (this.isConnected) {
            this.send({
                type: 'subscribe',
                symbol: symbol
            });
        }
    }

    unsubscribe(symbol) {
        this.subscriptions.delete(symbol);
        
        if (this.isConnected) {
            this.send({
                type: 'unsubscribe',
                symbol: symbol
            });
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    handleMessage(data) {
        const { type, symbol, ...payload } = data;
        
        // Emit global events for reactive UI updates
        window.dispatchEvent(new CustomEvent('ws:message', {
            detail: { type, symbol, ...payload }
        }));
        
        // Emit specific events for different message types
        window.dispatchEvent(new CustomEvent(`ws:${type}`, {
            detail: { symbol, ...payload }
        }));
        
        switch (type) {
            case 'price_update':
                this.handlePriceUpdate(symbol, payload);
                break;
            case 'alert_triggered':
                this.handleAlert(payload);
                break;
            case 'market_data':
                this.handleMarketData(symbol, payload);
                break;
            case 'portfolio_update':
                this.handlePortfolioUpdate(payload);
                break;
            case 'transaction_update':
                this.handleTransactionUpdate(payload);
                break;
            default:
                console.log('Unknown message type:', type);
        }
    }

    handlePriceUpdate(symbol, data) {
        // Update market data in UI
        const marketItem = document.querySelector(`[data-symbol="${symbol}"]`);
        if (marketItem) {
            const priceElement = marketItem.querySelector('.price-value');
            const changeElement = marketItem.querySelector('.price-change');
            
            if (priceElement) {
                priceElement.textContent = formatCurrency(data.price);
            }
            
            if (changeElement && data.change !== undefined) {
                changeElement.textContent = formatPercentage(data.change);
                changeElement.className = `price-change ${data.change >= 0 ? 'positive' : 'negative'}`;
            }
        }
        
        // Trigger custom event for other components
        window.dispatchEvent(new CustomEvent('priceUpdate', {
            detail: { symbol, ...data }
        }));
    }

    handleAlert(data) {
        showNotification(
            `${data.symbol}: ${data.message}`,
            'warning',
            'Alerta de Precio'
        );
        
        // Play notification sound if available
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('MyCrypto - Alerta de Precio', {
                body: `${data.symbol}: ${data.message}`,
                icon: '/static/favicon.ico'
            });
        }
    }

    handleMarketData(symbol, data) {
        // Update comprehensive market data
        window.dispatchEvent(new CustomEvent('marketDataUpdate', {
            detail: { symbol, ...data }
        }));
    }

    handlePortfolioUpdate(data) {
        // Emit portfolio update event for reactive UI
        window.dispatchEvent(new CustomEvent('portfolio:updated', {
            detail: data
        }));
    }

    handleTransactionUpdate(data) {
        // Emit transaction update event for reactive UI
        window.dispatchEvent(new CustomEvent('transaction:updated', {
            detail: data
        }));
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('ws-status');
        if (statusElement) {
            if (connected) {
                statusElement.className = 'status-indicator online';
                statusElement.innerHTML = '<i class="fas fa-circle"></i> Conectado';
            } else {
                statusElement.className = 'status-indicator offline';
                statusElement.innerHTML = '<i class="fas fa-circle"></i> Desconectado';
            }
        }
        
        // Emit connection status change event
        window.dispatchEvent(new CustomEvent('ws:connection', {
            detail: { connected }
        }));
    }

    // Add method to emit custom events for state management
    emitStateChange(eventType, data) {
        window.dispatchEvent(new CustomEvent(eventType, {
            detail: data
        }));
    }

    // Request state updates from server
    requestUpdate(type, params = {}) {
        this.send({
            type: 'request_update',
            update_type: type,
            params
        });
    }
}

// Global WebSocket manager instance
const wsManager = new WebSocketManager();

// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

// Auto-connect when authenticated
document.addEventListener('DOMContentLoaded', () => {
    if (isAuthenticated()) {
        wsManager.connect();
    }
});

// Disconnect on page unload
window.addEventListener('beforeunload', () => {
    wsManager.disconnect();
});
