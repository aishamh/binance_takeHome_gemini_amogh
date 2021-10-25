-- Question: What is the volume for a given timeframe?
select dd.date_value, dd.time_value, sum(volume)
from binance_dw.fct_candles1m fc join dim_date dd (on fc.date_key = dd.date_key and fc.time_key = dd.time_key)
where dd.date_value = <'Date of interest'> and dd.time_value = <'Time of interest'>
group by 1,2
order by 1,2
;