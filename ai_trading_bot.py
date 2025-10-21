import os
import json
import requests
from typing import List, Dict, Tuple


def fetch_market_data() -> Dict[str, Dict[str, float]]:
    """Fetch sample cryptocurrency market data from a public API (CoinGecko).
    Returns a dictionary mapping coin symbols to USD prices."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum", "vs_currencies": "usd"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_news(limit: int = 5) -> List[str]:
    """Fetch latest cryptocurrency news headlines using a news API.
    Set the NEWS_API_KEY environment variable to call a real API. If no key is provided,
    the function will return an empty list.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        # No API key provided; skip news fetching
        return []
    url = "https://cryptonews-api.com/api/v1/category"
    params = {"section": "general", "items": limit, "apikey": api_key}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [article.get("title", "") for article in data.get("data", [])]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def analyze_with_model(market_data: Dict[str, Dict[str, float]], news: List[str]) -> Dict[str, any]:
    """Send market and news data to an external neural network model via API.
    Requires MODEL_API_URL and MODEL_API_KEY environment variables. Returns a
    dictionary with keys like 'action' (buy/sell/hold) and 'confidence'. If the
    variables are not set or the API call fails, returns a default hold signal.
    """
    api_url = os.getenv("MODEL_API_URL")
    api_key = os.getenv("MODEL_API_KEY")
    if not api_url or not api_key:
        return {"action": "hold", "confidence": 0.0}
    payload = {"market_data": market_data, "news": news}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error calling model API: {e}")
        return {"action": "hold", "confidence": 0.0}


def calculate_trade_levels(price: float, action: str, take_profit_pct: float = 0.02, stop_loss_pct: float = 0.01) -> Tuple[float, float]:
    """Calculate take‑profit and stop‑loss levels based on current price and action.
    Returns a tuple of (take_profit_level, stop_loss_level)."""
    if action == "buy":
        take_profit = price * (1 + take_profit_pct)
        stop_loss = price * (1 - stop_loss_pct)
    elif action == "sell":
        take_profit = price * (1 - take_profit_pct)
        stop_loss = price * (1 + stop_loss_pct)
    else:
        take_profit = stop_loss = price
    return take_profit, stop_loss


def main() -> None:
    market_data = fetch_market_data()
    news = fetch_news()
    signal = analyze_with_model(market_data, news)
    btc_price = market_data.get("bitcoin", {}).get("usd")
    if btc_price is not None:
        take_profit, stop_loss = calculate_trade_levels(btc_price, signal.get("action", "hold"))
    else:
        take_profit = stop_loss = None
    print("Market data:", market_data)
    print("News headlines:", news)
    print("Model signal:", signal)
    print(f"Calculated levels -> Take Profit: {take_profit}, Stop Loss: {stop_loss}")


if __name__ == "__main__":
    main()
