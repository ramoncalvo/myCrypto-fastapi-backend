// Dashboard JavaScript functionality

// Global state
let currentSection = 'dashboard';
let portfolios = [];
let transactions = [];
let marketData = [];
let alerts = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async function() {
    // Check authentication
    if (!isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    // Set user info
    const user = getCurrentUser();
    if (user) {
        document.getElementById('username').textContent = user.username || user.email;
    }

    // Initialize navigation
    initializeNavigation();
    
    // Initialize WebSocket event listeners for reactive UI
    initializeWebSocketReactivity();
    
    // Load initial data
    await loadDashboardData();
    
    // Initialize modals
    initializeModals();
    
    // Connect WebSocket
    wsManager.connect();
    
    // Subscribe to common crypto pairs
    const commonPairs = ['btc_mxn', 'eth_mxn', 'xrp_mxn', 'ltc_mxn'];
    commonPairs.forEach(pair => wsManager.subscribe(pair));
});

// Initialize WebSocket-based reactive UI updates
function initializeWebSocketReactivity() {
    // Listen for portfolio updates
    window.addEventListener('portfolio:updated', (event) => {
        const portfolioData = event.detail;
        updatePortfolioSummary(portfolioData);
        if (currentSection === 'portfolio') {
            loadPortfolioData();
        }
    });

    // Listen for transaction updates
    window.addEventListener('transaction:updated', (event) => {
        const transactionData = event.detail;
        updateRecentTransactions(transactionData);
        if (currentSection === 'transactions') {
            loadTransactionData();
        }
    });

    // Listen for price updates
    window.addEventListener('ws:price_update', (event) => {
        const { symbol, ...data } = event.detail;
        updateMarketPrices(symbol, data);
    });

    // Listen for market data updates
    window.addEventListener('marketDataUpdate', (event) => {
        const { symbol, ...data } = event.detail;
        updateMarketData(symbol, data);
    });

    // Listen for connection status changes
    window.addEventListener('ws:connection', (event) => {
        const { connected } = event.detail;
        handleConnectionChange(connected);
    });

    // Listen for alert triggers
    window.addEventListener('ws:alert_triggered', (event) => {
        const alertData = event.detail;
        handleAlertTriggered(alertData);
    });
}

// Navigation handling
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            showSection(section);
        });
    });
}

function showSection(sectionName) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${sectionName}-section`).classList.add('active');
    
    currentSection = sectionName;
    
    // Load section-specific data
    loadSectionData(sectionName);
}

async function loadSectionData(section) {
    switch (section) {
        case 'dashboard':
            await loadDashboardData();
            break;
        case 'portfolio':
            await loadPortfolioData();
            break;
        case 'transactions':
            await loadTransactionData();
            break;
        case 'market':
            await loadMarketData();
            break;
        case 'alerts':
            await loadAlertsData();
            break;
    }
}

// Dashboard data loading
async function loadDashboardData() {
    try {
        // Load portfolio summary
        await loadPortfolioSummary();
        
        // Load recent transactions
        await loadRecentTransactions();
        
        // Load market overview
        await loadMarketOverview();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error cargando datos del dashboard', 'error');
    }
}

async function loadPortfolioSummary() {
    try {
        const portfoliosData = await api.getPortfolios();
        portfolios = portfoliosData;
        
        let totalValue = 0;
        let totalAssets = 0;
        
        portfolios.forEach(portfolio => {
            totalValue += portfolio.total_value || 0;
            totalAssets += portfolio.holdings?.length || 0;
        });
        
        document.getElementById('total-value').textContent = formatCurrency(totalValue);
        document.getElementById('total-assets').textContent = totalAssets;
        document.getElementById('daily-change').textContent = '$0.00 (0%)'; // TODO: Calculate from real data
        
    } catch (error) {
        console.error('Error loading portfolio summary:', error);
    }
}

async function loadRecentTransactions() {
    try {
        const transactionsData = await api.getTransactions({ limit: 5 });
        const container = document.getElementById('recent-transactions');
        
        if (transactionsData.length === 0) {
            container.innerHTML = '<div class="no-data">No hay transacciones recientes</div>';
            return;
        }
        
        container.innerHTML = transactionsData.map(transaction => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-icon ${transaction.type}">
                        <i class="fas fa-${transaction.type === 'buy' ? 'plus' : 'minus'}"></i>
                    </div>
                    <div class="transaction-details">
                        <h4>${transaction.type === 'buy' ? 'Compra' : 'Venta'} ${transaction.symbol}</h4>
                        <p>${formatDate(transaction.created_at)}</p>
                    </div>
                </div>
                <div class="transaction-amount">
                    ${formatCurrency(transaction.amount * transaction.price)}
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading recent transactions:', error);
        document.getElementById('recent-transactions').innerHTML = 
            '<div class="error">Error cargando transacciones</div>';
    }
}

async function loadMarketOverview() {
    try {
        const data = await api.getMarketData();
        const container = document.getElementById('market-data');
        
        if (!data || data.length === 0) {
            container.innerHTML = '<div class="no-data">No hay datos de mercado disponibles</div>';
            return;
        }
        
        container.innerHTML = data.slice(0, 6).map(item => `
            <div class="market-item" data-symbol="${item.book}">
                <div class="market-symbol">${item.book.toUpperCase()}</div>
                <div class="market-price">
                    <div class="price-value">${formatCurrency(parseFloat(item.last))}</div>
                    <div class="price-change ${parseFloat(item.change_24) >= 0 ? 'positive' : 'negative'}">
                        ${formatPercentage(parseFloat(item.change_24))}
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading market overview:', error);
        document.getElementById('market-data').innerHTML = 
            '<div class="error">Error cargando datos del mercado</div>';
    }
}

