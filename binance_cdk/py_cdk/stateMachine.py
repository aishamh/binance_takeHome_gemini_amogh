import aws_cdk.aws_stepfunctions as sfn
from aws_cdk import core as cdk
from binanceLambdaInfra import candles1mlambda, accountrderHandler

class StateMachineStack(cdk.Stack):
	'''
	State machine/step function that run every 5 mins and trigger the candle-grain1m and account orders lambda.
	'''
	def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
		super().__init__(scope, construct_id, **kwargs)

		accountrderHandler = lambda_.Function(self, "accountrderHandler", ...)
		candles1mlambda = lambda_.Function(self, "candles1mlambda", ...)

		submit_job_accountrderHandler = tasks.LambdaInvoke(self, "Submit Job",
		lambda_function=accountrderHandler,
		# Lambda's result is in the attribute `Payload`
		output_path="$.Payload" #Empty payload as we are not really seding any data to invoke lambda
		)

		submit_job_accountrderHandler = tasks.LambdaInvoke(self, "Submit Job",
		lambda_function=accountrderHandler,
		# Lambda's result is in the attribute `Payload`
		output_path="$.Payload" #Empty payload as we are not really seding any data to invoke lambda
		)

		wait_x = sfn.Wait(self, "Wait X Seconds",
		time=sfn.WaitTime.seconds_path("$.waitSeconds")
		)

		get_status_accountrderHandler = tasks.LambdaInvoke(self, "Get Job Status",
		lambda_function=accountrderHandler,
		# Pass just the field named "guid" into the Lambda, put the
		# Lambda's result in a field called "status" in the response
		input_path="$.guid",
		output_path="$.Payload"
		)

		get_status_candles1mlambda = tasks.LambdaInvoke(self, "Get Job Status",
		lambda_function=candles1mlambda,
		# Pass just the field named "guid" into the Lambda, put the
		# Lambda's result in a field called "status" in the response
		input_path="$.guid",
		output_path="$.Payload"
		)

		job_failed = sfn.Fail(self, "Job Failed",
		cause="AWS Batch Job Failed",
		error="DescribeJob returned FAILED"
		)


		definition = [submit_job_accountrderHandler, submit_job_accountrderHandler].next(wait_x).next([get_status_candles1mlambda, get_status_accountrderHandler]).next(sfn.Choice(self, "Job Complete?").when(sfn.Condition.string_equals("$.status", "FAILED"), job_failed).when(sfn.Condition.string_equals("$.status", "SUCCEEDED"), final_status).otherwise(wait_x))

		sfn.StateMachine(self, "BinanceStateMachine",
		definition=definition,
		timeout=cdk.Duration.minutes(5)
		)