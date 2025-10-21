"""
Utility functions for sending trade notifications via Telegram.

This module uses Telegram Bot API to send messages. It requires the TELEGRAM_BOT_TOKEN
and TELEGRAM_CHAT_ID environment variables to be set.
"""

import os
import logging
import requests
from typing import Optional


def send_telegram_message(message: str, bot_token: Optional[str] = None, chat_id: Optional[str] = None) -> None:
    """
    Send a text message to a Telegram chat using the Bot API.

    Args:
        message: The message text to send.
        bot_token: Telegram bot token. If None, read from the TELEGRAM_BOT_TOKEN environment variable.
        chat_id: Telegram chat ID or channel username. If None, read from the TELEGRAM_CHAT_ID environment variable.
    """
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        logging.warning("Telegram bot token or chat ID not provided. Skipping sending message.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat, "text": message}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logging.info("Message sent to Telegram successfully.")
    except requests.exceptions.RequestException as e:
        logging.error("Failed to send Telegram message: %s", e)
