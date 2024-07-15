import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

from simple_backtester import simple_backtest
from data_manager import *

df = get_data()

# three EMAs are needed for the williams fractal strategy
df['twenty_ema'] = get_ema_close(df, window=20)
df['fifty_ema'] = get_ema_close(df, window=50)
df['one_hundred_ema'] = get_ema_close(df, window=100)

# Williams fractals are needed for the strategy.
# I've marked both bullish and bearish fractals, 
# but only the bullish fractals are used 
# since the backtester only tracks long positions and not both long and short
def mark_fractals(signal):
	bull = []
	bear = []
	
	for i in range(len(signal)):
		bull.append(np.nan)
		bear.append(np.nan)
	
	for i in range(5, len(signal)):
		minimum = signal.Low[i - 3]
		if minimum < signal.Low[i - 5] and minimum < signal.Low[i - 4] and minimum < signal.Low[i - 2] and minimum < signal.Low[i - 1]:  
			bull[i - 3] = minimum
		
		maximum = signal.High[i - 3]
		if maximum > signal.High[i - 5] and maximum > signal.High[i - 4] and maximum > signal.High[i - 2] and maximum > signal.High[i - 1]:  
			bear[i - 3] = maximum
			
	return (bull, bear)

fractal = mark_fractals(df)
df['bull'] = fractal[0]
df['bear'] = fractal[1]

# a function that runs the trade simulation for long positions
# on the data and indicators defined above
# and blocks new trdes during active trades
# target is the tp tosl ratio
def simulate_trades(df, target=1.5): 
	# at least 102 datapoints are needed for the indicators to operate correctly
	if len(df) < 102 : 
		return None
	
	active_trade = False
	timestamps = []
	signals = []

	# let 100 ema catch up, and williams fractals require the following two candles
	for i in range(100, len(df) - 2): 
		if active_trade:
			if df.High[i] >= take_profit or df.Low[i] < stop_loss: 
				# complete the trade once tp or stop loss is met/exceeded
				# record the sell time and signal
				timestamps.append(df.Time[i])
				signals.append(-1)
				active_trade = False
		else:
			# hunt long positions if the emas line up for a swing high pattern
			if df.twenty_ema[i] > df.fifty_ema[i] > df.one_hundred_ema[i]:
				# our position, take profit, and stop loss changes depending on which EMAs the fractal occurs between
				if df['bull'][i] <= df.twenty_ema[i] and df['bull'][i] > df.fifty_ema[i]:
					# fractal is between the 20 and 50 EMA
					i += 2 # trade opens after the fractal is marked
					active_trade = True
					stop_loss = df.fifty_ema[i]
					diff = abs(df.Close[i] - stop_loss)
					take_profit = df.Close[i] + (diff * target)
					# record the buy time and signal
					timestamps.append(df.Time[i])
					signals.append(1)

				elif df['bull'][i] <= df.fifty_ema[i] and df['bull'][i] > df.one_hundred_ema[i]:  
					# fractal between 50 and 100 EMA
					i += 2 # trade opens after the fractal is marked
					active_trade = True
					stop_loss = df.one_hundred_ema[i]
					diff = abs(df.Close[i] - stop_loss)
					take_profit = df.Close[i] + (diff * target)
					# record the buy time and signal
					timestamps.append(df.Time[i])
					signals.append(1)

	# delete trailing buy signal, if present
	if signals[-1] == 1: 
		signals = signals[:-1]
		timestamps = timestamps[:-1]
	return timestamps, signals

timestamps, signals = simulate_trades(df, 1.5)

# run the backtester with the result of the simulator and print the results
result = simple_backtest(df, timestamps, signals)
print(result)

