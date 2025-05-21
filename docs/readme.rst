Forex Price Movement Prediction Dashboard
=========================================

This project implements a comprehensive dashboard for forex price movement analysis and prediction using Alpha Vantage data and Facebook Prophet time series forecasting.

Features
--------

- Historical forex data fetching using Alpha Vantage API
- Interactive Streamlit dashboard with technical indicators
- Time series forecasting using Facebook Prophet
- Technical indicators: RSI, MACD, Bollinger Bands
- Trading signals generation with confidence levels
- Prophet-enhanced trading signals with entry, take profit and stop loss
- Currency-specific news with sentiment analysis via News API
- Advanced data visualization with Plotly
- Data download as CSV
- Easy one-click forecasting

Prerequisites
-------------

- Python 3.9+
- Streamlit
- Pandas
- Facebook Prophet
- Plotly
- Alpha Vantage API key
- News API key (for the news feature)
- TextBlob (optional, for enhanced sentiment analysis)

Installation
------------

Clone this repository:

.. code-block:: bash

   git clone <repository-url>
   cd quant-model-for-forex-predict-prediction

Install the required packages:

.. code-block:: bash

   pip install -r requirements.txt

Install TextBlob for sentiment analysis (optional but recommended):

.. code-block:: bash

   pip install textblob
   python -m textblob.download_corpora

Create a `.env` file with your API keys:

.. code-block:: text

   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
   NEWS_API_KEY=your_news_api_key_here

You can get a free Alpha Vantage API key from `https://www.alphavantage.co`.  
You can get a free News API key from `https://newsapi.org`.

Usage
-----

Run the Streamlit dashboard:

.. code-block:: bash

   streamlit run app.py

This will launch the forex prediction dashboard in your browser.

Dashboard Features
------------------

1. Data Selection and Visualization

- Select currency pairs (EUR/USD, GBP/USD, etc.)
- Choose date range (up to 2 years of historical data)
- View candlestick charts and price statistics

2. Technical Indicators

- RSI: Helps identify overbought or oversold conditions
- MACD: Shows momentum trends
- Bollinger Bands: Display volatility and potential price breakouts

3. Price Forecasting with Facebook Prophet

- Choose which price to forecast (Open, High, Low, Close)
- Simplified model using essential price data
- 7-day forecast with confidence intervals
- Forecast metrics and interactive charts

4. Trading Signals

- Combines indicators and Prophet forecasts
- Entry, take profit, stop loss levels from forecast
- Signal confidence metrics and enhanced checklist

5. Forex News

- Currency pair-specific news with sentiment analysis
- Intelligent keyword-based search
- Color-coded sentiment (bullish, bearish, neutral)
- Cached results every 30 minutes

News API Integration
--------------------

- Targeted search using keywords and central banks
- TextBlob sentiment analysis
- Pair-specific and filtered content
- Caching for API efficiency

News API Features:

- Free Tier: 100 requests/day
- Real-time news from many sources
- Rich metadata and multi-language support

Facebook Prophet Model
-----------------------

How It Works:

- Clean and format historical price data
- Detect trends, seasonality, holidays
- Generate forecasts with uncertainty intervals

Model Features:

- Single column (Close, Open, etc.)
- Handles missing/outliers
- Includes confidence intervals

Best Practices:

- Use at least 60 days of historical data
- Pick predictable pairs
- Use daily data
- Combine with technical indicators and news

API Usage Notes
---------------

- Alpha Vantage: 5 calls/min (500/day)
- News API: 100 requests/day
- News cache refreshes every 30 min

Limitations
-----------

- Forecasts may not predict unpredictable events
- API rate limits
- Intraday data limitations
- Sentiment analysis may miss nuance

Future Enhancements
-------------------

- More technical indicators
- More news sources
- Strategy backtesting
- Portfolio optimization
- Real-time trading alerts
- Advanced NLP sentiment analysis

License
-------

MIT License

Acknowledgements
----------------

- Alpha Vantage
- News API
- Facebook Prophet
- Streamlit
- TextBlob
