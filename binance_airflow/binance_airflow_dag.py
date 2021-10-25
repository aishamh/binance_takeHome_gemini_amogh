"""
<html>
<head><h3>Binance Data Pipeline</h3></head>
<body>
    Binance data pipeline documentation :<a href='git readme .md (mark down file)'> Binance data pipeline documentation </a>

<br>  This is the automation of a pipeline that downloads the binance candle 1m grain and account order data using the binance apis documented here: https://python-binance.readthedocs.io/en/latest/binance.html#binance.client.BaseClient.__init__ </li></ol>

<br>==================
<br>Important links:
<br>==================
<ol>
<br> <li> AWS account: <a href='Burner Personal aws account'> Amogh Raghunath's person account </a></li>
<br> <li> CI/CD pipeline:<a href=''> AWS code deploy.</a></li>
<br> <li> CDK:<a href=''> Binance CDK </a></li>
<br> <li> Lambda script:<a href=''> Binance cancel 1m grain and account orders Lambda script </a></li>
<br> <li> Glue ETL script:<a href=''> Glue ETL (Spark) script </a></li>
</ol>
<br>============================
<br>How does the pipeline work:
<br>============================
<ol>
<br> <li> Lambda gets trigger from a stat machine (Step function) every 5m</li>
<br> <li> The lambdas (get candle data) and account orders data pulls in the data from using the apis get_klines and get_all_orders.</li>
<br> <li> Generates the final dataset (Parquet format) and stores it in the raw folder partition by year, month , day and hour</li>
<br> <li> Glue Etl is trigger by airflow , which flattens the Parquet file and spits out results in the cooked folder (Data lake)</li>
<br> <li> This data is exposed as the raw table (spectrum table) via glue to redshift and respective etls to build the fact and dim tables runs via airflow</li>
</ol>
</body></html>
"""
import datetime
import os
import sys
import logging
import boto3
import time
import enum
from retrying import retry
from airflow.models import DAG
from airflow.operators import (
    RsTransformTruncateInsertOperator,
    PythonOperator,
    BashOperator
)

class constants(enum.Enum):
    '''
    Enum class, contains all the necessary constants required/used by the Binance data pipeline
    '''
    ssl_cert = (None or get_conf('x-amz-ssl', 'ssl-cert', None))
    ssl_verify_server = (get_conf_bool('x-amz-ssl', 'ssl-verify-server', False))
    glue_endpoint_url = 'https://glue.us-east-1.amazonaws.com'
    glue_job_name = 'binance_accountOrders_glue_job_auomate' #Name as given in the CDK
    glue_job_error = ['STOPPED', 'FAILED', 'TIMEOUT']
    glue_job_success = ['SUCCEEDED']
    glue_crawler_error = ['ERROR', 'FAILED', 'TIMEOUT','STOPPED']
    glue_crawler_success = ['READY']
    aws_region='us-east-1'
    aws_access_key_id = '' #Fill in your key
    aws_secret_access_key = '' #Fill in your secret key
    bucket_details = [{'bucket':'binance-candle-input-1mGrain','task':'candleGrains1m','prefix':'','crawler_name':'binance_candles1m-crawler'},\
                      {'bucket':'binance-candle-input-1mGrain','task':'accountOrders','prefix':'','crawler_name':'binance_accountOrders-crawler'}]
    
dag_id = 'binance_data_ETL'
dag = DAG(
    dag_id=dag_id,
    default_args=default_args,
    max_active_runs=5,
    concurrency=5,
    schedule_interval='0 * * * *' #Dag runs at every 0th min. of the hour
)

dag.catchup = False
dag.doc_md = __doc__

dataset_default = "{{ ds }}"
run = datetime.datetime.now()

