import json
import boto3
import logging
from binanceClient import binanceClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bucket = os.environ['bucket'] #passed as lambda env. variable
key = os.environ['prefix']

def handler(event, context):
    '''
    Handler method, entry point of the program
    '''
    print('request: {}'.format(json.dumps(event)))

    bc = binanceClient()

    s3 = boto3.resource('s3')
    #Note: if you want to test it using the other method using requests, then use bc._get_all_ordersin line 23
    try:
        response = json.loads(bc._get_all_orders_using_binance_client())
	
    except:
        raise ValueError("Something went wrong when downloading the resonse from binace apis , see the stack trace from cloudwatch logs.")

    with open('accoutOrders.json', 'w') as f:
        json.dump(resonse, f)

    logging.info("Uploading file to accountOrders raw prefix.........")
    s3object = s3.Object(bucket , key)

    s3object.put(Body=(bytes(json.dumps('accoutOrders.json').encode('UTF-8')))