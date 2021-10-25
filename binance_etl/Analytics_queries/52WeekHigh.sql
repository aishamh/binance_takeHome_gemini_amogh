--Question: What is the 52 week high and low for all the items sold in the past 3 months?
with orders_sold as 
(
	select
	from fct_Accountorders fao join dim_status ds
	on fao.status_key = ds.status_key and lower(ds.status_key) = 'sold'
)