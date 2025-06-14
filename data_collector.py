import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from sqlalchemy import create_engine
import os
import requests
import streamlit as st

class ForexDataCollector:
    def __init__(self, currency_pair="EUR/USD", interval="daily", db_path="sqlite:///forex_data.db", alpha_vantage_key=None):
        """
        Initialize the ForexDataCollector using Alpha Vantage API
        
        Parameters:
        -----------
        currency_pair : str
            The forex pair to collect data for (default: "EUR/USD")
            Format should be "BASE/QUOTE" (e.g., "EUR/USD", "GBP/JPY")
        interval : str
            Data interval (default: "daily")
            Valid values: "daily", "weekly", "monthly"
        db_path : str
            SQLite database path
        alpha_vantage_key : str
            Alpha Vantage API key (optional). If not provided, must be set in .env file
        """
        self.base_currency, self.quote_currency = currency_pair.split('/')
        self.interval = self._convert_interval(interval)
        self.engine = create_engine(db_path)

        # Load Alpha Vantage API key from argument or .streamlit/secrets.toml
        if alpha_vantage_key:
            self.alpha_vantage_key = alpha_vantage_key
        else:
            try:
                self.alpha_vantage_key = st.secrets["ALPHA_VANTAGE_API_KEY"]
            except Exception:
                raise ValueError("Alpha Vantage API key not found. Please provide it as an argument or set it in .streamlit/secrets.toml.")

        
    def _convert_interval(self, interval):
        """Convert interval string to Alpha Vantage format"""
        interval_map = {
            'daily': 'Daily',
            'weekly': 'Weekly',
            'monthly': 'Monthly',
            '1min': '1min',
            '5min': '5min',
            '15min': '15min',
            '30min': '30min',
            '45min': '45min',  # New interval
            '60min': '60min'
        }
        return interval_map.get(interval.lower(), 'Daily')
            
    def fetch_forex_data(self, start_date=None, end_date=None):
        """
        Fetch forex data from Alpha Vantage
        
        Parameters:
        -----------
        start_date : str or datetime, optional
            Start date for data fetching. If None, fetches last the 100 days
        end_date : str or datetime, optional
            End date for data fetching. If None, uses current date
        """
        # Set default dates if not provided
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=100)
        
        try:
            # Convert dates to string format
            start_date_str = pd.to_datetime(start_date).strftime("%Y-%m-%d")
            end_date_str = pd.to_datetime(end_date).strftime("%Y-%m-%d")
            
            # Use FX_DAILY for daily data
            params = {
                "function": "FX_DAILY",
                "from_symbol": self.base_currency,
                "to_symbol": self.quote_currency,
                "apikey": self.alpha_vantage_key,
                "outputsize": "full"
            }
            time_series_key = "Time Series FX (Daily)"
            
            # Make the API request
            response = requests.get("https://www.alphavantage.co/query", params=params)
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
            
            if "Note" in data:
                raise ValueError(f"Alpha Vantage API limit reached: {data['Note']}")
            
            if "Information" in data:
                raise ValueError(f"Alpha Vantage API error: {data['Information']}")
            
            # Get the correct time series key
            if time_series_key not in data:
                raise ValueError(f"No {time_series_key} found in the API response")
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
            
            if df.empty:
                raise ValueError("Empty dataset received from Alpha Vantage")
            
            # Rename columns
            column_map = {
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close'
            }
            df = df.rename(columns=column_map)
            
            # Convert to float and process
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Filter date range
            df = df[df.index >= pd.to_datetime(start_date_str)]
            df = df[df.index <= pd.to_datetime(end_date_str)]
            
            if df.empty:
                raise ValueError("No data available for the selected date range")
            
            # Add technical indicators and trading signals
            df = self._process_data(df)
            
            # Ensure at least 20 data points for signal calculation
            if len(df) >= 20:
                df = self.calculate_trading_signals(df, confidence_threshold=0.8)
            else:
                print("Not enough data points for signal calculation")
                # Initialize signal columns to prevent errors
                df['Signal'] = 0
                df['Confidence'] = 0.0
                df['Entry_Price'] = df['Close']
                df['Take_Profit'] = df['Close']
                df['Stop_Loss'] = df['Close']
            
            return df
            
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return pd.DataFrame()
    
    def _process_data(self, data):
        """
        Process the data by adding technical indicators
        """
        if data.empty:
            return data
            
        # Calculate technical indicators
        try:
            # Trend Indicators
            data['SMA_20'] = SMAIndicator(close=data['Close'], window=20).sma_indicator()
            data['EMA_20'] = EMAIndicator(close=data['Close'], window=20).ema_indicator()

            # Momentum Indicators
            data['RSI'] = RSIIndicator(close=data['Close'], window=14).rsi()
            macd = MACD(close=data['Close'], window_slow=26, window_fast=12, window_sign=9)
            data['MACD'] = macd.macd()
            data['MACD_Signal'] = macd.macd_signal()
            data['MACD_Hist'] = macd.macd_diff()

            # Volatility Indicators
            atr = AverageTrueRange(high=data['High'], low=data['Low'], close=data['Close'], window=14)
            data['ATR'] = atr.average_true_range()
            bb = BollingerBands(close=data['Close'], window=20)
            data['Bollinger_Upper'] = bb.bollinger_hband()
            data['Bollinger_Middle'] = bb.bollinger_mavg()
            data['Bollinger_Lower'] = bb.bollinger_lband()

            # Add Weekly VWAP (Volume Weighted Average Price)
            # For Forex, we don't have volume, so use a simple 5-day moving average
            data['Weekly_VWAP'] = data['Close'].rolling(window=5).mean()

            # Add Support and Resistance for Breakout detection
            data['Resistance'] = data['High'].rolling(window=20).max()
            data['Support'] = data['Low'].rolling(window=20).min()

            # Volume handling (we don't have volume for forex from Alpha Vantage)
            if 'Volume' not in data.columns:
                data['Volume'] = 0

            # Add percentage changes
            data['Returns'] = data['Close'].pct_change()
            data['Log_Returns'] = np.log(data['Close']/data['Close'].shift(1))

        except Exception as e:
            print(f"Error calculating technical indicators: {str(e)}")
        return data
    
    def fetch_news_data(self, query=None, max_results=10):
        """
        Fetch relevant news articles using Alpha Vantage News API
        
        Parameters:
        -----------
        query : str, optional
            The search query for news articles. If None, uses the currency pair.
        max_results : int, optional
            Maximum number of news articles to return (default: 10)
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with news articles
        """
        try:
            # Set default query if not provided
            if query is None:
                # Format the query for better results: EUR/USD -> "EUR USD forex"
                query = f"{self.base_currency} {self.quote_currency} forex"
            
            # Make sure max_results is an integer to avoid type issues    
            try:
                max_results = int(max_results)
            except (ValueError, TypeError):
                print(f"Warning: Invalid max_results value ({max_results}), using default of 10")
                max_results = 10
                
            # Try to use Alpha Vantage's news API if available
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": f"FOREX:{self.base_currency}{self.quote_currency}",
                "apikey": self.alpha_vantage_key,
                "sort": "RELEVANCE",
                "limit": max_results
            }
            
            # Print debugging information
            print(f"Fetching news with query: {query}, max_results: {max_results}")
            print(f"API request params: {params}")
            
            # Make the API request
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check if we got valid data
            if "feed" in data:
                # Extract relevant fields from each news item
                news_list = []
                for item in data["feed"][:max_results]:
                    news_list.append({
                        'title': item.get('title', 'No title'),
                        'summary': item.get('summary', 'No summary'),
                        'url': item.get('url', '#'),
                        'source': item.get('source', 'Unknown'),
                        'published_at': item.get('time_published', None),
                        'sentiment': item.get('overall_sentiment_score', 0)
                    })
                
                # Convert to DataFrame
                news_df = pd.DataFrame(news_list)
                if not news_df.empty and 'published_at' in news_df.columns:
                    news_df['published_at'] = pd.to_datetime(news_df['published_at'], format='%Y%m%dT%H%M%S', errors='coerce')
                    news_df = news_df.sort_values('published_at', ascending=False)
                
                print(f"Successfully fetched {len(news_list)} news articles")
                return news_df
            else:
                # If Alpha Vantage news isn't available, try a fallback approach
                print("Alpha Vantage News API not available or no results. Using alternative news source.")
                if "Note" in data:
                    print(f"API response note: {data['Note']}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def save_to_database(self, data, table_name='forex_data'):
        """
        Save data to SQLite database
        """
        try:
            data.to_sql(table_name, self.engine, if_exists='append')
            print(f"Data saved to {table_name} successfully")
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
    
    def load_from_database(self, table_name='forex_data', start_date=None, end_date=None):
        """
        Load data from SQLite database
        """
        query = f"SELECT * FROM {table_name}"
        if start_date and end_date:
            query += f" WHERE index BETWEEN '{start_date}' AND '{end_date}'"
            
        try:
            data = pd.read_sql(query, self.engine, index_col='index', parse_dates=['index'])
            return data
        except Exception as e:
            print(f"Error loading from database: {str(e)}")
            return None

    def detect_breakouts(self, data, window=20):
        """
        Detect potential breakouts from support/resistance levels
        """
        if data is None or data.empty:
            return pd.DataFrame()
        
        # Make sure Resistance and Support columns exist
        if 'Resistance' not in data.columns or 'Support' not in data.columns:
            print("Calculating Support and Resistance levels for breakout detection")
            # Calculate Resistance and Support if they don't exist
            data['Resistance'] = data['High'].rolling(window=window).max()
            data['Support'] = data['Low'].rolling(window=window).min()
            
        # Initialize Breakout column if needed
        data['Breakout'] = 0  # 0: No breakout, 1: Bullish breakout, -1: Bearish breakout
        
        try:
            # Bullish breakout
            data.loc[data['Close'] > data['Resistance'].shift(1), 'Breakout'] = 1
            
            # Bearish breakout
            data.loc[data['Close'] < data['Support'].shift(1), 'Breakout'] = -1
        except Exception as e:
            print(f"Error calculating breakouts: {str(e)}")
            # Fallback: set all to 0 (no breakout)
            data['Breakout'] = 0
        
        return data
    
    def calculate_tp_sl_levels(self, data, atr_multiplier_tp=1.5, atr_multiplier_sl=1.0):
        """
        Calculate Take Profit and Stop Loss levels based on ATR
        """
        if data is None or data.empty:
            return pd.DataFrame()
            
        data['TP_Long'] = data['Close'] + (data['ATR'] * atr_multiplier_tp)
        data['SL_Long'] = data['Close'] - (data['ATR'] * atr_multiplier_sl)
        data['TP_Short'] = data['Close'] - (data['ATR'] * atr_multiplier_tp)
        data['SL_Short'] = data['Close'] + (data['ATR'] * atr_multiplier_sl)
        
        return data 

    def calculate_trading_signals(self, data, confidence_threshold=0.8):
        """
        Calculate trading signals with confidence levels
        
        Parameters:
        -----------
        data : pd.DataFrame
            The forex data with technical indicators
        confidence_threshold : float
            Minimum confidence level required for a signal (0.0 to 1.0)
        """
        if data is None or data.empty:
            return pd.DataFrame()
        
        # Initialize signals
        data['Signal'] = 0  # 0: No signal, 1: Buy, -1: Sell
        data['Confidence'] = 0.0
        data['Entry_Price'] = 0.0
        data['Take_Profit'] = 0.0
        data['Stop_Loss'] = 0.0
        
        try:
            for i in range(20, len(data)):
                # Get current window of data
                window = data.iloc[i-20:i+1]
                
                # Calculate confidence based on multiple factors
                signals = []
                confidences = []
                
                # 1. RSI Signal (30% weight)
                rsi = window['RSI'].iloc[-1]
                if rsi < 30:
                    signals.append(1)  # Oversold - Buy
                    confidences.append(min((30 - rsi) / 10, 1.0) * 0.3)
                elif rsi > 70:
                    signals.append(-1)  # Overbought - Sell
                    confidences.append(min((rsi - 70) / 10, 1.0) * 0.3)
                
                # 2. MACD Signal (30% weight)
                macd = window['MACD'].iloc[-1]
                macd_signal = window['MACD_Signal'].iloc[-1]
                macd_hist = macd - macd_signal
                if macd > macd_signal:
                    signals.append(1)
                    confidences.append(min(abs(macd_hist) / 0.0005, 1.0) * 0.3)
                else:
                    signals.append(-1)
                    confidences.append(min(abs(macd_hist) / 0.0005, 1.0) * 0.3)
                
                # 3. Bollinger Bands Signal (40% weight)
                price = window['Close'].iloc[-1]
                bb_upper = window['Bollinger_Upper'].iloc[-1]
                bb_lower = window['Bollinger_Lower'].iloc[-1]
                bb_width = bb_upper - bb_lower
                
                if price < bb_lower:
                    signals.append(1)
                    confidences.append(min((bb_lower - price) / bb_width, 1.0) * 0.4)
                elif price > bb_upper:
                    signals.append(-1)
                    confidences.append(min((price - bb_upper) / bb_width, 1.0) * 0.4)
                
                # Calculate overall signal and confidence
                if signals:
                    # Weight the signals by their confidence
                    weighted_signal = sum(s * c for s, c in zip(signals, confidences))
                    total_confidence = sum(confidences)
                    
                    if total_confidence >= confidence_threshold:
                        final_signal = 1 if weighted_signal > 0 else -1
                        data.iloc[i, data.columns.get_loc('Signal')] = final_signal
                        data.iloc[i, data.columns.get_loc('Confidence')] = total_confidence
                        
                        # Calculate entry, TP, and SL prices
                        entry_price = price
                        atr = window['ATR'].iloc[-1]
                        
                        if final_signal == 1:  # Buy signal
                            take_profit = entry_price + (atr * 2)  # 2x ATR for TP
                            stop_loss = entry_price - (atr * 1)   # 1x ATR for SL
                        else:  # Sell signal
                            take_profit = entry_price - (atr * 2)
                            stop_loss = entry_price + (atr * 1)
                        
                        data.iloc[i, data.columns.get_loc('Entry_Price')] = entry_price
                        data.iloc[i, data.columns.get_loc('Take_Profit')] = take_profit
                        data.iloc[i, data.columns.get_loc('Stop_Loss')] = stop_loss
        
        except Exception as e:
            print(f"Error calculating trading signals: {str(e)}")
        
        return data 

    def _fetch_histdata_minute_data(self, start_date=None, end_date=None):
        """
        Fetch 1-minute data from HistData.com and aggregate to desired interval
        
        Parameters:
        -----------
        start_date : datetime, optional
            Start date for data fetch
        end_date : datetime, optional
            End date for data fetch
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with OHLCV data at the specified interval
        """
        try:
            import requests
            from io import StringIO
            import zipfile
            from datetime import datetime, timedelta
            
            # Format currency pair for HistData URL (e.g., EUR/USD -> EURUSD)
            pair = f"{self.base_currency}{self.quote_currency}"
            
            # If no dates provided, get last 30 days
            if start_date is None:
                start_date = datetime.now() - timedelta(days=30)
            if end_date is None:
                end_date = datetime.now()
                
            # Create list of months to download
            months = []
            current = start_date.replace(day=1)
            while current <= end_date:
                months.append(current)
                current = (current + timedelta(days=32)).replace(day=1)
            
            all_data = []
            
            for date in months:
                # Format URL for HistData
                year = date.strftime("%Y")
                month = date.strftime("%m")
                url = f"https://www.histdata.com/download-free-forex-historical-data/?/ascii/{pair}_ASCII/1_MINUTE_QUOTES/{year}/{month}"
                
                try:
                    # Download and process data
                    response = requests.get(url)
                    if response.status_code == 200:
                        # Process the CSV data
                        df = pd.read_csv(StringIO(response.text), 
                                       names=['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume'],
                                       parse_dates=['DateTime'])
                        
                        # Filter by date range
                        df = df[(df['DateTime'] >= start_date) & (df['DateTime'] <= end_date)]
                        
                        all_data.append(df)
                        
                except Exception as e:
                    print(f"Error downloading data for {year}-{month}: {str(e)}")
                    continue
            
            if not all_data:
                raise Exception("No data could be downloaded from HistData")
                
            # Combine all data
            data = pd.concat(all_data)
            
            # Resample to 45-minute intervals
            if self.interval == '45min':
                data.set_index('DateTime', inplace=True)
                resampled = data.resample('45T').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
                return resampled.reset_index()
            
            return data
            
        except Exception as e:
            print(f"Error fetching data from HistData: {str(e)}")
            return None
    
    def fetch_data(self, start_date=None, end_date=None):
        """
        Fetch forex data for the specified currency pair and interval
        
        Parameters:
        -----------
        start_date : str or datetime, optional
            Start date for data fetch (default: None)
        end_date : str or datetime, optional
            End date for data fetch (default: None)
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with OHLCV data
        """
        try:
            # Convert dates to datetime if they're strings
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date)
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date)
            
            # For intraday data (45min), use HistData
            if self.interval == '45min':
                data = self._fetch_histdata_minute_data(start_date, end_date)
                if data is not None:
                    return data
                    
            # Fallback to Alpha Vantage for other intervals
            # ... existing Alpha Vantage code ...
            
        except Exception as e:
            print(f"Error fetching data: {str(e)}")

            return None
