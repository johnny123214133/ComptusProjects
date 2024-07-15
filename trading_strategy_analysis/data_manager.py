import numpy as np
import pandas as pd

def get_data():
    """ returns the BTC_1.feather files as a pandas DataFrame with columns
    Time: Unix timestamp in milliseconds
    Open: Opening price of the candle
    High: Highest price of the candle
    Low: Lowest price of the candle
    Close: Closing price of the candle
    Volume: Volume of the candle
    
    where each candlestick lasts for 1 minute
    """
    path = "BTC_1.feather"
    df = pd.read_feather(path)
    return df

def get_readable_date(df):
    """ takes in a DataFrame with a 'Time' column and returns a pandas Series
    with the 'Time' column converted to a readable date format
    """
    return pd.to_datetime(df['Time'], unit='ms')

def get_1h_perc_change(df):
    """ takes in a DataFrame with a 'Close' column and returns a numpy array
    with the percentage change in the 'Close' column over the last 1 hour
    """
    close = df['Close'].values
    prev_1h = df['Close'].shift(60).values
    perc_change_1h = (close - prev_1h) / prev_1h
    return perc_change_1h

def get_24h_perc_change(df):
    """ takes in a DataFrame with a 'Close' column and returns a numpy array
    with the percentage change in the 'Close' column over the last 24 hours
    """
    close = df['Close'].values
    prev_24h = df['Close'].shift(60*24).values
    perc_change_24h = (close - prev_24h) / prev_24h
    return perc_change_24h

def get_7d_perc_change(df):
    """ takes in a DataFrame with a 'Close' column and returns a numpy array
    with the percentage change in the 'Close' column over the last 7 days
    """
    close = df['Close'].values
    prev_7d = df['Close'].shift(60*24*7).values
    perc_change_7d = (close - prev_7d) / prev_7d
    return perc_change_7d

def get_24h_volume(df):
    """ takes in a DataFrame with a 'date' and 'Volume' column and returns a numpy array
    with the 24-hour volume for each row in the DataFrame since the start of the day
    """
    # create a copy of the dataframe to avoid modifying the original
    df = df.copy()
    # create a mask the finds the first entry for each day
    df['date'] = pd.to_datetime(df['Time'], unit='ms')
    mask = (df['date'].dt.hour == 0) & (df['date'].dt.minute == 0)
    # calculate the cumulative volume and then subtract off the 
    # cumulative volume at the start of the day to get the 24-hour volume
    df['cumulative_volume'] = df['Volume'].cumsum()
    df['offset'] = np.nan
    df.loc[mask, 'offset'] = df.loc[mask, 'cumulative_volume'].copy()
    df['offset'] = df['offset'].ffill()
    df['24h_volume'] = df['cumulative_volume'] - df['offset']
    # return the 24-hour volume as a numpy array
    return df['24h_volume'].values

def get_ema_close(df, window=60):
    """ takes in a DataFrame with a 'Close' column and returns a numpy array
    with the exponential moving average of the 'Close' column with the given window
    """
    close = df['Close'].values
    ema = pd.Series(close).ewm(span=window).mean()
    return ema.values

def get_window_std(df, window=60):
    """ takes in a DataFrame with a 'Close' column and returns a numpy array
    with the rolling standard deviation of the 'Close' column with the given window
    """
    close = df['Close'].values
    std = pd.Series(close).rolling(window).std()
    return std.values