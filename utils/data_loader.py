import yfinance as yf
import pandas as pd
import os
pd.set_option('display.max_rows', None)    # Show all rows
pd.set_option('display.max_columns', None)
pd.set_option("display.float_format", "{:,.2f}".format)

def download_data(ticker, start_date, end_date, save_path=None):
    """
    Download OHLCV data from yfinance and optionally save as parquet.
    If parquet file already exists, load from disk instead of downloading.
    
    Args:
        ticker: str, e.g. "SPY", "RSP"
        start_date: str, e.g. "2015-01-01"
        end_date: str, e.g. "2025-01-01"
        save_path: str or None, e.g. "data/RSP.parquet"
    
    Returns:
        pd.DataFrame with columns [Open, High, Low, Close, Volume]
    """
    if save_path and os.path.exists(save_path):
        print(f"Loading from cache: {save_path}")
        return pd.read_parquet(save_path)

    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    df.columns = df.columns.droplevel(1)
    
    if save_path:
        df.to_parquet(save_path)
        print(f"Saved to {save_path}")
    
    return df

#test = download_data("RSP", "2015-01-01", "2025-01-01", save_path="C:\\Users\\nic\\Desktop\\py\\data\\RSP.parquet")
#print(test.head())