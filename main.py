import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from env import env

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Target currencies to display prices in
TARGET_CURRENCIES = ["USD", "EUR", "BRL", "GBP", "AUD"]
API_KEY = env("API_KEY")


@app.get("/cryptocurrency/{crypto_code}/")
def cryptocurrency_quote(crypto_code: str):
    crypto_code = crypto_code.upper()

    api_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }

    all_prices = {}

    for currency in TARGET_CURRENCIES:
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
                status_code=404, detail=f"Cryptocurrency '{crypto_code}' not found"
            )
        all_prices[currency] = (
            crypto_data.get(crypto_code).get("quote", {}).get(currency, {}).get("price")
        )

    return all_prices
