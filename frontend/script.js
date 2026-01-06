// API URL - use relative path when in Docker (nginx proxy), absolute for local dev
// In Docker: nginx proxies /cryptocurrency/ to api:8000
// For local dev: use localhost:8000
const getApiUrl = () => {
    const host = window.location.hostname;
    // If running locally (not in Docker)
    if (host === 'localhost' || host === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    // In Docker, use relative URL (nginx will proxy)
    return '';
};

const API_BASE_URL = getApiUrl();

// Allow Enter key to trigger search
document.getElementById('crypto-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        fetchPrices();
    }
});

async function fetchPrices() {
    const cryptoInput = document.getElementById('crypto-input');
    const cryptoCode = cryptoInput.value.trim().toUpperCase();
    
    // Hide previous results and errors
    document.getElementById('results').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    
    // Validate input
    if (!cryptoCode) {
        showError('Please enter a cryptocurrency symbol (e.g., BTC, ETH)');
        return;
    }
    
    // Additional validation: alphanumeric only, max 10 characters
    if (!/^[A-Z0-9]{1,10}$/.test(cryptoCode)) {
        showError('Invalid cryptocurrency code. Use only letters and numbers (1-10 characters).');
        return;
    }
    
    // Show loading state
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('search-btn').disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/cryptocurrency/${cryptoCode}/`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(cryptoCode, data);
        
    } catch (error) {
        console.error('Error fetching prices:', error);
        showError(error.message || 'Failed to fetch cryptocurrency prices. Please try again.');
    } finally {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('search-btn').disabled = false;
    }
}

function displayResults(cryptoCode, prices) {
    const resultsDiv = document.getElementById('results');
    const cryptoName = document.getElementById('crypto-name');
    const pricesGrid = document.getElementById('prices-grid');
    
    // Set cryptocurrency name
    cryptoName.textContent = `${cryptoCode} Prices`;
    
    // Clear previous prices
    pricesGrid.innerHTML = '';
    
    // Create price cards for each currency
    const currencies = Object.keys(prices);
    
    if (currencies.length === 0) {
        showError('No price data available for this cryptocurrency.');
        return;
    }
    
    currencies.forEach(currency => {
        const price = prices[currency];
        if (price !== null && price !== undefined) {
            const priceCard = createPriceCard(currency, price);
            pricesGrid.appendChild(priceCard);
        }
    });
    
    // Show results
    resultsDiv.classList.remove('hidden');
}

function createPriceCard(currency, price) {
    const card = document.createElement('div');
    card.className = 'price-card';
    
    const currencyDiv = document.createElement('div');
    currencyDiv.className = 'currency';
    currencyDiv.textContent = currency;
    
    const amountDiv = document.createElement('div');
    amountDiv.className = 'amount';
    // Format price with commas and 2 decimal places
    amountDiv.textContent = formatPrice(price);
    
    card.appendChild(currencyDiv);
    card.appendChild(amountDiv);
    
    return card;
}

function formatPrice(price) {
    if (price === null || price === undefined) {
        return 'N/A';
    }
    
    // Format large numbers with commas
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(price).replace('$', '');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

