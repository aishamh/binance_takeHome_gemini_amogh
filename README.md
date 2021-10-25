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


![image](https://user-images.githubusercontent.com/11287901/138631515-e22a5a3a-9541-4594-9ab9-7878df4d9c0c.png)

Notes from the above architecture:
1. All the above mentioned aws services/resources are deployed using CDK (Cloud development kit - https://aws.amazon.com/blogs/developer/getting-started-with-the-aws-cloud-development-kit-and-python/) via code commit and code pipeline i.e. the developer can commit the code to git and the pipeline build the artifacts and deploys the cloudformation changeset (internaly converts to .yml config file) into the beta and prod aws accounts. In a nutshell the workflow would look like:
 
 ![image](https://user-images.githubusercontent.com/11287901/138632517-6711e5a1-bdfe-45a9-b84d-35176b03a591.png)

2. With that being said, I would like to dig a bit into the code, the entry point to the program is app.py (can be found here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/app.py), which instantiates two classes BinancePipelineStack (Codepipeline, code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/binance_cicd.py) and s3Infra (code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/s3infra.py).
3. These two stack will create all the necessary code pipelines and sadd in stages to the pipelines, also creates the Datalake (s3 objects) necessary to store the candles and accountOrders data from binance apis.
4. The S3Infra stack initializes the lambda stack, which contains the lambda funtions, which inturn calls the binance apis to downloads the data (for more details, please scroll down to dissection of the lambda code) (code for lambda stack is here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/binanceLambdaInfra.py) 
5. The S3Infra stack also initializes a state machine aka step functions (code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/stateMachine.py), which runs in the intervals of 5 mins each, invoking the lamndas (accountOrders and candles data at 1m grain), the S3Infra stack also initializes the glue db and the scripts necessary to perform the etl(s) and store the data in dataLake. (for more details, please scroll down to glue-etl code dissection section) (code here: https://github.com/amogh147/binance_takeHome_gemini_amogh/blob/main/binance_cdk/py_cdk/gluedb_ETL.py).
6. Finally the commands used to run the cdk stacks are:
    cdk synth
    cdk deploy (to beta/developer/burner account for testing)
    
    for prod:
    All these done on feature branch
    1. git status 
    2. git commit -m "<Commit message>"
    3. Code review (if needed)
    4. git pull --rebase
    5. git push 
    This workflow triggers code deploy pipeline in aws to beta account and then to prod account.
    For code deploy refer binance_cicd.py.
 



