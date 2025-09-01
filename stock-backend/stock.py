import yfinance as yf
import pandas as pd
import numpy as np

class StockAnalyzer:
    def fetch_stock_data(self, symbol, start_date, end_date):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                return None
            
            # Reset index to make Date a column
            data = data.reset_index()
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            
            # Select only the core stock variables
            data = data[['Date', 'Open', 'High', 'Low', 'Close','Volume']]

            # Clean up non-finite values (still important for core variables)
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            
            return data
            
        except Exception as e:
            return None

    def align_and_merge(self, stock_data, custom_data, date_column):
        try:
            # Prepare stock data
            stock_data = stock_data.copy()
            stock_data['date'] = pd.to_datetime(stock_data['Date'], errors='coerce')
            if pd.api.types.is_datetime64tz_dtype(stock_data['date']):
                stock_data['date'] = stock_data['date'].dt.tz_localize(None)
            stock_data['date'] = stock_data['date'].dt.normalize()

            # Prepare custom data
            custom_data = custom_data.copy()
            custom_data['date'] = pd.to_datetime(custom_data[date_column], errors='coerce')
            if pd.api.types.is_datetime64tz_dtype(custom_data['date']):
                custom_data['date'] = custom_data['date'].dt.tz_localize(None)
            custom_data['date'] = custom_data['date'].dt.normalize()

            # Remove rows with invalid dates
            stock_data = stock_data.dropna(subset=['date'])
            custom_data = custom_data.dropna(subset=['date'])

            
            # Merge on date
            merged = pd.merge(stock_data, custom_data, on='date', how='inner')
            
            return merged
            
        except Exception as e:
            return pd.DataFrame()  # Return empty DataFrame on error