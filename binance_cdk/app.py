'''
App (PSVM method) entry point of the program.

=======
Note:
=======
Steps tp setup CDK:
1. install npm
2. cdk -init (creates an empty project)
3. Add in your infrastructure code.
4. Run CDK synth
5. CDK bootstrap <aws_account>/<region>
6. Run CDK deploy ---> This creates a cloudformation .yml file and the aws resources will be created as per the mentioned stack. 

CI/CD way:
All these done on feature branch
1. git status 
2. git commit -m "<Commit message>"
3. Code review (if needed)
4. git pull --rebase
5. git push 

This workflow triggers code deploy pipeline in aws to beta account and then to prod account.
For code deploy refer binance_cicd.py.
'''
from aws_cdk import core

from py_cdk.s3infra import s3Infra

app = cdk.App()
#Pipeline stack
BinancePipelineStack(app , 'BinancePipelineStack')
#S3 infra stack
s3Infra(app, "s3Infra")
app.synth()