import yfinance as yf
import requests
import pandas as pd
from datetime import datetime

# Define Yahoo Finance tickers for BTC and ETH
tickers = {
    'Bitcoin': 'BTC-USD',
#    'Ethereum': 'ETH-USD',
}

# Function to fetch BTC and ETH data from Yahoo Finance
def fetch_yahoo_data(tickers, period='1mo', interval='1d'):
    data = {}
    for name, ticker in tickers.items():
        print(f"Fetching data for {name} from Yahoo Finance...")
        df = yf.download(ticker, period=period, interval=interval)
        df['Symbol'] = name
        data[name] = df
    print(data)
    return data

# Function to fetch Solana data from CoinGecko
def fetch_solana_data():
    print("Fetching Solana data from CoinGecko...")
    url = "https://api.coingecko.com/api/v3/coins/solana/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': '30',  # Fetch last 30 days of data
        'interval': 'daily',
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    # Process response into a DataFrame
    solana_prices = data['prices']
    solana_df = pd.DataFrame(solana_prices, columns=['timestamp', 'price'])
    solana_df['timestamp'] = pd.to_datetime(solana_df['timestamp'], unit='ms')
    solana_df.set_index('timestamp', inplace=True)
    solana_df['Symbol'] = 'Solana'
    print(solana_df)
    return solana_df

# Merge all data into a single DataFrame
def merge_data(yahoo_data, solana_data):
    yahoo_df = pd.concat(yahoo_data.values(), keys=yahoo_data.keys())
    yahoo_df = yahoo_df.reset_index(level=0).rename(columns={'level_0': 'Cryptocurrency'})
    yahoo_df.reset_index(inplace=True)
    yahoo_df.rename(columns={'index': 'Date'}, inplace=True)
    
    # Add Solana data
    solana_data.reset_index(inplace=True)
    solana_data.rename(columns={'timestamp': 'Date', 'price': 'Close'}, inplace=True)
    
    # Combine all into one DataFrame
    merged_df = pd.concat([yahoo_df[['Date', 'Close', 'Symbol']], solana_data], ignore_index=True)
    return merged_df

# Fetch and process data
yahoo_data = fetch_yahoo_data(tickers)
solana_data = fetch_solana_data()
merged_data = merge_data(yahoo_data, solana_data)

# Save to CSV (optional)
merged_data.to_csv('crypto_data.csv', index=False)

# Display the first few rows
print(merged_data.head())

##
##import yfinance as yf
##import pandas as pd
##
### Define ticker symbols
##tickers = {
##    'Bitcoin': 'BTC-USD',
###    '#Ethereum': 'ETH-USD',
##    'Solana': 'SOL-USD'
##}
##
### Fetch data
##def fetch_crypto_data(tickers, period='1mo', interval='1d'):
##    data = {}
##    for name, ticker in tickers.items():
##        print(f"Fetching data for {name}...")
##        df = yf.download(ticker, period=period, interval=interval)
##        df['Symbol'] = name
##        data[name] = df
##    return data
##
### Merge all data into a single DataFrame
##def merge_data(data):
##    merged_df = pd.concat(data.values(), keys=data.keys())
##    return merged_df.reset_index(level=0).rename(columns={'level_0': 'Cryptocurrency'})
##
### Fetch and process data
##crypto_data = fetch_crypto_data(tickers)
##merged_data = merge_data(crypto_data)
##
### Save to CSV (optional)
##merged_data.to_csv('crypto_data.csv', index=False)
##
### Display the first few rows
##print(merged_data.head())


import krakenex
import time
import pandas as pd

# Initialize Kraken API client
kraken = krakenex.API()

