from aws_cdk import (
aws_ec2 as ec2,
aws_ssm as ssm,
core
    )
    
class binanceVPCStack(core.Stack):
'''
Lambda infra to download the candels data at 1m grain and orders data.
'''
def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
	super().__init__(scope, construct_id, **kwargs)

	#Create an VPC FOR THE LAMBDA TO BE DEPLOYED IN THIS VPC. (More secure)

	self.vpc = ec2.Vpc(self, 'demovpc',
            cidr = '192.168.50.0/24',
            max_azs = 2,
            enable_dns_hostnames = True,
            enable_dns_support = True, 
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name = 'Public-Subent',
                    subnet_type = ec2.SubnetType.PUBLIC,
                    cidr_mask = 26
                ),
                ec2.SubnetConfiguration(
                    name = 'Private-Subnet',
                    subnet_type = ec2.SubnetType.PRIVATE,
                    cidr_mask = 26
                )
            ],
            nat_gateways = 1,

        )
        priv_subnets = [subnet.subnet_id for subnet in self.vpc.private_subnets]

        count = 1
        for psub in priv_subnets: 
            ssm.StringParameter(self, 'private-subnet-'+ str(count),
                string_value = psub,
                parameter_name = '/'+env_name+'/private-subnet-'+str(count)
                )
            count += 1 

	