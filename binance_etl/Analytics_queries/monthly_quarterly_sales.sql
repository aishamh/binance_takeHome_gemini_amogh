--Question: Monthly, quarterly and yearly volume for items that have 10 million+ in volume over the past year?
with 10m_plus as
(
	select ticker_key,sum(volume) as ref
	from fct_candles1m
	having sum(volume) >= 10000000
)

select ticker,yr_num,yr_mth_name,yr_qte_name,sum(volume) --these attributes are constructed as part of dim_date table.
from (select * from fct_candles1m where ticker_key in (select distinct ticker_key from 10m_plus)) fc 
join dim_date (on dd.date_key = fc.date_key and dd.time_key = fc.time_key)
join dim_ticker dt on fc.ticker_key = dt.ticker_key
group by 1,2,3,4
order by 1,2,3,4 
