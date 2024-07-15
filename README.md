# ComptusProjects
Take home projects for Comptus Tech job interview.

Assuming you have the required modules installed for both projects...

### To run the web scraper:
`cd web_scraper`
create or provide a mysql database to persist data into
Fill out `credentials.cfg`
`python3 scraper.py`

### To run the strategy analysis:
copy `BTC_1.feather` into `trading_strategy_analysis`
`cd trading_strategy_analysis`
`python3 williams_fractal_trading_simulator.py`
