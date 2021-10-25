create external table spectrum.binance_candles1m_datafeed_raw(
  "Trading Pairs" varchar(20)
, "openTime" timestamp
, "open" decimal(8,2)
, "high" decimal(8,2)
, "low" decimal(8,2)
, "close" decimal(8,2)
, "volume" decimal(8,2)
, "closeTime" timestamp
, "quoteVolume" decimal(8,2)
, "numTrades" integer
, "Taker buy" decimal(8,2) 
, "Taker buy quote" decimal(8,2)
)
STORED AS PARQUET
location 's3://binance-candle-input-1mGrain/binanceCookedDataLake/binance-curatedDataLake-candles/spectrum/candles/'
;