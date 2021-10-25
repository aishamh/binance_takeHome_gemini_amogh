from aws_cdk import (
aws_s3 as s3,
aws_iam as iam,
aws_glue as glue, 
CfnCrawler,
CfnJob,
core
)
class glueDB(cdk.Stack):
	'''
	Class definition to crate my s3 buckets for creation of the data lake.
	'''
	def __init__(self, app: core.Construct, id: str, **kwargs):
	    super().__init__(app, id, **kwargs)
	    
	    #Redshift role to copy data from data lake to the clusters
	    binanceS3AccessForRedshiftClusterRole = iam.Role(self, 'binanceS3AccessForRedshiftClusterRole', {
	    roleName = 'binanceS3AccessForRedshiftClusterRole',
	    assumedBy = new iam.AccountPrincipal('123456'), #dummy aws account number, prefer to not give the exact account number for security reasons.
            managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess")]
	    )                              
	    #Glue crawler
	    glueCrawlerRole = iam.Role(self, "GlueCrawlerRole", 
		assumedBy = new iam.ServicePrincipal("glue.amazonaws.com"),
		inlinePolicies = (inline = new iam.PolicyDocument(statements = [iam.PolicyStatement(effect: iam.Effect.ALLOW, resources: ["arn:aws:s3:::binance-candle-input-1mGrain/*"], actions: ["*"])]),
				  managedPolicies = [iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AWSGlueServiceRole"), \
				  iam.ManagedPolicy.fromAwsManagedPolicyName("CloudWatchFullAccess"),
				  iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess")]
		))
	    
	    glueDB = glue.Database(self, 'binance_raw_data', databaseName = 'binance-etl-batch')
	    
	    #Glue table 
	    binance_candles1m_datafeed = glue.Table(self, 'binance_candles1m_datafeed', 
		  database = glueDB,
		  tableName = 'binance_candles1m_datafeed',
		  bucket = kwargs['bucket'],
		  s3Prefix = 'binanceInputFeedsRaw/candels-raw/',
		  dataFormat = glue.DataFormat.JSON,
		  partitionKeys = [
		    { name: "year", type: {inputString: "string", isPrimitive: true} },
		    { name: "month", type: {inputString: "string", isPrimitive: true} },
		    { name: "day", type: {inputString: "string", isPrimitive: true} },
		    { name: "hour", type: {inputString: "string", isPrimitive: true} }
		    ],
		  columns = [
		    {'name': 'trading_pair', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'open_price', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'close_price', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'high_price', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'low_price', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'btc_volume', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'usd_volume', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'no_of_trades', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'candle_open_time', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'candle_close_time', 'type': {'isPrimitive': true, inputString: 'string'}}
		  ]
	    
	      )
	    
            binance_accountOrders_datafeed = glue.Table(self, 'binance_accountOrders_datafeed', 
		  database = glueDB,
		  tableName = 'binance_accountOrders_datafeed',
		  bucket = kwargs['bucket'],
		  s3Prefix = 'binanceInputFeedsRaw/orders-raw',
		  dataFormat = glue.DataFormat.JSON,
		  partitionKeys = [
		    { name: "year", type: {inputString: "string", isPrimitive: true} },
		    { name: "month", type: {inputString: "string", isPrimitive: true} },
		    { name: "day", type: {inputString: "string", isPrimitive: true} },
		    { name: "hour", type: {inputString: "string", isPrimitive: true} }
		    ],
		  columns = [
		    {'name': 'symbol', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'orderid', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'price', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'origqty', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'executedqty', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'status', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'type', 'type': {'isPrimitive': true, inputString: 'string'}},
		    {'name': 'side', 'type': {'isPrimitive': true, inputString: 'string'}}
		  ]
	    
	      )

	   candles1m_crawler = CfnCrawler(self , 'binance_candles1m-crawler', 
		  role = glueCrawlerRole.roleArn,
		  name = 'binance_candles1m-crawler',
		  description = 'Crawler to create/update a glue table for binance candles datafeed',
		  schemaChangePolicy = {
		    "deleteBehavior": "LOG",
		    "updateBehavior": "LOG",
		  },
		  databaseName: glueDB.databaseName,
		  targets = {
		    "catalogTargets": [{
		      "databaseName": glueDB.databaseName,
		      "tables": [binance_candles1m_datafeed.tableName]
		    }],
		  }
	      })
	      
	   accountOrders_crawler = CfnCrawler(self , 'binance_accountOrders-crawler', 
		  role = glueCrawlerRole.roleArn,
		  name = 'binance_accountOrders-crawler',
		  description = 'Crawler to create/update a glue table for binance account/orders datafeed',
		  schemaChangePolicy = {
		    "deleteBehavior": "LOG",
		    "updateBehavior": "LOG",
		  },
		  databaseName: glueDB.databaseName,
		  targets = {
		    "catalogTargets": [{
		      "databaseName": glueDB.databaseName,
		      "tables": [binance_accountOrders_datafeed.tableName]
		    }],
		  }
	      })
	    
	      glueRole = iam.Role(self, "glue-role", 
		roleName = "glueETL_job_automate", 
		assumedBy = new iam.ServicePrincipal("glue.amazonaws.com"),
		managedPolicies = [
		  iam.ManagedPolicy.fromAwsManagedPolicyName(
		    "service-role/AWSGlueServiceRole"
		  ),
		  iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess"),
		  iam.ManagedPolicy.fromAwsManagedPolicyName("CloudWatchFullAccess"),
		],
	      )
	    
	      binance_candles_glue_job_auomate = glue.CfnJob(
		   self,
		   "binance_candles_glue_job_auomate",
		   name = "binance_candles_glue_job_auomate",
		   role = glueRole.roleArn,
		   command = {
		      "name": "glueetl", //Must be 'glueetl1' for an Apache Spark job
		      "pythonVersion": "3",
		      "scriptLocation": "s3://binance-candle-input-1mGrain/binance-glueETL/candles1m.py",
		    },
		    glueVersion = "2.0",
		    numberOfWorkers = 10,
		    workerType = "G.1X",
		    executionProperty = {
		    "maxConcurrentRuns" : 2,
		    },
		    timeout = 300,
		    defaultArguments = {
		      "--job-language": "python",
		      "--enable-metrics": true,
		      "--enable-continuous-cloudwatch-log": true,
		      "--src_prefix": "export_csv/5",
		      "--dest_s3_bucket": "",
		      "--dest_prefix": "liveramp-upload",
		      "--dataset_date":""
		    }
		)

	    binance_accountOrders_glue_job_auomate = glue.CfnJob(
		   self,
		   "binance_accountOrders_glue_job_auomate",
		   name = "binance_accountOrders_glue_job_auomate",
		   role = glueRole.roleArn,
		   command = {
		      "name": "glueetl", //Must be 'glueetl1' for an Apache Spark job
		      "pythonVersion": "3",
		      "scriptLocation": "s3://binance-candle-input-1mGrain/binance-glueETL/accountOrders.py",
		    },
		    glueVersion = "2.0",
		    numberOfWorkers = 10,
		    workerType = "G.1X",
		    executionProperty = {
		    "maxConcurrentRuns" : 2,
		    },
		    timeout = 300,
		    defaultArguments = {
		      "--job-language": "python",
		      "--enable-metrics": true,
		      "--enable-continuous-cloudwatch-log": true,
		      "--src_prefix": "export_csv/5",
		      "--dest_s3_bucket": "",
		      "--dest_prefix": "liveramp-upload",
		      "--dataset_date":""
		    }
		)

	    