// Portfolio data loading
async function loadPortfolioData() {
    try {
        const portfoliosData = await api.getPortfolios();
        const container = document.getElementById('portfolio-content');
        
        if (portfoliosData.length === 0) {
            container.innerHTML = `
                <div class="no-data">
                    <h3>No tienes portfolios aún</h3>
                    <p>Crea tu primer portfolio para comenzar a gestionar tus inversiones</p>
                    <button class="btn-primary" onclick="createPortfolio()">
                        <i class="fas fa-plus"></i> Crear Portfolio
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = portfoliosData.map(portfolio => `
            <div class="portfolio-card">
                <div class="portfolio-header">
                    <div class="portfolio-name">${portfolio.name}</div>
                    <div class="portfolio-value">${formatCurrency(portfolio.total_value || 0)}</div>
                </div>
                <div class="portfolio-stats">
                    <div class="stat-item">
                        <div class="stat-label">Activos</div>
                        <div class="stat-value">${portfolio.holdings?.length || 0}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Rendimiento</div>
                        <div class="stat-value">+0.00%</div>
                    </div>
                </div>
                <div class="portfolio-actions">
                    <button class="btn-primary" onclick="viewPortfolio('${portfolio.id}')">
                        Ver Detalles
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading portfolio data:', error);
        showNotification('Error cargando portfolios', 'error');
    }
}

// Transaction data loading
async function loadTransactionData() {
    try {
        const transactionsData = await api.getTransactions();
        const container = document.getElementById('transactions-content');
        
        if (transactionsData.length === 0) {
            container.innerHTML = '<div class="no-data">No hay transacciones</div>';
            return;
        }
        
        container.innerHTML = `
            <div class="table-content">
                ${transactionsData.map(transaction => `
                    <div class="table-row">
                        <div><strong>${transaction.symbol}</strong></div>
                        <div>${transaction.type === 'buy' ? 'Compra' : 'Venta'}</div>
                        <div>${transaction.amount}</div>
                        <div>${formatCurrency(transaction.price)}</div>
                        <div>${formatDate(transaction.created_at)}</div>
                        <div>
                            <span class="status-badge ${transaction.status}">
                                ${transaction.status}
                            </span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading transaction data:', error);
        showNotification('Error cargando transacciones', 'error');
    }
}

// Market data loading
async function loadMarketData() {
    try {
        const data = await api.getMarketData();
        const container = document.getElementById('market-content');
        
        container.innerHTML = data.map(item => `
            <div class="market-card" data-symbol="${item.book}">
                <div class="market-card-header">
                    <div class="market-card-symbol">${item.book.toUpperCase()}</div>
                    <button class="btn-secondary" onclick="wsManager.subscribe('${item.book}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
                <div class="market-card-price">${formatCurrency(parseFloat(item.last))}</div>
                <div class="market-card-change ${parseFloat(item.change_24) >= 0 ? 'positive' : 'negative'}">
                    ${formatPercentage(parseFloat(item.change_24))}
                </div>
                <div class="market-card-volume">
                    Vol: ${parseFloat(item.volume).toLocaleString()}
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading market data:', error);
        showNotification('Error cargando datos del mercado', 'error');
    }
}

// Alerts data loading
async function loadAlertsData() {
    try {
        const alertsData = await api.getAlerts();
        const container = document.getElementById('alerts-content');
        
        if (alertsData.length === 0) {
            container.innerHTML = `
                <div class="no-data">
                    <h3>No tienes alertas configuradas</h3>
                    <p>Crea alertas para recibir notificaciones cuando los precios cambien</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = alertsData.map(alert => `
            <div class="alert-card">
                <div class="alert-header">
                    <div class="alert-symbol">${alert.symbol}</div>
                    <button class="alert-delete" onclick="deleteAlert('${alert.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="alert-condition">${alert.condition}</div>
                <div class="alert-value">${formatCurrency(alert.target_price)}</div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading alerts data:', error);
        showNotification('Error cargando alertas', 'error');
    }
}

// Modal functions
function initializeModals() {
    // Close modals when clicking outside
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
    
    // Load crypto assets for dropdowns
    loadCryptoAssets();
    loadPortfolioOptions();
}

async function loadCryptoAssets() {
    try {
        const assets = await api.getCryptoAssets();
        const selects = document.querySelectorAll('#buy-symbol, #sell-symbol, #alert-symbol');
        
        selects.forEach(select => {
            select.innerHTML = '<option value="">Seleccionar...</option>' +
                assets.map(asset => `<option value="${asset.symbol}">${asset.name} (${asset.symbol})</option>`).join('');
        });
    } catch (error) {
        console.error('Error loading crypto assets:', error);
    }
}

async function loadPortfolioOptions() {
    try {
        const portfoliosData = await api.getPortfolios();
        const selects = document.querySelectorAll('#buy-portfolio, #sell-portfolio');
        
        selects.forEach(select => {
            select.innerHTML = '<option value="">Seleccionar...</option>' +
                portfoliosData.map(portfolio => `<option value="${portfolio.id}">${portfolio.name}</option>`).join('');
        });
    } catch (error) {
        console.error('Error loading portfolios:', error);
    }
}

// Modal show/hide functions
function showBuyModal() {
    document.getElementById('buy-modal').style.display = 'flex';
}

function closeBuyModal() {
    document.getElementById('buy-modal').style.display = 'none';
}

function showSellModal() {
    document.getElementById('sell-modal').style.display = 'flex';
}

function closeSellModal() {
    document.getElementById('sell-modal').style.display = 'none';
}

function showAlertModal() {
    document.getElementById('alert-modal').style.display = 'flex';
}

function closeAlertModal() {
    document.getElementById('alert-modal').style.display = 'none';
}

// Transaction functions
document.getElementById('buy-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const transactionData = {
        symbol: formData.get('symbol'),
        amount: parseFloat(formData.get('amount')),
        price: parseFloat(formData.get('price')),
        portfolio_id: formData.get('portfolio')
    };
    
    try {
        await api.createBuyTransaction(transactionData);
        showNotification('Orden de compra creada exitosamente', 'success');
        closeBuyModal();
        loadDashboardData();
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

document.getElementById('sell-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const transactionData = {
        symbol: formData.get('symbol'),
        amount: parseFloat(formData.get('amount')),
        price: parseFloat(formData.get('price')),
        portfolio_id: formData.get('portfolio')
    };
    
    try {
        await api.createSellTransaction(transactionData);
        showNotification('Orden de venta creada exitosamente', 'success');
        closeSellModal();
        loadDashboardData();
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

document.getElementById('alert-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const alertData = {
        symbol: formData.get('symbol'),
        alert_type: formData.get('type'),
        target_value: parseFloat(formData.get('value'))
    };
    
    try {
        await api.createAlert(alertData);
        showNotification('Alerta creada exitosamente', 'success');
        closeAlertModal();
        loadAlertsData();
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

// Utility functions
async function createPortfolio() {
    const name = prompt('Nombre del portfolio:');
    if (!name) return;
    
    try {
        await api.createPortfolio({ name, description: '' });
        showNotification('Portfolio creado exitosamente', 'success');
        loadPortfolioData();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function deleteAlert(alertId) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta alerta?')) return;
    
    try {
        await api.deleteAlert(alertId);
        showNotification('Alerta eliminada', 'success');
        loadAlertsData();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Reactive UI update functions using WebSocket events
function updatePortfolioSummary(portfolioData) {
    if (portfolioData.totalValue !== undefined) {
        document.getElementById('total-value').textContent = formatCurrency(portfolioData.totalValue);
    }
    if (portfolioData.totalAssets !== undefined) {
        document.getElementById('total-assets').textContent = portfolioData.totalAssets;
    }
    if (portfolioData.dailyChange !== undefined) {
        const changeElement = document.getElementById('daily-change');
        changeElement.textContent = `${formatCurrency(portfolioData.dailyChange.amount)} (${formatPercentage(portfolioData.dailyChange.percentage)})`;
        changeElement.className = portfolioData.dailyChange.amount >= 0 ? 'positive' : 'negative';
    }
}

function updateRecentTransactions(transactionData) {
    // Add new transaction to the recent transactions list
    const container = document.getElementById('recent-transactions');
    if (container && transactionData) {
        // Create new transaction element
        const transactionElement = document.createElement('div');
        transactionElement.className = 'transaction-item';
        transactionElement.innerHTML = `
            <div class="transaction-info">
                <div class="transaction-icon ${transactionData.type}">
                    <i class="fas fa-${transactionData.type === 'buy' ? 'plus' : 'minus'}"></i>
                </div>
                <div class="transaction-details">
                    <h4>${transactionData.type === 'buy' ? 'Compra' : 'Venta'} ${transactionData.symbol}</h4>
                    <p>${formatDate(transactionData.created_at)}</p>
                </div>
            </div>
            <div class="transaction-amount">
                ${formatCurrency(transactionData.amount * transactionData.price)}
            </div>
        `;
        
        // Add to top of list and remove oldest if more than 5
        container.insertBefore(transactionElement, container.firstChild);
        if (container.children.length > 5) {
            container.removeChild(container.lastChild);
        }
    }
}

function updateMarketPrices(symbol, data) {
    // Update market prices in real-time
    const marketItems = document.querySelectorAll(`[data-symbol="${symbol}"]`);
    marketItems.forEach(item => {
        const priceElement = item.querySelector('.price-value, .market-card-price');
        const changeElement = item.querySelector('.price-change, .market-card-change');
        
        if (priceElement && data.price) {
            priceElement.textContent = formatCurrency(data.price);
            // Add animation for price changes
            priceElement.classList.add('price-updated');
            setTimeout(() => priceElement.classList.remove('price-updated'), 1000);
        }
        
        if (changeElement && data.change !== undefined) {
            changeElement.textContent = formatPercentage(data.change);
            changeElement.className = `price-change ${data.change >= 0 ? 'positive' : 'negative'}`;
        }
    });
}

function updateMarketData(symbol, data) {
    // Update comprehensive market data
    updateMarketPrices(symbol, data);
    
    // Update volume if available
    const volumeElements = document.querySelectorAll(`[data-symbol="${symbol}"] .market-card-volume`);
    volumeElements.forEach(element => {
        if (data.volume) {
            element.textContent = `Vol: ${parseFloat(data.volume).toLocaleString()}`;
        }
    });
}

function handleConnectionChange(connected) {
    // Update UI based on connection status
    const statusElements = document.querySelectorAll('.connection-status, .status-indicator');
    statusElements.forEach(element => {
        if (connected) {
            element.classList.remove('offline');
            element.classList.add('online');
        } else {
            element.classList.remove('online');
            element.classList.add('offline');
        }
    });
    
    // Show notification on connection changes
    if (connected) {
        showNotification('Conectado al servidor en tiempo real', 'success');
    } else {
        showNotification('Conexión perdida. Reintentando...', 'warning');
    }
}

function handleAlertTriggered(alertData) {
    // Handle triggered alerts with enhanced UI feedback
    showNotification(
        `${alertData.symbol}: ${alertData.message}`,
        'warning',
        'Alerta de Precio Activada'
    );
    
    // Add visual indicator to the relevant market item
    const marketItem = document.querySelector(`[data-symbol="${alertData.symbol}"]`);
    if (marketItem) {
        marketItem.classList.add('alert-triggered');
        setTimeout(() => marketItem.classList.remove('alert-triggered'), 3000);
    }
    
    // Update alerts section if visible
    if (currentSection === 'alerts') {
        loadAlertsData();
    }
}

// Enhanced state management through WebSocket requests
function requestPortfolioUpdate() {
    wsManager.requestUpdate('portfolio');
}

function requestTransactionUpdate() {
    wsManager.requestUpdate('transactions');
}

function requestMarketUpdate() {
    wsManager.requestUpdate('market_data');
}

// Auto-refresh data using WebSocket events
setInterval(() => {
    if (wsManager.isConnected) {
        switch (currentSection) {
            case 'dashboard':
                requestPortfolioUpdate();
                requestMarketUpdate();
                break;
            case 'portfolio':
                requestPortfolioUpdate();
                break;
            case 'transactions':
                requestTransactionUpdate();
                break;
            case 'market':
                requestMarketUpdate();
                break;
        }
    }
}, 30000); // Update every 30 seconds

function logout() {
    api.logout();
}
