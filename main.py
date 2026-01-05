import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import re

from env import env

app = FastAPI()

# CORS configuration - in production, specify exact origins
DEBUG = env("DEBUG", default=False, warn_default=False)
if DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Replace with specific origins in production
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

# Target currencies to display prices in
TARGET_CURRENCIES = ["USD", "EUR", "BRL", "GBP", "AUD"]
API_KEY = env("API_KEY")

# Validate API key on startup
if not API_KEY:
    raise ValueError("API_KEY environment variable is required. Please set it in .env file")


def validate_crypto_code(crypto_code: str) -> bool:
    """Validate cryptocurrency code format (2-5 alphanumeric characters, must contain at least one letter)"""
    code = crypto_code.upper()
    # Must be 2-5 characters, alphanumeric, and contain at least one letter
    return bool(re.match(r'^[A-Z0-9]{2,5}$', code)) and bool(re.search(r'[A-Z]', code))


@app.get("/cryptocurrency/{crypto_code}/")
def cryptocurrency_quote(crypto_code: str):
    """
    Get cryptocurrency prices in multiple currencies.
    
    Args:
        crypto_code: Cryptocurrency symbol (e.g., BTC, ETH)
    
    Returns:
        Dictionary with prices in USD, EUR, BRL, GBP, AUD
    """
    # Validate and sanitize input
    crypto_code = crypto_code.upper().strip()
    
    if not validate_crypto_code(crypto_code):
        raise HTTPException(
            status_code=400,
            detail="Invalid cryptocurrency code. Use alphanumeric characters only (1-10 chars)."
        )

    api_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }

    all_prices = {}

    for currency in TARGET_CURRENCIES:
        try:
            # PLAN NOT ALLOWED TO USE COMMA SEPARATED VALUES
            # params = {"symbol": crypto_code, "convert": ",".join(TARGET_CURRENCIES)}
            params = {"symbol": crypto_code, "convert": currency}

            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status", {}).get("error_code") != 0:
                error_message = data.get("status", {}).get("error_message", "Unknown error")
                raise HTTPException(
                    status_code=400,
                    detail=f"CoinMarketCap API error for {currency}: {error_message}",
                )

            # Extract cryptocurrency data
            crypto_data = data.get("data", {})
            if not crypto_data:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Cryptocurrency '{crypto_code}' not found"
                )
            
            # Safe access with error handling
            price = (
                crypto_data.get(crypto_code, {})
                .get("quote", {})
                .get(currency, {})
                .get("price")
            )
            
            if price is not None:
                all_prices[currency] = price
                
        except requests.exceptions.RequestException as e:
            # Log error but continue with other currencies
            print(f"Error fetching {currency} price: {str(e)}")
            all_prices[currency] = None
        except HTTPException:
            # Re-raise HTTP exceptions
            raise

    # Check if we have any valid prices (not None)
    if not all_prices or all(price is None for price in all_prices.values()):
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch prices for '{crypto_code}'. Please check the symbol and try again."
        )

    return all_prices
