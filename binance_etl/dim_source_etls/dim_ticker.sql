CREATE TABLE IF NOT EXISTS binance_dw.dim_ticker
(
	 ticker_key INTEGER NOT NULL  
	,ticker_symbol VARCHAR(10)   ENCODE lzo
	,ticker_symbol_desc VARCHAR(10)   ENCODE lzo
)
DISTSTYLE ALL
SORTKEY (ticker_key)
;