# Function to fetch market data for a pair
def fetch_kraken_data(pair, interval=1, since=None):
    """
    Fetch historical OHLC data for a given trading pair from Kraken.
    
    Args:
        pair (str): The trading pair (e.g., DOGEUSD, SHIBUSD).
        interval (int): Time interval in minutes (e.g., 1, 5, 15, 30, 60, 240, 1440).
        since (int): Timestamp to fetch data from (UNIX time). Default is None.
    
    Returns:
        pd.DataFrame: A DataFrame containing OHLC data.
    """
    try:
        print(f"Fetching data for {pair}...")
        response = kraken.query_public('OHLC', {'pair': pair, 'interval': interval, 'since': since})
        if 'error' in response and response['error']:
            raise Exception(f"API Error: {response['error']}")

        data = response['result'][list(response['result'].keys())[0]]  # Extract pair-specific data
        columns = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
        df = pd.DataFrame(data, columns=columns)
        df['time'] = pd.to_datetime(df['time'], unit='s')  # Convert UNIX to datetime
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

# Memecoins to fetch data for (example pairs)
pairs = ['DOGEUSD', 'SHIBUSD']  # Ensure these pairs exist on Kraken

# Fetch data for each pair
interval = 5  # 5-minute interval
all_data = {}

for pair in pairs:
    data = fetch_kraken_data(pair, interval=interval)
    if not data.empty:
        all_data[pair] = data
        # Save data to CSV (optional)
        data.to_csv(f"{pair}_data.csv", index=False)
        print(f"Data for {pair} saved to {pair}_data.csv")

# Example: Display the first few rows of DOGEUSD data
if 'DOGEUSD' in all_data:
    print(all_data['DOGEUSD'].head())
    print(all_data['SHIBUSD'].head())



##
##
##
##import krakenex
##import time
##
### Initialize Kraken API client
##api = krakenex.API()
##api.load_key('kraken_api.key')  # Save your API keys in a file (see below)
##
### Function to get account balance
##def get_balance(asset):
##    response = api.query_private('Balance')
##    if 'error' in response and response['error']:
##        print(f"Error fetching balance: {response['error']}")
##        return None
##    return float(response['result'].get(asset, 0))
##
### Function to place an order
##def place_order(pair, side, volume, price=None, order_type='limit'):
##    """
##    Place a buy/sell order.
##    """
##    order = {
##        'pair': pair,
##        'type': side,  # 'buy' or 'sell'
##        'ordertype': order_type,  # 'limit' or 'market'
##        'volume': str(volume),
##    }
##    if price and order_type == 'limit':
##        order['price'] = str(price)
##    
##    response = api.query_private('AddOrder', order)
##    if 'error' in response and response['error']:
##        print(f"Error placing order: {response['error']}")
##        return None
##    print(f"Order placed: {response['result']}")
##    return response['result']
##
### Function to monitor the price and place an order
##def automated_trading(pair, asset, side, threshold, volume):
##    """
##    Monitor the price and automate trading based on a threshold.
##    """
##    while True:
##        # Get ticker info
##        response = api.query_public('Ticker', {'pair': pair})
##        if 'error' in response and response['error']:
##            print(f"Error fetching ticker: {response['error']}")
##            break
##        
##        price = float(response['result'][list(response['result'].keys())[0]]['c'][0])  # Current price
##        print(f"Current price for {pair}: {price}")
##        
##        # Check condition
##        if (side == 'buy' and price <= threshold) or (side == 'sell' and price >= threshold):
##            print(f"Trigger met: Placing {side} order for {volume} {asset}")
##            place_order(pair, side, volume, price=threshold)
##            break
##        
##        time.sleep(10)  # Check every 10 seconds
##
### Example Usage
##if __name__ == "__main__":
##    # Save your API key in 'kraken_api.key' as:
##    # key = YOUR_PUBLIC_KEY
##    # secret = YOUR_PRIVATE_KEY
##
##    pair = 'DOGEUSD'  # Example pair
##    asset = 'DOGE'
##    side = 'buy'  # 'buy' or 'sell'
##    threshold = 0.07  # Example price threshold
##    volume = 1000  # Amount to buy/sell
##
##    automated_trading(pair, asset, side, threshold, volume)
##
##
##
##
##


























