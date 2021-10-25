from aws_cdk import core as cdk
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep

class BinancePipelineStack(cdk.Stack):
	'''
	CI/CD pipeline to deploy all the artifact via code commit like git.
	'''
	def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
		super().__init__(scope, construct_id, **kwargs)

		pipeline =  CodePipeline(self, "BinancePipeline", 
				pipeline_name="BinancePipeline",
				synth=ShellStep("Synth", 
					input=CodePipelineSource.git_hub("OWNER/REPO", "main"),
					commands=["npm install -g aws-cdk", 
					"python -m pip install -r requirements.txt", 
					"cdk synth"]
				)
				)
		#Add all the artifacts to codepipeline uside py_cdk package
		s3infra = s3Infra(self, 's3Infra')