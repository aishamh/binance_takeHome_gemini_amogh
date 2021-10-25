CREATE TABLE IF NOT EXISTS binance_dw.dim_side
(
	 side_key INTEGER NOT NULL  
	,side VARCHAR(10)   ENCODE lzo
	,side_desc VARCHAR(10)   ENCODE lzo
)
DISTSTYLE ALL
SORTKEY (side_key)
;