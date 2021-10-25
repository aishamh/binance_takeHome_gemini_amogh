CREATE TABLE IF NOT EXISTS binance_dw.dim_type
(
	 type_key INTEGER NOT NULL  
	,type VARCHAR(10)   ENCODE lzo
	,type_desc VARCHAR(10)   ENCODE lzo
)
DISTSTYLE ALL
SORTKEY (type_key)
;