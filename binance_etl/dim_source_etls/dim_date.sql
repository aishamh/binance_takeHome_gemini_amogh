--Note: the compression types are got by running analyze spectrum.binance_accountOrders_datafeed_raw/spectrum.binance_candles1m_datafeed_raw
CREATE TABLE IF NOT EXISTS binance_dw.dim_date
(
	 date_key INTEGER NOT NULL 
	,time_key  INTEGER NOT NULL
	,date_value DATE   ENCODE lzo
	,time_value DATE   ENCODE lzo
	,opentime TIMESTAMP WITHOUT TIME ZONE NOT NULL  ENCODE lzo
	,closetime TIMESTAMP WITHOUT TIME ZONE NOT NULL  ENCODE lzo
	,date_format_us VARCHAR(10)   ENCODE lzo
	,date_format_eu VARCHAR(10)   ENCODE lzo
	,display_date_dd_mon_yyyy VARCHAR(11)   ENCODE lzo
	,mth_name VARCHAR(10)   ENCODE lzo
	,qtr_name VARCHAR(2)   ENCODE lzo
	,yr_mth_name VARCHAR(8) NOT NULL  ENCODE lzo
	,yr_qtr_name VARCHAR(7)   ENCODE lzo
	,yr_num NUMERIC(4,0)   ENCODE lzo
	,day_num_in_wk NUMERIC(1,0)   ENCODE lzo
	,day_num_in_mth NUMERIC(2,0)   ENCODE lzo
	,day_num_in_yr NUMERIC(3,0)   ENCODE lzo
	,wk_num_in_yr NUMERIC(2,0)   ENCODE lzo
	,mth_num_in_yr NUMERIC(2,0)   ENCODE lzo
	,qtr_num_in_yr NUMERIC(1,0)   ENCODE lzo
	,wk_start_date DATE   ENCODE lzo
	,wk_end_date DATE   ENCODE lzo
	,wk_start_flag VARCHAR(1)   ENCODE lzo
	,mth_start_flag VARCHAR(1)   ENCODE lzo
	,qtr_start_flag VARCHAR(1)   ENCODE lzo
	,yr_start_flag VARCHAR(1)   ENCODE lzo
	,mth_end_date DATE   ENCODE lzo
	,wkd_flag VARCHAR(1)   ENCODE lzo
	,dw_creation_date TIMESTAMP WITHOUT TIME ZONE NOT NULL  ENCODE lzo
	,dw_last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL  ENCODE lzo
	,dw_created_by VARCHAR(75) NOT NULL  ENCODE lzo
	,dw_updated_by VARCHAR(75) NOT NULL  ENCODE lzo
	,days_in_mth_ct NUMERIC(3,0) NOT NULL DEFAULT 0 ENCODE lzo
	,mth_key INTEGER   ENCODE lzo
	,day_of_week CHAR(3)   ENCODE lzo
	,prev_month_key INTEGER   ENCODE lzo
	,day_num_in_qtr NUMERIC(3,0) NOT NULL DEFAULT 0 ENCODE lzo
	,week_key INTEGER NOT NULL DEFAULT -2 ENCODE lzo
	,qtr_key INTEGER NOT NULL DEFAULT -2 ENCODE lzo
	,year_key INTEGER NOT NULL DEFAULT -2 ENCODE lzo
	,prev_yr_dt_key INTEGER  DEFAULT -1 ENCODE lzo
	,prev_mth_dt_key INTEGER  DEFAULT -1 ENCODE lzo
	,prev_qtr_dt_key INTEGER  DEFAULT -1 ENCODE lzo
	,PRIMARY KEY (date_key)
)
DISTSTYLE ALL
SORTKEY (date_key)
;