create external table spectrum.binance_accountOrders_datafeed_raw(
  "symbol" varchar(20)
, "orderId" integer
, "price" decimal(8,2)
, "origQty" decimal(8,2)
, "executedQty" decimal(8,2)
, "status" varchar(20)
, "type" varchar(20)
, "side" varchar(20)
)
STORED AS PARQUET
location 's3://binance-candle-input-1mGrain/binanceCookedDataLake/binance-curatedDataLake-orders/spectrum/accountOrders/'
;