# ai-trading-bot

## Features
- Connects to neural network models via API to analyze market data and news.
- Fetches cryptocurrency market prices from external API (e.g., CoinGecko).
- Fetches news headlines and passes them to the model for sentiment or signal analysis.
- Generates trade signals (buy, sell, or hold) with confidence scores.
- Calculates take-profit and stop-loss levels based on configurable percentages.
- - Computes 7-day simple moving averages from historical prices for additional context.
- Logs trade decisions with price, moving average, and levels to console and optionally to a file.
-  Supports multiple AI models (default, OpenAI, HuggingFace) using environment variables and the new `model_utils` module.
- Includes an enhanced script `ai_trading_bot_enhanced.py` with these features and improved CLI options.


## Requirements
- Python 3.8+
- See `requirements.txt` for required packages.

## Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```


## Configuration
Before running the bot, set the following environment variables (optional):
- `NEWS_API_KEY`: your API key for a news provider to fetch headlines.
- `MODEL_API_URL`: URL of your deployed neural network model API.
- `MODEL_API_KEY`: API key or token required to access the model API.

If these variables are not set, the bot will skip news fetching or use default behavior.

## Usage
Run the trading bot from the command line:
```bash
python ai_trading_bot.py
```
The script will fetch market data and news (if configured), call the model to get a trade signal, and output calculated take-profit and stop-loss levels.

## Contributing
Contributions are welcome! Feel free to open issues or pull requests to add new features, improve model integration, or fix bugs.
