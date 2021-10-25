CREATE TABLE IF NOT EXISTS binance_dw.fct_candles1m
(
	  ticker_key INTEGER NOT NULL 
	, date_key INTEGER NOT NULL 
	, time_key INTEGER NOT NULL 
	, status_key INTEGER NOT NULL  
	, 52week_high INTEGER NOT NULL  
	, 52week_low INTEGER NOT NULL 
	, high decimal(8,2)
	, low decimal(8,2)
	, close decimal(8,2)
	, volume decimal(8,2)
	, quoteVolume decimal(8,2)
	, numTrades integer
	, Taker buy decimal(8,2) 
	, Taker buy quote decimal(8,2)
)
DISTSTYLE KEY
DISTKEY (ticker_key , date_key)
;
