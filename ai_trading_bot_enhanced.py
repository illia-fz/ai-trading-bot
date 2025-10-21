#!/usr/bin/env python3
"""
Enhanced AI-driven trading bot script.

This script fetches cryptocurrency market data and news, calls an AI model via API to generate trading signals,
computes simple moving averages from historical prices and calculates take-profit and stop-loss levels based on
user-configurable percentages. It logs trade decisions to console and optionally to a file.

Usage:
    python ai_trading_bot_enhanced.py --symbols bitcoin,ethereum --currency usd --take-profit 0.03 --stop-loss 0.015 --logfile trades.log
"""

import argparse
import logging
import os
from typing import Dict, List, Optional, Tuple

from datetime import datetime
import requests

import config  # default configuration



def fetch_market_data(symbols: List[str], currency: str) -> Dict[str, float]:
    """Fetch current cryptocurrency prices from CoinGecko for given symbols."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(symbols), "vs_currencies": currency}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return {sym: float(data.get(sym, {}).get(currency, 0.0)) for sym in symbols}


def fetch_historical_prices(symbol: str, currency: str, days: int = 7) -> Optional[List[float]]:
    """Fetch historical daily prices for a symbol over the past 'days' days."""
    try:
        endpoint = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
        params = {"vs_currency": currency, "days": days}
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [point[1] for point in data.get("prices", [])]
    except (requests.RequestException, ValueError) as e:
        logging.error("Failed to fetch historical prices for %s: %s", symbol, e)
        return None


def calculate_moving_average(prices: List[float]) -> float:
    """Calculate the simple moving average of a list of prices."""
    return sum(prices) / len(prices) if prices else 0.0


def fetch_news(limit: int = 5) -> List[str]:
    """Fetch top cryptocurrency news headlines using the CryptoControl API."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return []
    url = "https://cryptocontrol.io/api/v1/public/news"
    params = {"latest": "true", "page": 0, "limit": limit}
    headers = {"x-api-key": api_key}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        articles = response.json()
        return [art.get("title", "") for art in articles[:limit]]
    except (requests.RequestException, ValueError) as e:
        logging.error("Failed to fetch news: %s", e)
        return []


def analyze_with_model(market_data: Dict[str, float], news: List[str]) -> str:
    """Call an external AI model API to generate a trading signal (buy/sell/hold)."""
    model_url = os.getenv("MODEL_API_URL")
    model_key = os.getenv("MODEL_API_KEY")
    if not model_url or not model_key:
        # Default behaviour when no model is configured.
        return "hold"
    payload = {"market_data": market_data, "news": news}
    headers = {"Authorization": f"Bearer {model_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(model_url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        result = response.json()
        return result.get("signal", "hold")
    except (requests.RequestException, ValueError) as e:
        logging.error("AI model request failed: %s", e)
        return "hold"


def calculate_trade_levels(action: str, price: float, take_profit_pct: float, stop_loss_pct: float) -> Tuple[float, float]:
    """Calculate take-profit and stop-loss price levels based on trade action and current price."""
    if action == "buy":
        return price * (1 + take_profit_pct), price * (1 - stop_loss_pct)
    if action == "sell":
        return price * (1 - take_profit_pct), price * (1 + stop_loss_pct)
    return price, price


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Enhanced AI-driven trading bot.")
    parser.add_argument("--symbols", type=str, default=config.DEFAULT_SYMBOL, help="Comma-separated list of symbols (default: bitcoin)")
    parser.add_argument("--currency", type=str, default=config.DEFAULT_CURRENCY, help="Fiat currency for pricing (default: usd)")
    parser.add_argument("--take-profit", type=float, default=config.TAKE_PROFIT_PCT, help="Take-profit percentage (e.g., 0.02 for 2%)")
    parser.add_argument("--stop-loss", type=float, default=config.STOP_LOSS_PCT, help="Stop-loss percentage (e.g., 0.01 for 1%)")
    parser.add_argument("--logfile", type=str, default=None, help="Path to a file for saving trade logs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Configure logging
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    if args.logfile:
        file_handler = logging.FileHandler(args.logfile)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(file_handler)

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    currency = args.currency

    try:
        market_data = fetch_market_data(symbols, currency)
    except Exception as e:
        logger.error("Error fetching market data: %s", e)
        return

    news = fetch_news()

    # Get AI signal
    signal = analyze_with_model(market_data, news)

    # Determine trade parameters
    take_profit_pct = args.take_profit
    stop_loss_pct = args.stop_loss

    for symbol, price in market_data.items():
        hist_prices = fetch_historical_prices(symbol, currency)
        moving_avg = calculate_moving_average(hist_prices) if hist_prices else None

        tp, sl = calculate_trade_levels(signal, price, take_profit_pct, stop_loss_pct)

        logger.info(
            "Symbol: %s | Price: %.2f | 7d MA: %s | Action: %s | TP: %.2f | SL: %.2f",
            symbol,
            price,
            f"{moving_avg:.2f}" if moving_avg else "N/A",
            signal,
            tp,
            sl,
        )

        print(f"{symbol} price: {price:.2f} {currency.upper()}")
        if moving_avg:
            print(f"7-day moving average: {moving_avg:.2f} {currency.upper()}")
        print(f"Trade signal: {signal}")
        print(f"Take-profit at: {tp:.2f} {currency.upper()}, Stop-loss at: {sl:.2f} {currency.upper()}")
        print("-" * 40)


if __name__ == "__main__":
    main()
