'''
Glue ETL job that is trigger by airflow every hour to flatten out the candles data and stores as parquet format.

For more details please visit this document: git readme file.
'''
from pyspark.sql.functions import col, row_number, first
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import re
from awsglue.dynamicframe import DynamicFrame
import datetime

args = getResolvedOptions(sys.argv, ['JOB_NAME','dataset_date', 'dest_s3_bucket', 'dest_prefix'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

ds=int(args['dataset_date'].replace('-',''))

pdp = "partition_date == '{dataset_date}'".format(dataset_date=str(args['dataset_date'])) #Constructed by airflow

s3_dest = 's3://'+args['dest_s3_bucket']+'/'+args['dest_prefix']

print(s3_dest)

def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    '''
    Method to run Spark sql.
    '''
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)

def rename_s3() -> None:
  '''
  Method to rename s3 file produced by the glue etl to appropriate name
  '''
  URI = sc._gateway.jvm.java.net.URI
  Path = sc._gateway.jvm.org.apache.hadoop.fs.Path
  FileSystem = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
  fs = FileSystem.get(URI(f"{s3_dest}/dataset_date={ds}/"), sc._jsc.hadoopConfiguration())
  file_path = f"{s3_dest}/dataset_date={ds}/"
  # rename created file
  created_file_path = fs.globStatus(Path(file_path + "*part*.gz"))[0].getPath()
  fs.rename(created_file_path,Path(file_path + f"audibleliverampuserfeed_{ds}.gz"))
 
 binance_accountorders_datafeed = glueContext.create_dynamic_frame.from_catalog(database = "binance_raw_data", table_name = "binance_accountorders_datafeed", additional_options = {"recurse": True}, push_down_predicate = pdp ,transformation_ctx = "binance_accountorders_datafeed")


 binance_accountorders_datafeed.coalesce(1).write.format('parquet').mode("append").option("compression", "snappy").partitionBy("dataset_date").save(s3_dest , header = 'true')

rename_s3()
job.commit()