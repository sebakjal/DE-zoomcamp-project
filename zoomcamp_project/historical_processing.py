import pyspark
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql.functions import hour
from pyspark.sql import types
from pyspark.sql.functions import col, lower
import os

# Defining functions to validate records
def latitude_check(df):
    return df.filter(col('latitude').between(-90,90))

def longitude_check(df):
    return df.filter(col('longitude').between(-180,180))

def depth_check(df):
    return df.filter((col('depth').between(-5,1000)) | (col('depth').isNull()))

def mag_check(df):
    return df.filter((col('mag').between(-1,10)) | (col('mag').isNull()))

def magType_check(df):
    df_lower = df.withColumn('magType_lower', lower(col('magType')))
    df_lower = df_lower.drop('magType')
    return df_lower

def status_check(df):
    return df.filter((col('status')=='reviewed') | (col('status')=='automatic'))

# Setting variables from environment variables
project_id = os.environ.get("GCP_PROJECT")
dataset_id = os.environ.get("BQ_DATASET")
table_name = os.environ.get("BQ_TABLE")
gcs_historical_bucket = os.environ.get("GCS_HISTORICAL_BUCKET")
gcp_project = os.environ.get("GCP_PROJECT")

credentials_locations = "/home/kjal/zoomcamp_project/zoomcamp-scarvajal-2758157f7ca9.json"

# Sets the configuration for spark (BQ and GCS connectors)
conf = SparkConf() \
    .setMaster('local[*]') \
    .setAppName('test') \
    .set("spark.jars", "/home/kjal/pyspark_gcs_connector/gcs-connector-hadoop3-2.2.5.jar, /home/kjal/pyspark_bq_connector/spark-3.3-bigquery-0.32.0.jar") \
    .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .set("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_locations)

sc = SparkContext(conf=conf)

sc._jsc.hadoopConfiguration().set("fs.AbstractFileSystem.gs.impl",  "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
sc._jsc.hadoopConfiguration().set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
sc._jsc.hadoopConfiguration().set("fs.gs.auth.service.account.json.keyfile", credentials_locations)
sc._jsc.hadoopConfiguration().set("fs.gs.auth.service.account.enable", "true")

# Start a Spark session with the previous configuration
spark = SparkSession.builder \
    .config(conf=sc.getConf()) \
    .getOrCreate()

# Schema to apply to the data
schema = types.StructType([
    types.StructField("time", types.TimestampType(), False),
    types.StructField("latitude", types.DoubleType(), False),
    types.StructField("longitude", types.DoubleType(), False),
    types.StructField("depth", types.DoubleType(), True),
    types.StructField("mag", types.DoubleType(), True),
    types.StructField("magType", types.StringType(), True),
    types.StructField("nst", types.IntegerType(), True),
    types.StructField("gap", types.DoubleType(), True),
    types.StructField("dmin", types.DoubleType(), True),
    types.StructField("rms", types.DoubleType(), True),
    types.StructField("net", types.StringType(), True),
    types.StructField("id", types.StringType(), True),
    types.StructField("updated", types.TimestampType(), True),
    types.StructField("place", types.StringType(), True),
    types.StructField("type", types.StringType(), True),
    types.StructField("horizontalError", types.DoubleType(), True),
    types.StructField("depthError", types.DoubleType(), True),
    types.StructField("magError", types.DoubleType(), True),
    types.StructField("magNst", types.IntegerType(), True),
    types.StructField("status", types.StringType(), True),
    types.StructField("locationSource", types.StringType(), True),
    types.StructField("magSource", types.StringType(), True)
])

# Reading historical data from GCS bucket
df_earthquakes = spark.read \
    .option('header', 'true') \
    .schema(schema) \
    .csv(f'gs://{gcs_historical_bucket}/earthquakes/query?format=csv&starttime=*')

df_earthquakes = df_earthquakes.repartition(4)

df_earthquakes.printSchema()

validation_rules = [
    ("latitude_constrain", latitude_check),
    ("longitude_constrain", longitude_check),
    ("depth_constrain", depth_check),
    ("magnitude_constrain", mag_check),
    ("magnitude_type_lowering", magType_check),
    ("status_valid_codes", status_check)
]

# Checking and validating data
for validation_name, validation_func in validation_rules:
    result = validation_func(df_earthquakes)
    if result.count() > 0:
        print(f"Validation {validation_name} completed. \
            Valid rows: {result.count()} ")
    df_earthquakes = result

# Creating new fields    
df_with_percentages = df_earthquakes.withColumn('depthError_percent', col('depthError')/col('depth')*100) \
                              .withColumn('magError_percent', col('magError')/col('mag')*100)

# Loading the data into Bigquery
df_with_percentages.write \
  .format("bigquery") \
  .option("writeMethod", "direct") \
  .mode("append") \
  .save(f"{project_id}.{dataset_id}.{table_name}")

# Stopping the Spark session 
sc.stop()
spark.stop()