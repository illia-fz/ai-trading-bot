#!/usr/bin/env python3
"""
AI-driven trading bot script.
This script fetches market data and news, calls an AI model via API to get trading signals,
and calculates take-profit and stop-loss levels.

Use CLI arguments to specify symbol(s), currency, and profit/loss percentages.
See README for details.
"""

import os
import argparse
import logging
import requests
from typing import List, Dict, Tuple

import config  # custom config file with default values


def fetch_market_data(symbols: List[str], currency: str) -> Dict[str, Dict[str, float]]:
    """Fetch cryptocurrency market data from CoinGecko API for given symbols."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(symbols), "vs_currencies": currency}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def fetch_news(limit: int = 5) -> List[str]:
    """Fetch latest news headlines from CryptoNews API if API key provided."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return []
    url = "https://cryptonews-api.com/api/v1/category"
    params = {"section": "general", "items": limit, "apiKey": api_key}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return [article.get("title", "") for article in data.get("data", [])]


def analyze_with_model(market_data: Dict[str, Dict[str, float]], news: List[str]) -> str:
    """Send combined market data and news to external AI model and return action (buy/hold/sell)."""
    model_url = os.getenv("MODEL_API_URL")
    model_key = os.getenv("MODEL_API_KEY")
    if not model_url or not model_key:
        return "hold"
    payload = {"market_data": market_data, "news": news}
    headers = {"Authorization": f"Bearer {model_key}", "Content-Type": "application/json"}
    response = requests.post(model_url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    result = response.json()
    return result.get("action", "hold")


def calculate_trade_levels(price: float, action: str, tp_pct: float, sl_pct: float) -> Tuple[float, float]:
    """Calculate take-profit and stop-loss levels based on current price and action."""
    if action == "buy":
        return price * (1 + tp_pct), price * (1 - sl_pct)
    elif action == "sell":
        return price * (1 - tp_pct), price * (1 + sl_pct)
    return price, price


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the trading bot."""
    parser = argparse.ArgumentParser(description="AI-driven trading bot")
    parser.add_argument(
        "--symbols",
        type=str,
        default=config.DEFAULT_SYMBOL,
        help="Comma-separated list of cryptocurrency IDs (e.g., bitcoin,ethereum)",
    )
    parser.add_argument(
        "--currency",
        type=str,
        default=config.DEFAULT_CURRENCY,
        help="Fiat currency (e.g., usd, eur)",
    )
    parser.add_argument(
        "--tp",
        type=float,
        default=config.TAKE_PROFIT_PCT,
        help="Take-profit percentage (e.g., 0.02 for 2%)",
    )
    parser.add_argument(
        "--sl",
        type=float,
        default=config.STOP_LOSS_PCT,
        help="Stop-loss percentage (e.g., 0.01 for 1%)",
    )
    return parser.parse_args()


def main() -> None:
    """Main execution function for the trading bot."""
    args = parse_args()
    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    # Configure logging to provide timestamped info
        from telegram_utils import send_telegram_message
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logging.info("Fetching market data for symbols %s in %s", symbols, args.currency)
    market_data = fetch_market_data(symbols, args.currency)
    logging.info("Market data: %s", market_data)

    news = fetch_news()
    if news:
        logging.info("Latest news headlines: %s", news)

    action = analyze_with_model(market_data, news)
    logging.info("AI model action: %s", action)

    for symbol in symbols:
        price = market_data[symbol][args.currency]
        take_profit, stop_loss = calculate_trade_levels(price, action, args.tp, args.sl)
        logging.info(
            "For %s at price %f: take-profit %f, stop-loss %f",
            symbol,
            price,
            take_profit,
            stop_loss,
        )

    # Print final action for user reference
    print("Action:", action)
    # Send trade notification via Telegram
    message_lines = [f"Trading signal: {action.upper()}"]
    for symbol in symbols:
        price = market_data[symbol][args.currency]
        tp, sl = calculate_trade_levels(price, args.tp, args.sl)
        message_lines.append(f"{symbol.upper()} {price:.2f} {args.currency}, TP {tp:.2f}, SL {sl:.2f}")
    message = "\n".join(message_lines)
    try:
        send_telegram_message(message)
    except Exception as e:
        logging.error("Failed to send Telegram notification: %s", e)



if __name__ == "__main__":
    main()
