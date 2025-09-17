// API Configuration
const API_BASE_URL = window.location.origin;
const WS_BASE_URL = window.location.origin.replace('http', 'ws');

// API Client Class
class APIClient {
    constructor() {
        this.token = localStorage.getItem('access_token');
    }

    // Get headers with authentication
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    // Generic API request method
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                // Token expired, try to refresh
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Retry the original request
                    config.headers = this.getHeaders();
                    const retryResponse = await fetch(url, config);
                    return await this.handleResponse(retryResponse);
                } else {
                    // Refresh failed, redirect to login
                    this.logout();
                    return null;
                }
            }
            
            return await this.handleResponse(response);
        } catch (error) {
            console.error('API request failed:', error);
            showNotification('Error de conexión', 'error');
            throw error;
        }
    }

    // Handle API response
    async handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
    }

    // Authentication methods
    async login(email, password) {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        if (response.ok) {
            const data = await response.json();
            this.token = data.access_token;
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            
            // Get user profile after login
            const userProfile = await this.getUserProfile();
            localStorage.setItem('user_info', JSON.stringify(userProfile));
            
            return { ...data, user: userProfile };
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error de autenticación');
        }
    }

    async register(userData) {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: userData.email,
                name: userData.username,
                password: userData.password
            })
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Error en el registro');
        }
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access_token;
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }

        return false;
    }

    // Get user profile
    async getUserProfile() {
        return await this.request('/auth/profile');
    }

    logout() {
        this.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_info');
        window.location.href = '/login';
    }

    // Portfolio methods
    async getPortfolios() {
        return await this.request('/portfolios/');
    }

    async createPortfolio(portfolioData) {
        return await this.request('/portfolios/', {
            method: 'POST',
            body: JSON.stringify(portfolioData)
        });
    }

    async getPortfolioDetails(portfolioId) {
        return await this.request(`/portfolios/${portfolioId}/details`);
    }

    // Transaction methods
    async getTransactions(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/transactions/?${params}`);
    }

    async createBuyTransaction(transactionData) {
        return await this.request('/transactions/buy', {
            method: 'POST',
            body: JSON.stringify(transactionData)
        });
    }

    async createSellTransaction(transactionData) {
        return await this.request('/transactions/sell', {
            method: 'POST',
            body: JSON.stringify(transactionData)
        });
    }

    async executeTransaction(transactionId) {
        return await this.request(`/transactions/execute`, {
            method: 'POST',
            body: JSON.stringify({ transaction_id: transactionId })
        });
    }

    // Market data methods
    async getMarketData() {
        return await this.request('/bitso/market-overview');
    }

    async getTicker(symbol) {
        return await this.request(`/bitso/ticker/${symbol}`);
    }

    // Crypto assets methods
    async getCryptoAssets() {
        return await this.request('/crypto-assets/');
    }

    // Alerts methods
    async getAlerts() {
        return await this.request('/ws/alerts');
    }

    async createAlert(alertData) {
        return await this.request('/ws/alerts/price', {
            method: 'POST',
            body: JSON.stringify(alertData)
        });
    }

    async deleteAlert(alertId) {
        return await this.request(`/ws/alerts/${alertId}`, {
            method: 'DELETE'
        });
    }
}

// Global API client instance
const api = new APIClient();

// Utility functions
function showNotification(message, type = 'info', title = '') {
    const container = document.getElementById('notifications');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };

    notification.innerHTML = `
        <i class="${iconMap[type] || iconMap.info}"></i>
        <div class="notification-content">
            ${title ? `<div class="notification-title">${title}</div>` : ''}
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Format currency
function formatCurrency(amount, currency = 'MXN') {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Format percentage
function formatPercentage(value) {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
}

// Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Check if user is authenticated
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

// Get current user info
function getCurrentUser() {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
}
