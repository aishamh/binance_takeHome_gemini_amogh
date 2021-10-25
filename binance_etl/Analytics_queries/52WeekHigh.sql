--Question: What is the 52 week high and low for all the items sold in the past 3 months?

select max(52week_high) as 52week_high, min(52week_low) as 52week_low
from fct_candles1m fc join dim_status ds
(on fc.status_key = ds.status_key and lower(ds.status_key) = 'sold')
join dim_date on (dd.date_key = fc.date_key)
where datediff(months, dd.date_value, current_date) <= 3
