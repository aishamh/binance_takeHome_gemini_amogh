--What is the high/low price/volume in the past 2 hours?

select max(high) as high, min(low) as low
from binance_dw.fct_candles1m fc join dim_date dd (on fc.date_key = dd.date_key and fc.time_key = dd.time_key)
where (sysdate - dd.openTime::time) <= 2 or (sysdate - dd.closeTime::time) <= 2
;