def get_aws_client(resource=None) -> boto3.client or boto3.session:
    '''
        Method to get the client object to interact with AWS services using boto3 py library.
    '''
    ACCESS_KEY = constants.aws_access_key_id.value
    SECRET_KEY = constants.aws_secret_access_key.value

    if resource == 'glue':
        return boto3.client(service_name=resource, 
                          aws_access_key_id=ACCESS_KEY, 
                          aws_secret_access_key=SECRET_KEY, 
                          region_name=constants.aws_region.value,
                          endpoint_url=constants.glue_endpoint_url.value
                          ) 
    else:
        return boto3.Session( 
                          aws_access_key_id=ACCESS_KEY, 
                          aws_secret_access_key=SECRET_KEY
                          ) 

def retryOnErrors(exception : object) -> bool:
    '''
    Method to retry lambda success function.
    '''
    logging.info("Retrying to fetch glue job status........")
    return isinstance(exception, ValueError)


@retry(retry_on_exception=retryOnErrors,
           stop_max_attempt_number=7,
           wait_random_min=0.5, #Retry after 30-60 secs
           wait_random_max=1)
def get_glue_job_status(**kwargs : dict) ->  str:
    '''
        Method to get the job status of a glue job run
    '''
    try:
    	status = kwargs.get('client').get_job_run(JobName= constants.glue_job_name.value, RunId=kwargs.get('JobRunId'))
    except:
	     raise ValueError("glu job not completed, please check cloudwatch logs....")
    return status['JobRun']['JobRunState']

def get_glue_crawler_status(**kwargs  : dict) -> str:
    '''
        Method to get the job status of a glue crawler run
    '''
    status = kwargs.get('client').get_crawler(Name=kwargs.get('crawler_name'))
    return status["Crawler"]["State"]

def get_status(client : object, state  : str, status : object, const_success  :  constants, const_err :  constants, name :  str, JobRunId :  int) -> None:
    '''
        Poller to get job status of glue resources
    '''
    while state not in const_success:
        time.sleep(30) #Sleeps for 30 seconds before fetching the next job status
        logging.info("Getting glue job status")
        state = status(client = client , crawler_name = name , JobRunId = JobRunId)
        logging.info(f"Status is {state}")
        if state in const_err:
            raise Exception('Failed to execute glue job, please check cloudwatch logs for more info')


def run_glue_job(*args : list, **kwargs : dict) -> None:
    '''
        PythonOperator callable to run either a glue job or a glue crawler.
    '''

    client = get_aws_client('glue')
    #Depending on the type in keyworded args, this will run either GLUE crawler or glue etl job.
    if kwargs.get('type') == 'glue_job':
        response = client.start_job_run(JobName=constants.glue_job_name.value, Arguments = {'--dataset_date':"{0}".format(kwargs['templates_dict']['dataset_date']), \
                                                                                            '--dest_s3_bucket':constants.bucket_details.value[0]['bucket']})
        status = get_glue_job_status(client = client, JobRunId = response['JobRunId'])
        if status:
            logging.info('Glue Job Started....... Getting the status of the run')
            get_status(client, status, get_glue_job_status,constants.glue_job_success.value, constants.glue_job_error.value, None ,response['JobRunId'] )

    elif kwargs.get('type') == 'glue_crawler':
        response = client.start_crawler(Name=kwargs.get('crawler_name'))
        status = get_glue_crawler_status(client = client, crawler_name = kwargs.get('crawler_name'))
        if status:
            logging.info(f"Glue crawler {kwargs.get('crawler_name')} started....... Getting the status of the run")
            get_status(client , status, get_glue_crawler_status,constants.glue_crawler_success.value, constants.glue_crawler_error.value, kwargs.get('crawler_name'), None)

