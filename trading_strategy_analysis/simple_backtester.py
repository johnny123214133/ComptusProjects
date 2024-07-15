import numpy as np
import pandas as pd

BUY = 1.0
SELL = -1.0

def simple_backtest(df, timestamps, signals):
    """
    Takes in a DataFrame, a list of timestamps, and a list of signals,
    and returns a dictionary with the backtest results.

    Parameters:
    df (pd.DataFrame): A DataFrame containing the following columns:
        - 'Time': Unix timestamp in milliseconds
        - 'Close': Closing price of the candlestick
    timestamps (list): A list of Unix timestamps in milliseconds that 
                       correspond to the closing time of each candlestick.
    signals (list): A list of integers representing trading signals for 
                    each timestamp. 
                    - A signal of 1 represents a buy signal
                    - A signal of -1 represents a sell signal
                    - A signal of 0 represents no action

    Returns:
    dict: A dictionary with the backtest results containing the following keys:
        - 'buy_times': Array of timestamps when buy signals were executed.
        - 'sell_times': Array of timestamps when sell signals were executed.
        - 'trade_times': Array of timestamps when trades (both buys and sells) were executed.
        - 'trade_gain_losses': Array of monetary gain or loss for each trade.
        - 'trade_perc_gain_losses': Array of percentage gain or loss for each trade.
        - 'num_wins': Total number of profitable trades.
        - 'win_rate': Proportion of profitable trades over total trades.
        - 'num_trades': Total number of trades executed.
        - 'start_portfolio_value': Initial value of the portfolio.
        - 'end_portfolio_value': Final value of the portfolio after all trades.
        - 'percentage_gain': Overall percentage gain or loss of the portfolio.
        - 'avg_perc_gain_per_trade': Average percentage gain or loss per trade.
        - 'avg_gain_loss_per_trade': Average monetary gain or loss per trade.
        - 'avg_holding_time': Average time duration between buying and selling (holding period).

    Explanation of the return dictionary keys:
        - 'buy_times': Timestamps when buy orders were executed. This helps to track when investments were made.
        - 'sell_times': Timestamps when sell orders were executed. This helps to track when investments were liquidated.
        - 'trade_times': Timestamps for both buy and sell orders. This is useful to see the sequence and timing of all trades.
        - 'trade_gain_losses': The profit or loss from each trade in monetary terms. Positive values indicate profit, and negative values indicate loss.
        - 'trade_perc_gain_losses': The profit or loss from each trade in percentage terms. This standardizes gains and losses relative to the size of the initial investment.
        - 'num_wins': The count of trades that resulted in a profit. This provides insight into the strategy's effectiveness.
        - 'win_rate': The ratio of profitable trades to the total number of trades. This is a measure of how often the strategy is successful.
        - 'num_trades': The total number of trades executed. This helps understand the frequency of trading activity.
        - 'start_portfolio_value': The initial amount of money in the portfolio before any trades were made. This is a baseline for measuring performance.
        - 'end_portfolio_value': The final amount of money in the portfolio after all trades were executed. This is the ultimate measure of the strategy's performance.
        - 'percentage_gain': The overall percentage change in the portfolio's value. This summarizes the total performance of the strategy.
        - 'avg_perc_gain_per_trade': The average percentage change in value per trade. This provides an average measure of the effectiveness of each trade.
        - 'avg_gain_loss_per_trade': The average monetary gain or loss per trade. This gives a sense of the typical profit or loss magnitude for each trade.
        - 'avg_holding_time': The average duration (in time units) between buy and sell trades. This indicates the typical investment horizon of the strategy.

    Raises:
    ValueError: If any of the provided timestamps are not present in the DataFrame.
    """
    if any([t not in df['Time'].values for t in timestamps]):
        raise ValueError("Timestamps must be in the DataFrame")
    
    # add the signals to the DataFrame by merging on the 'Time' column
    df = df.copy()
    sort_order = np.argsort(timestamps)
    timestamps = np.array(timestamps)[sort_order]
    signals = np.array(signals)[sort_order]
    signal_df = pd.DataFrame({'Time': timestamps, 'Signal': signals})
    merged_df = pd.merge(df, signal_df, how='left', on='Time')
    df_filtered = merged_df.loc[~np.isnan(merged_df['Signal']), :].copy()
    
    # initialize all of the backtest variables
    position = False
    prev_portfolio_value = 100.0
    portfolio_value = 100.0
    crypto_value = 0.0
    
    buy_times = []
    sell_times = []
    trade_times = []
    trade_gain_losses = []
    trade_perc_gain_losses = []
    wins = 0
    trades = 0
    
    # loop through the rows of the DataFrame and execute trades
    times = df_filtered['Time'].values
    closes = df_filtered['Close'].values
    signals = df_filtered['Signal'].values
    for time, close, signal in zip(times, closes, signals):
        
        # if the signal is a buy signal and the position is not already long
        if not position and signal == BUY:
            prev_portfolio_value = portfolio_value
            crypto_value = portfolio_value / close
            buy_times.append(time)
            position = True
        
        # if the signal is a sell signal and the position is long
        elif position and signal == SELL:
            portfolio_value = crypto_value * close
            position = False
            gain_loss = portfolio_value - prev_portfolio_value
            perc_gain_loss = gain_loss / prev_portfolio_value
            
            sell_times.append(time)
            trade_times.append(time)
            trade_gain_losses.append(gain_loss)
            trade_perc_gain_losses.append(perc_gain_loss)
            
            trades += 1
            if gain_loss >= 0:
                wins += 1
                
    # convert the lists to numpy arrays
    buy_times = np.array(buy_times)
    sell_times = np.array(sell_times)
    trade_times = np.array(trade_times)
    trade_gain_losses = np.array(trade_gain_losses)
    trade_perc_gain_losses = np.array(trade_perc_gain_losses)
             
    # return the backtest results and summary statistics   
    res = {
        'buy_times': buy_times,
        'sell_times': sell_times,
        'trade_times': trade_times,
        'trade_gain_losses': trade_gain_losses,
        'trade_perc_gain_losses': trade_perc_gain_losses,
        'num_wins': wins,
        'win_rate': wins / trades if trades > 0 else 0,
        'num_trades': trades,
        'start_portfolio_value': 100.0,
        'end_portfolio_value': portfolio_value,
        'percentage_gain': (portfolio_value - 100.0) / 100.0,
        'avg_perc_gain_per_trade': np.mean(trade_perc_gain_losses) if len(trade_perc_gain_losses) > 0 else 0,
        'avg_gain_loss_per_trade': np.mean(trade_gain_losses) if len(trade_gain_losses) > 0 else 0,
        'avg_holding_time': np.mean(sell_times - buy_times) if len(buy_times) > 0 and len(sell_times) > 0 else 0
    }
    return res

            
    