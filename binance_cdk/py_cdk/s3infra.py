from aws_cdk import (
aws_s3 as s3,
aws_secretsmanager as secretsmanager,
aws_iam as role
core
)
import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import JSON
import glueDB
import binanceVPCStack
import binanceLambdaStack
import StateMachineStack
 
class s3Infra(cdk.Stack):
	'''
	Class definition to crate my s3 buckets for creation of the data lake.
	'''
	def __init__(self, app: cdk.App, id: str, **kwargs):
	    super().__init__(app, id, **kwargs)

	    bucket = s3.Bucket(self, "binance-candle-input-1mGrain", versioned=True)

	    #Creates an input prefix in the binance-candle-input-1mGrain bucket.
	    candlesRaw = s3deploy.BucketDeployment(self, "binanceInputFeedsRaw/candles-raw", sources=[s3deploy.Source.asset("")], destination_bucket=self.bucket, destination_key_prefix="binanceInputFeedsRaw/candles-raw")
	    ordersRaw = s3deploy.BucketDeployment(self, "binanceInputFeedsRaw/orders-raw", sources=[s3deploy.Source.asset("")], destination_bucket=self.bucket, destination_key_prefix="binanceInputFeedsRaw/orders-raw")
	    #Creates an cooked prefix, where the json is flatted out and store in data lake partitioned by year-month-day and hour. in the binance-candle-input-1mGrain bucket. This is the dest. from the output of lambda function
	    s3deploy.BucketDeployment(self, "binanceCookedDataLake", sources = [s3deploy.Source.asset("")], destination_bucket = self.bucket, destination_key_prefix = "binance-cooked-DataLake-candles")

	    #Creates an curated prefix, where the json is flatted out and store in data lake partitioned by year-month-day and hour. in the binance-candle-input-1mGrain bucket. This is the dest. from the output of glue etl (Spark job) function
	    s3deploy.BucketDeployment(self, "binanceCuratedDataLake", sources = [s3deploy.Source.asset("")], destination_bucket = self.bucket, destination_key_prefix = "binance-curatedDataLake-orders")

	    #Folder to holder all the glue scripts that is read by the glue job
	    s3deploy.BucketDeployment(self, "binancglueETL",sources = [s3deploy.Source.asset("py_cdk/glueETLScripts/accountOrders.py")], destination_bucket = self.bucket, destination_key_prefix = "binance-glueETL")
	    s3deploy.BucketDeployment(self, "binancglueETL",sources = [s3deploy.Source.asset("py_cdk/glueETLScripts/candles1m.py")], destination_bucket = self.bucket, destination_key_prefix = "binance-glueETL")
	    
	    #Role for aws secret manager to store secret keys and value
	    role = iam.Role(stack, "SomeRole", assumed_by=iam.AccountRootPrincipal())
	    
	    binance_Apisecret = secretsmanager.Secret(self, "TemplatedSecret",
    				generate_secret_string=SecretStringGenerator(
        			secret_string_template=JSON.stringify({"API_KEY": "API_KEY"}),
        			generate_string_key="API_SECRET" #Prefer not to specify the api secret,
				encryption_key=key #Not implementing the encryption method here, but will use something like hmac, sha256 to encrpyt the keys
    				))

	    #Call to the lambda stack
	    binanceLambdaStack(self, 'binanceLambdaStack')

	    #Call to the glue stack
	    glueDB(self, 'glueDB')

	    #Call to the vpc stack
	    binanceVPCStack(self , 'binanceVPCStack')
	    
	    #Call statemachine stack
	    StateMachineStack(self , 'StateMachineStack')
