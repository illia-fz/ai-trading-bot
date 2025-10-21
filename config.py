"""Configuration for AI Trading Bot.

This file defines default settings such as the cryptocurrency symbol to trade and
percentage values for take profit and stop loss levels. You can adjust these values
as needed to fit your trading strategy.
"""

# Default cryptocurrency ID used by the CoinGecko API
DEFAULT_SYMBOL = "bitcoin"

# Default fiat currency for price quotes
DEFAULT_CURRENCY = "usd"

# Default take profit percentage (e.g., 0.02 for 2%)
TAKE_PROFIT_PCT = 0.02

# Default stop loss percentage (e.g., 0.01 for 1%)
STOP_LOSS_PCT = 0.01
