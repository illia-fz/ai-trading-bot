"""
Utility functions for market data analysis.

This module provides functions to calculate moving averages and
relative strength index (RSI) for a sequence of price data.
"""

from typing import List, Optional


def calculate_moving_average(prices: List[float], window: int = 7) -> Optional[float]:
    """
    Calculate the simple moving average for the last `window` prices.
    If fewer than `window` prices are provided, returns the average of all prices.
    """
    if not prices:
        return None
    if len(prices) < window:
        return sum(prices) / len(prices)
    return sum(prices[-window:]) / window


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    Calculate the Relative Strength Index (RSI) for a list of prices.
    Returns None if not enough data is available.
    """
    if len(prices) < period + 1:
        return None

    gains = 0.0
    losses = 0.0
    for i in range(-period, 0):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains += change
        else:
            losses -= change  # change is negative

    average_gain = gains / period
    average_loss = losses / period if losses != 0 else 0.001  # avoid division by zero
    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
