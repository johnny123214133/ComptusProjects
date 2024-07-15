import time
import requests
import pymysql
import configparser
import sys

# a function to gather config vars from a config file
def get_config_dict(config_file_path):
	config = configparser.RawConfigParser()
	config.read(config_file_path)
	if not hasattr(get_config_dict, 'config_dict'):
		get_config_dict.config_dict = dict(config.items('CREDENTIALS'))
	return get_config_dict.config_dict

config_vars = get_config_dict('credentials.cfg')

# type conversion between python float and mysql decimal
conversions = pymysql.converters.conversions
conversions[pymysql.FIELD_TYPE.DECIMAL] = lambda x: float(x)

# a function to connect to a mysql database
def connect():
	return pymysql.connect( 
		host=config_vars['host'], 
		user=config_vars['user'],  
		password=config_vars['password'], 
		db=config_vars['database'], 
	)

# define a table to persist market data into if it doesn't exist already
conn = connect()
try:
	cur = conn.cursor()
	stmt = """
		create table if not exists marketData(
			id int not null auto_increment primary key,
			coin_id varchar(255) not null,
			name varchar(255) not null,
			symbol varchar(255) not null,
			current_price decimal(20,11) not null,
			market_cap decimal(25,11) not null,
			volume_one_day decimal(25,11) not null,
			percentage_change_one_hour decimal(20,11) not null,
			percentage_change_one_day decimal(20,11) not null,
			percentage_change_one_week decimal(20,11) not null,
			timestamp datetime not null default CURRENT_TIMESTAMP
		);
	"""
	cur.execute(stmt)
except Exception as e:
	print(e)
	conn.close()
	# if a problem occurred here, there is no point in 
	# continuting execution as nothing will be persisted.
	# so let's just report the error and exit
	sys.exit(1)
finally:
	conn.close()

"""
coin gecko has a 10000 monthly api call cap on their free demo tier.
to get all the data we want at any given time, 2 calls are needed.
10000 / 2 / 31 / 24 gives us about 6 calls an hour, so ping every 10 minutes.
this leaves a little over 1000 extra calls per month.
"""

# the coins and time frames for data we want to request from coin gecko
ids = ['bitcoin', 'ethereum', 'binancecoin', 'solana']
windows = ['1h', '24h', '7d']

def join_list(l) : 
	return ','.join(l)

# define request params for both price and market data endpoints.
# as there are overlapping fields, 
# I'll use lists to filter for the appropriate params for each call
params = {
	'vs_currency' : 'usd',
	'vs_currencies' : 'usd',
	'ids' : join_list(ids),
	'price_change_percentage' : join_list(windows),
	'precision' : 'full',
	'include_24hr_vol' : 'true'
}

# list of params keys
market_param_keys = ['vs_currency', 'ids', 'price_change_percentage', 'precision']
price_param_keys = ['vs_currencies', 'ids', 'precision', 'include_24hr_vol']

# price and market data enpoints
market_url = 'https://api.coingecko.com/api/v3/coins/markets'
price_url = 'https://api.coingecko.com/api/v3/simple/price'

# filter params for the appropriate params for each endpoint
market_params = {key : value for key, value in params.items() if key in market_param_keys}
price_params = {key : value for key, value in params.items() if key in price_param_keys}

# a list of the fields we want to save from the market data response object
desired_keys = [
	'id',
	'name',
	'symbol',
	'current_price',
	'market_cap',
	'usd_24h_vol',
	'price_change_percentage_1h_in_currency',
	'price_change_percentage_24h_in_currency',
	'price_change_percentage_7d_in_currency',
]

# function for calling coin gecko's endpoints with query params
def get_api_data(base_url, params) : 
	headers = {
		'accept': 'application/json',
		'x-cg-demo-api-key': config_vars['api_key']
	}
	return requests.get(base_url, headers=headers, params=params).json()

def get_current_market_data(market_url, market_params, price_url, price_params, output_keys):
	# fetch data from coin gecko
	market_api_response = get_api_data(market_url, market_params)
	market_data = get_api_data(price_url, price_params)

	# transform market endpoint response data to a usable state
	market_dict = dict([(item['id'], item) for item in market_api_response])
	
	# combine the price and market response data
	for key in market_data.keys():
		market_data[key].update(market_dict[key])

	# filter out undesired fields in response
	for key in market_data.keys():
		market_data[key] = dict([(k, v) for k,v in market_data[key].items() if k in output_keys])

	return market_data

# a function to persist the market and price data at a given moment
def save(data):
	conn = connect()
	try:
		cur = conn.cursor()
		stmt = f"""
			insert into marketData(
				coin_id,
				name,
				symbol,
				current_price,
				market_cap,
				volume_one_day,
				percentage_change_one_hour,
				percentage_change_one_day,
				percentage_change_one_week
			)
			values (
			"{data['id']}",
			"{data['name']}",
			"{data['symbol']}",
			{data['current_price']},
			{data['market_cap']},
			{data['usd_24h_vol']},
			{data['price_change_percentage_1h_in_currency']},
			{data['price_change_percentage_24h_in_currency']},
			{data['price_change_percentage_7d_in_currency']}
			);
		"""
		cur.execute(stmt)
		conn.commit()
	except Exception as e:
		print(e)
	finally:
		conn.close()

# the function that regularly gets and saves market data for the parameters
# defined above
def run():
	# run indefinitely
	while(True):
		market_data = get_current_market_data(market_url, market_params, price_url, price_params, desired_keys)
		for _, item in market_data.items():
			save(item)
		time.sleep(600) # wait 10 minutes between api calls

if __name__ == '__main__':
	run()


