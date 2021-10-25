CREATE TABLE IF NOT EXISTS binance_dw.dim_status
(
	 status_key INTEGER NOT NULL  
	,status VARCHAR(10)   ENCODE lzo
	,status_desc VARCHAR(10)   ENCODE lzo
)
DISTSTYLE ALL
SORTKEY (status_key)
;