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


![image](https://user-images.githubusercontent.com/11287901/138631485-47a07cef-237c-4585-a721-2c7a798eeea9.png)


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
 3. Finally Glue etl job (Design choice: could have gone for databricks as well, but glue etl is fully managed and was easier for clueters to warm up, I am give 10 slave nodes, as per here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/gluedb_ETL.py#L132-L158) is kicked off by airflow, that reads the raw files from candles and accountorders and stores it as a parquet format (efficient for fast I/O reads, better compressions hence went with this file format).
 4. Once the glue etl runs, the data in s3 (cooked folder) is exposed as a specturm table, which can be read from this raw data to construct facts and dimensions (which is detailed out in the ETL processing section :) ). 


------------------------------
Dissection of the lambda code
------------------------------
1. The lambda handlers for accountOrders (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/accountHandler.py) and candle-grains (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/candles1mHandler.py) are the entry points to the program that is kicked off by step functions in 5 min. intervals.
2. I have modularized the code into binanceClient module, which has the methods for getting the data, this class is initialized here (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/candles1mHandler.py#L18). Then, the response (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/candles1mHandler.py#L23) is a json object, in case of the failures, it is dead letter queued into an SQS queue and retied for 3 times or the lambda times out (15 mins) whichever occurs first; before being tombstoned.
3. The json objectis written to a file and store in the raw s3 key of the data lake (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/candles1mHandler.py#L27-L33).
4. The binanceClien.py file (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/binanceClient.py) is a class that has methods _klines_using_binance_client (using the api from the binance official documentation) and _klines (using request library) , the code can be found here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/binanceClient.py#L29-L150.
5. Finally all the constants are stored in the consts.py file (https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/constants.py), Note: that I am using aws secrets manager to store the api_key and the api_secret (code is here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/lambda/constants.py#L25-L48) (cdk code is here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/s3infra.py#L40-L45).
