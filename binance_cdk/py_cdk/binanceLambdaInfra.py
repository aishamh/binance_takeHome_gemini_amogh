from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    aws_lambda as _lambda
    core
)
import s3Infra

class binanceLambdaStack(core.Stack):
    '''
    Lambda infra to download the candels data at 1m grain and orders data.
    '''
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        vpc = binanceVPCStack(self , 'binanceVPCStack')
        super().__init__(scope, construct_id, **kwargs)

        #Create an IAM user for the entire account and name it as binanceUser
        binance_etl_user = iam.User(self, "binance_etl_user", userName = "binance_etl_user")

        binance_etl_user.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess"))

        #Add glue access.
        binance_etl_user.addToPolicy(iam.PolicyStatement(
        actions = [
            "glue:GetCrawler",
            "glue:GetCrawlers",
            "glue:StartCrawler",
            "glue:StartCrawlerSchedule",
            "glue:StartJobRun",
            "glue:GetJobRun",
            "glue:StartTrigger"
        ],
        effect = iam.Effect.ALLOW,
        resources = ["*"]
        ))

        candles1mlambdarole = new iam.Role(self, 'liverampAPTHashRole', 
        roleName = 'liverampAPTHashRole',
        assumedBy = new iam.ServicePrincipal('lambda.amazonaws.com'),
        managedPolicies = [
            iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonS3FullAccess"),
            iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AWSLambdaBasicExecutionRole")
        ]
        )
        
        #dead letter queue for the candled 1m lambda handler
        candles1mHandlerdlq = sqs.Queue(
            self, "candles1mHandlerdlq",
            visibility_timeout=core.Duration.seconds(300),
        )
        #Lambda function to download candles data at 1m grain
        candles1mlambda = _lambda.Function(
            self, 'candles1mHandler',
            runtime = _lambda.Runtime.PYTHON_3_7,
            environment = {'bucket' : s3Infra.bucket.bucketName , 'key' : s3Infra.candlesRaw.name},
            role = candles1mlambdarole, 
            code = _lambda.Code.from_asset('lambda'),
            handler = 'candles1mHandler.handler',
            timeout = Duration.seconds(900),
            onFailure = SqsDestination(SqsDestination),
            vpc = self.vpc
        )

        #dead letter queue for the account orders lambda handler
        accountHandlerdlq = sqs.Queue(
            self, "candles1mHandlerdlq",
            visibility_timeout=core.Duration.seconds(300),
        )
        #Lambda function to download candles data at 1m grain
        accountorderHandler = _lambda.Function(
            self, 'accountrderHandler',
            runtime = _lambda.Runtime.PYTHON_3_7,
            environment = {'bucket' : s3Infra.bucket.bucketName , 'key' : s3Infra.ordersRaw.name},
            role = candles1mlambdarole, 
            code = _lambda.Code.from_asset('lambda'),
            handler = 'accountHandler.handler',
            timeout = Duration.seconds(900),
            onFailure = SqsDestination(accountHandlerdlq),
            vpc = self.vpc
        )