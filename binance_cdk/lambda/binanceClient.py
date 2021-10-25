import constants
import time
import json
import hmac
import hashlib
import requests
from urllib.parse import urljoin, urlencode
import binance.exceptions
from binance.client import Client
from pip._internal import main as pipmain

pipmain(['install', 'python-binance'])

class binanceClient(object):
	'''
	class that encapsulats the implementation of methods that gets the candle_grains1m and account orders data.

	Note: I have implemented the methods using both request library and the binance client apis documented under:
	https://python-binance.readthedocs.io/en/latest/binance.html
	'''

	def __init__(self):
		client = Client(constants.api_key.value, constants.api_secret.value , tld = 'us')

	def __repr__(self): #Abstract method incase if we want to represent the object of this class as a representable string.
		pass
	
	@classmethod
	def _klines_using_binance_client(cls):
		#Initialize the constructor to binance client.
		client = cls.client
		client.API_URL = constants.api_endpoint.value+'/api'
		params = constants.klines_params.value
		
		return [{
			"Trading Pairs" : "BTCUSDT",
			"openTime": d[0],
			"open": d[1],
			"high": d[2],
			"low": d[3],
			"close": d[4],
			"volume": d[5],
			"closeTime": d[6],
			"quoteVolume": d[7],
			"numTrades": d[8],
			"Taker buy": d[9],
			"Taker buy quote": d[10],
			"_": d[11]
		} for d in client.get_klines(**params)]

	
	def _klines(self) -> json data: #This is the implementation using request library.
		"""Get kline/candlestick bars for a symbol.

		Klines are uniquely identified by their open time. If startTime and endTime
		are not sent, the most recent klines are returned.

		Args:
			symbol (str)
			interval (str)
			limit (int, optional): Default 500; max 500.
			startTime (int, optional)
			endTime (int, optional)

		"""
		
		headers = {
			'X-MBX-APIKEY': constants.api_secret.value #got from aws secret manager
		}
		
		url = urljoin(constants.api_endpoint.value, constants.klines_api_relative_path.value)
		r = requests.get(url, params=constants.klines_params.value)
		if r.status_code == 200:
			data = r.json()
		else:
			raise BinanceException(status_code=r.status_code, data=r.json())

		return [{
			"Trading Pairs" : "BTCUSDT"
			"openTime": d[0],
			"open": d[1],
			"high": d[2],
			"low": d[3],
			"close": d[4],
			"volume": d[5],
			"closeTime": d[6],
			"quoteVolume": d[7],
			"numTrades": d[8],
			"Taker buy": d[9],
			"Taker buy quote": d[10],
			"_": d[11]
		} for d in data]


	def _get_all_orders(self) -> json data: #This is the implementation using request library.
		"""
		Get orders for a symbol.

		Args:
			symbol (str)
			orderid (int)
			startTime (int, optional)
			endTime (int, optional)
			limit (int, optional): Default 500; max 1000.
			recvWindow (int , optional)
			timestamp (int , required )
			signature (query , required)

		"""
		
		headers = {
			'X-MBX-APIKEY': constants.api_secret.value #got from aws secret manager
		}
		
		url = urljoin(constants.api_endpoint.value, constants.accountOrders_api_relative_path.value)
		r = requests.get(url, params=constants.accountOrders_Params.value)
		if r.status_code == 200:
			data = r.json()
		else:
			raise BinanceException(status_code=r.status_code, data=r.json())

		return [{
			"symbol" : d[0],
			"orderId" : d[1],
			"price" : d[4],
			"origQty" : d[5],
			"executedQty" : d[6],
			"status" : d[8],
			"type" : d[10],
			"side" : d[11],
		} for d in data]


	@classmethod
	def _get_all_orders_using_binance_client(cls):
		#Initialize the constructor to binance client.
		client = cls.client
		client.API_URL = constants.api_endpoint.value+'/api'
		params = constants.accountOrders_Params.value
		
		return [{
			"symbol" : d[0],
			"orderId" : d[1],
			"price" : d[4],
			"origQty" : d[5],
			"executedQty" : d[6],
			"status" : d[8],
			"type" : d[10],
			"side" : d[11],
		} for d in client.get_all_orders(**params)]
	