CREATE TABLE IF NOT EXISTS binance_dw.fct_Accountorders
(
	  
	  order_id VARCHAR(45)   ENCODE lzo
	, ticker_key INTEGER NOT NULL 
	, status_key INTEGER NOT NULL 
	, type_key INTEGER NOT NULL 
	, side_key INTEGER NOT NULL 
	, price NUMERIC(8,2)  ENCODE delta32k
	, origQty NUMERIC(8,2)  ENCODE delta32k
	, executedQty NUMERIC(8,2)  ENCODE delta32k


)
DISTSTYLE KEY
DISTKEY (order_id)
INTERLEAVED SORTKEY (status_key)
;
