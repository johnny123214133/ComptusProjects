# ComptusProjects
Take home projects for Comptus Tech job interview.

For the trading strategy analysis project I used the Williams Fractal trading strategy as described in the videos [Easy 1 Minute Scalping Trading Strategy | Simple But Effective](https://www.youtube.com/watch?v=juZlrecsIts) and [Simple But Effective 1 Minute Scalping Strategy Tested 100 Trades | EMA + Fractal Indicators](https://www.youtube.com/watch?v=0Q6iENmeUys) posted by Trade Pro on YouTube.

Ensure you have the packages in `requirements.txt` installed.

### To run the web scraper:
1. `cd web_scraper`
2. create or provide a mysql database to persist data into
3. Fill out `credentials.cfg`
4. `python3 scraper.py`

### To run the strategy analysis:
1. copy `BTC_1.feather` into `trading_strategy_analysis`
2. `cd trading_strategy_analysis`
3. `python3 williams_fractal_trading_simulator.py`
