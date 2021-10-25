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

2. Lam