#Note: this is an customer operator, will not be coding out the exact operator in interest of time, but the defition will be comething like:
'''
from airflow.sensors.base_sensor_operator import BaseSensorOperator

from airflow.utils.decorators import apply_defaults

class S3PrefixSensor(BaseSensorOperator):

    template_fields = ('prefix', 'bucket_name')

    @apply_defaults
    def __init__(self,
                 bucket_name,
                 prefix,
                 delimiter='/',
                 aws_conn_id='aws_default',
                 verify=None,
                 *args,
                 **kwargs):
        super(S3PrefixSensor, self).__init__(*args, **kwargs)
        # Parse
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.delimiter = delimiter
        self.full_url = "s3://" + bucket_name + '/' + prefix
        self.aws_conn_id = aws_conn_id
        self.verify = verify

    def poke(self, context):
        self.log.info('Poking for prefix : %s in bucket s3://%s', self.prefix, self.bucket_name)
        from airflow.hooks.S3_hook import S3Hook
        hook = S3Hook(aws_conn_id=self.aws_conn_id, verify=self.verify)
        return hook.check_for_prefix(
            prefix=self.prefix,
            delimiter=self.delimiter,
            bucket_name=self.bucket_name)
'''
#S3 prefix sensor to check for that hour partition for candlegrains.
s3_binance_candle_grains= S3PrefixSensor(
    task_id='binance_candle_grains'
    dag=dag,
    # Poll S3 every 1 mins
    poke_interval=60,
    # Dont want to wait more than 2 hours
    timeout=60*2,
    bucket_name = constants.bucket_details[0].bucket,
    prefix="binanceInputFeedsRaw/candles-raw/{0}/{1}/{2}/{3}".format(run.year, run.month, run.day, run.hour), # data-repo account has cross account access to the
    aws_conn_id="binance_conn_id") #Created a nick name and store the conenction details under ADMIN->Configuration tab in airflow UI

#S3 prefix sensor to check for that hour partition for accountOrders.
s3_binance_orderdata = S3PrefixSensor(
    task_id='binance_orderdata'
    dag=dag,
    # Poll S3 every 1 mins
    poke_interval=60,
    # Dont want to wait more than 2 hours
    timeout=60*2,
    bucket_name = constants.bucket_details[0].bucket,
    prefix="binanceInputFeedsRaw/orders-raw/{0}/{1}/{2}/{3}".format(run.year, run.month, run.day, run.hour), # data-repo account has cross account access to the
    aws_conn_id="binance_conn_id") #Created a nick name and store the conenction details under ADMIN->Configuration tab in airflow UI


#Run the glue crawlers once the partitions are available for that hour in the s3 buckets and detect any schema changes abd update the glue table.

for i in constants.bucket_details.value:
    binance_glue_crawler_run = PythonOperator(
        task_id='{task}_glue_crawler_run'.format(task=i.get('task')),
        python_callable=run_glue_job,
        op_kwargs={'type':'glue_crawler', 'crawler_name': i.get('crawler_name')},
        provide_context=True,
        dag=dag
    )

#Set the upstream/downstream flows
s3_binance_candle_grains.set_upstream([s3_binance_candle_grains , s3_binance_orderdata])
binance_orderdata.set_upstream([s3_binance_candle_grains , s3_binance_orderdata])

#Run Binance candle GLue etl job
candlegrains1m_glue_job_run = PythonOperator(
    task_id='candlegrains_glue_job_run',
    python_callable=run_glue_job,
    op_kwargs={'type':'glue_job'},
    templates_dict={'dataset_date': dataset_default},
    provide_context=True,
    dag=dag
)
    
candleGrains1m_glue_crawler_run.set_downstream(candlegrains1m_glue_job_run)

#Run Binance candle GLue etl job
accountOrders_glue_job_run = PythonOperator(
    task_id='accountOrders_glue_job_run',
    python_callable=run_glue_job,
    op_kwargs={'type':'glue_job'},
    templates_dict={'dataset_date': dataset_default},
    provide_context=True,
    dag=dag
)

accountOrders_glue_crawler_run.set_downstream(candlegrains1m_glue_job_run)


#Logic to run etl code that builds out the facts and dims will be in a stand alone dag.