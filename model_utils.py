"""
Model utilities for AI trading bot.
This module allows selecting different AI models (e.g., default, Hugging Face, OpenAI) and calling them.
"""

import os
import requests
import logging
from typing import Optional, Dict

def analyze_text_with_model(
    text: str,
    model: str = "default",
    model_api_url: Optional[str] = None,
    model_api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    Call an external model to analyze input text and return a dictionary with 'label' and 'score'.
    :param text: The text to analyze.
    :param model: Name of the model to use ('default', 'openai', 'huggingface').
    :param model_api_url: Override API URL. If None, falls back to environment variables:
                          MODEL_API_URL, OPENAI_API_URL, HUGGINGFACE_API_URL.
    :param model_api_key: API key. If None, falls back to environment variables accordingly.
    :return: A dictionary with keys 'label' and 'score'.
    """
    # Determine model-specific environment variables
    if model_api_url is None:
        if model == "openai":
            model_api_url = os.getenv("OPENAI_API_URL")
        elif model == "huggingface":
            model_api_url = os.getenv("HUGGINGFACE_API_URL")
        else:
            model_api_url = os.getenv("MODEL_API_URL")
    if model_api_key is None:
        if model == "openai":
            model_api_key = os.getenv("OPENAI_API_KEY")
        elif model == "huggingface":
            model_api_key = os.getenv("HUGGINGFACE_API_KEY")
        else:
            model_api_key = os.getenv("MODEL_API_KEY")

    if not model_api_url or not model_api_key:
        logging.warning("Model API URL or API key not configured. Returning default neutral signal.")
        return {"label": "hold", "score": 0.0}

    try:
        response = requests.post(
            model_api_url,
            headers={
                "Authorization": f"Bearer {model_api_key}",
                "Content-Type": "application/json",
            },
            json={"text": text, "model": model},
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        return result.get("data", {"label": "hold", "score": 0.0})
    except Exception as e:
        logging.error(f"Failed to analyze text with model {model}: {e}")
        return {"label": "hold", "score": 0.0}
