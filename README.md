ETL Design to get data from binance api (https://python-binance.readthedocs.io/en/latest/binance.html)
--------------------
Problem Statement: 
--------------------
Write a script (python/similar) to export data from https://www.binance.com/ for the trading pairs
BTC-USD.
1. With 1 minute candles grain and store it into the assumed Data Lake. Refer Binance API
clients for this task.
Required columns in the output are:
● Trading Pair,Open Price,Close Price,High Price,Low Price,BTC Volume,USD
Volume,Number of Trades,Candle Open Time,Candle Close Time

2. Get Account orders for the same trading pair for a sample size (500 to 1000 limit OR for
a 15 minute period, as the volume will be high).
Required columns in the output are:
● Symbol, OrderID, Price, OrigQty, ExecutedQty, status, type, side

---------------
Design Process:
---------------
 - For the designing such ETL(s) in either bath (1 hour intervals cadence in my current design) or near real time (a bit delay) , I have choosen my tech stack as AWS (Amazon web services). The ETL flow can be depicted in the following arch. design.


![image](https://user-images.githubusercontent.com/11287901/138637271-6f5e16d6-b307-4b52-a4de-0474ec49eb5d.png)


Notes from the above architecture:
1. All the above mentioned aws services/resources are deployed using CDK (Cloud development kit - https://aws.amazon.com/blogs/developer/getting-started-with-the-aws-cloud-development-kit-and-python/) via code commit and code pipeline i.e. the developer can commit the code to git and the pipeline build the artifacts and deploys the cloudformation changeset (internaly converts to .yml config file) into the beta and prod aws accounts. In a nutshell the workflow would look like:
 
 ![image](https://user-images.githubusercontent.com/11287901/138632517-6711e5a1-bdfe-45a9-b84d-35176b03a591.png)

2. With that being said, I would like to dig a bit into the code, the entry point to the program is app.py (can be found here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/app.py), which instantiates two classes BinancePipelineStack (Codepipeline, code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/binance_cicd.py) and s3Infra (code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/s3infra.py).
3. These two stack will create all the necessary code pipelines and sadd in stages to the pipelines, also creates the Datalake (s3 objects) necessary to store the candles and accountOrders data from binance apis.
4. The S3Infra stack initializes the lambda stack, which contains the lambda funtions, which inturn calls the binance apis to downloads the data (for more details, please scroll down to dissection of the lambda code) (code for lambda stack is here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/binanceLambdaInfra.py) Note that this lambda is deployed in a separeate VPC using tight bound security groupd, ingress and outbound rules (code can be found here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/vpc.py)
5. The S3Infra stack also initializes a state machine aka step functions (code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/stateMachine.py), which runs in the intervals of 5 mins each, invoking the lamndas (accountOrders and candles data at 1m grain), the S3Infra stack also initializes the glue db and the scripts necessary to perform the etl(s) and store the data in dataLake. (for more details, please scroll down to glue-etl code dissection section) (code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/gluedb_ETL.py).
6. Finally the commands used to run the cdk stacks are:
    cdk synth
    cdk deploy (to beta/developer/burner account for testing)
    
    for prod:
    All these done on feature branch
    1. git status 
    2. git commit -m "Commit message"
    3. Code review (if needed)
    4. git pull --rebase
    5. git push 
    This workflow triggers code deploy pipeline in aws to beta account and then to prod account.
    For code deploy refer binance_cicd.py.
 
 In summary, the step function running at 5 min intervals invokes the candle1mgrain and accountOrders data, which calls the apis (get_klines and get_all_orders) and ushes the data to raw folder (partitioned by year, month, day and hour) of the data lake. Any failure to call the api due to bandwidth issue or some internal server call error (500, 404 etc.), the calls are dead letter queued (see picture 1) in a SQS queue and retried upto 3 times (code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/binanceLambdaInfra.py#L47). Once the data is in s3 buckets (raw folders) Airflow jobs picks up the process, which is detailed out in the below section
 
 ---------------
 Aiflow Process
 ---------------
 Note: for setup please refer to Airflow architecture and setup section below.
 
 The Airflow process can be depicted as shown below: 
 
 ![image](https://user-images.githubusercontent.com/11287901/138631515-e22a5a3a-9541-4594-9ab9-7878df4d9c0c.png)

Codebase to airflow: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_airflow/binance_airflow_dag.py
 1. The airflow dags is triggered every one hours (identified by a cron time 0 * * * *) and the airflow task (binance_candle_grains (s3 sensor) and binance_orderdata (s3 sensor)) senses for the folder pertaining to that hour of interest in the raw paritions data lake, for example: let's say the airflow dag gets triggered at 12 PM, then the s3 prefix sensor searches for the _SUCCESS file in binanceInputFeedsRaw/candles-raw/year=2021/month=10/day=24/hour=12 or binanceInputFeedsRaw/orders-raw/year=2021/month=10/day=24/hour=12. Code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_airflow/binance_airflow_dag.py#L201-L222
 2. Then the airflow leverages pythonOperator and kicks of the glue crawlers pertaining to accountOrders and candles-grain data in their respective partitions (code: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_airflow/binance_airflow_dag.py#L227-L238 , https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_airflow/binance_airflow_dag.py#L141-L162) and prepares the glue tables under the database binance_raw_data (as defined in the cdk here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/gluedb_ETL.py#L31-L84)
 3. Finally Glue etl job (Design choice: could have gone for databricks as well, but glue etl is fully managed and was easier for clusters to warm up, I am give 10 slave nodes, as per here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/gluedb_ETL.py#L132-L158) is kicked off by airflow, that reads the raw files from candles and accountorders and stores it as a parquet format (efficient for fast I/O reads, better compressions hence went with this file format).
 4. Once the glue etl runs, the data in s3 (cooked folder) is exposed as a specturm table, which can be read from this raw data to construct facts and dimensions (which is detailed out in the ETL processing section :) ). 


------------------------------
Dissection of the lambda code
------------------------------
1. The lambda handlers for accountOrders (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/accountHandler.py) and candle-grains (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/candles1mHandler.py) are the entry points to the program that is kicked off by step functions in 5 min. intervals.
2. I have modularized the code into binanceClient module, which has the methods for getting the data, this class is initialized here (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/candles1mHandler.py#L18). Then, the response (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/candles1mHandler.py#L23) is a json object, in case of the failures, it is dead letter queued into an SQS queue and retied for 3 times or the lambda times out (15 mins) whichever occurs first; before being tombstoned.
3. The json objectis written to a file and store in the raw s3 key of the data lake (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/candles1mHandler.py#L27-L33).
4. The binanceClien.py file (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/binanceClient.py) is a class that has methods _klines_using_binance_client (using the api from the binance official documentation) and _klines (using request library) , the code can be found here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/binanceClient.py#L29-L150.
5. Finally all the constants are stored in the consts.py file (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/constants.py), Note: that I am using aws secrets manager to store the api_key and the api_secret (code is here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/constants.py#L25-L48) (cdk code is here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/s3infra.py#L40-L45).

--------------------------------
Airflow architecture and setup
--------------------------------
I have setup my airflow locally (pseudo mode, single machine), where my local desktop acts as all the 3 - webserver , scheduler and worker and persists the metadata to sqllite db. 
But ideally the way I would setup in the prod environment as follows (depicted in the below architecture). Or I would use MWAA (Manager airflow on aws) or on astronomer (https://www.astronomer.io/managed-airflow-service?utm_term=astronomer%20airflow&utm_campaign=Apache+Airflow+New+Ads&utm_source=adwords&utm_medium=ppc&hsa_acc=4274135664&hsa_cam=14735211258&hsa_grp=130506078387&hsa_ad=549925325240&hsa_src=g&hsa_tgt=kwd-829224476570&hsa_kw=astronomer%20airflow&hsa_mt=p&hsa_net=adwords&hsa_ver=3&gclid=Cj0KCQjwiNSLBhCPARIsAKNS4_cibClZB5jZ3sLSPItoFZuASs4YDI659tyytVvvfuR3OgXxDoxpthMaAuEVEALw_wcB). 

![image](https://user-images.githubusercontent.com/11287901/138636775-51ef53c6-829e-4f3d-8a29-77530be420bd.png)


--------------------------------
Problem statement 2. ETL Design
--------------------------------
Based on the raw data extracted from the previous section, come up with the ETL design to
ingest and maintain this data in the Data Lake and the DWH. Design a sample schema based
on this data to facilitate any analysis and answer the sample queries mentioned below.


-----------------
Design Process:
----------------
To help answer some of the questions listed above, I have constructed a star schema in reshift using the raw tables extracted from the problem statement 1. Below is the schema.

1. The star schema for accountOrders is as follows:
![image](https://user-images.githubusercontent.com/11287901/138753541-dc56481f-e6c5-4607-8eba-baa45b2d3760.png)

The specturm table definitions for the raw tables are here: https://github.com/amogh147/binance_takeHome_gemini_amogh/tree/main/binance_etl/object_defs
The dim table definitions are here: https://github.com/amogh147/binance_takeHome_gemini_amogh/tree/main/binance_etl/dim_source_etls
The fact table definitions are here: https://github.com/amogh147/binance_takeHome_gemini_amogh/tree/main/binance_etl/fct_source_etls.sql

2. The star schema for klines (Candles at 1m grain is here) is as shown below:
![image](https://user-images.githubusercontent.com/11287901/138754480-9b5027e7-55f2-4d22-97ef-8c50975359dc.png)

The definitions of the tables are same as mentioned above.

Answers to some questions:
1. List all the components involved in ETL strategy, refresh type, refresh frequency,
tools/technologies, etc - Airflow , redshift , refreshed on an hourly basis. refresh type: Upsert (update and insert)

2. Define the strategy for streaming data and batch data coming in from this source for
historical and near-real time analysis - Same as above, for streaming I would use kinesis firehose send the streams to sqs and store the data in data lake using lambda.

3. Sample model/schema with Facts and Dimensions to help answer below sample
questions - same as in the above section. 

4. All the assumptions are detailed in the code comment section. 

-------------------------------------------
How are these star schemas updated:
-------------------------------------------
Again I would use airflow with Pg8kOperator (raw code below) and update all the facts and dimensions and warp it around an airflow dag.

Operator pseudo code:
try:
            pg_hook = Pg8kHook(cluster_to_monitor)
            pg_conn = pg_hook.get_conn()
        except Exception as e:
            raise Exception('Database connection error:' + str(e))
        pg_conn.autocommit = False
        pg_cursor = pg_conn.cursor()
        try:
            pg_cursor.execute(kwargs['templates_dict']['sql'])
        except Exception as e:
            raise Exception("Query execution failed: " + str(e))
        query_output = pg_cursor.fetchall()

--------------------
Analytical Queries
--------------------
1. What is the 52 week high and low for all the items sold in the past 3 months?
Code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_etl/Analytics_queries/52WeekHigh.sql
2. What is the high/low price/volume in the past 2 hours?
 Code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_etl/Analytics_queries/highLwPriceVolume.sql
3. What is the volume for a given timeframe?
Code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_etl/Analytics_queries/volume_timeFrame.sql
4. Monthly, quarterly and yearly volume for items that have 10 million+ in volume over the
past year?
Code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_etl/Analytics_queries/monthly_quarterly_sales.sql
