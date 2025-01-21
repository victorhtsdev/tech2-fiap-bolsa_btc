import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, max as spark_max
from pyspark.sql.types import DecimalType, IntegerType, StructType, StructField, LongType
import boto3
from pyspark.sql import functions as F

# Capture the JOB_NAME parameter
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Initialize Glue Context and Job
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Disable the creation of _SUCCESS file
spark.conf.set("mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Glue Catalog database and table configurations
database_name = "bolsa_bovespa"
table_name = "carteira_teorica"
silver_table_name = "carteira_teorica_silver"
gold_table_name = "carteira_teorica_gold"
output_path_refined = "s3://vhts-fiap-tech-challenge2/bolsa_bovespa/refined/"
output_path_silver = "s3://vhts-fiap-tech-challenge2/bolsa_bovespa/silver/"
output_path_gold = "s3://vhts-fiap-tech-challenge2/bolsa_bovespa/gold/"

def check_s3_path_exists(s3_path):
    """
    Check if the specified S3 path exists.
    """
    s3 = boto3.client("s3")
    bucket = s3_path.split("/")[2]
    prefix = "/".join(s3_path.split("/")[3:])
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return "Contents" in response
    except Exception as e:
        print(f"Error accessing bucket: {e}")
        return False

def repair_table(database_name, table_name):
    """
    Run MSCK REPAIR TABLE to update table partitions in Glue Catalog.
    """
    repair_table_query = f"MSCK REPAIR TABLE {database_name}.{table_name}"
    try:
        print(f"Running command: {repair_table_query}")
        spark.sql(repair_table_query)
        print(f"MSCK REPAIR TABLE executed successfully for table '{table_name}'.")
    except Exception as e:
        print(f"Error running MSCK REPAIR TABLE for table '{table_name}': {e}")

# Ensure the Glue Catalog tables exist
def ensure_table_exists(table_name, columns, partition_keys, location):
    """
    Verify or create the specified Glue table in the catalog.
    """
    table_input = {
        'Name': table_name,
        'StorageDescriptor': {
            'Columns': columns,
            'Location': location,
            'InputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
            'Compressed': False,
            'SerdeInfo': {
                'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
                'Parameters': {'serialization.format': '1'}
            }
        },
        'PartitionKeys': partition_keys,
        'TableType': 'EXTERNAL_TABLE'
    }
    glue_client = boto3.client("glue")
    try:
        glue_client.get_table(DatabaseName=database_name, Name=table_name)
        print(f"Table '{table_name}' already exists in Glue Catalog.")
    except glue_client.exceptions.EntityNotFoundException:
        glue_client.create_table(DatabaseName=database_name, TableInput=table_input)
        print(f"Table '{table_name}' created in Glue Catalog successfully.")

# Define table schemas and partitions
refined_columns = [
    {"Name": "acao", "Type": "string"},
    {"Name": "tipo", "Type": "string"},
    {"Name": "qtd_teorica", "Type": "bigint"},
    {"Name": "participacao", "Type": "decimal(5,3)"}
]
gold_columns = [
    {"Name": "soma_qtd_teorica", "Type": "bigint"},
    {"Name": "soma_participacao", "Type": "decimal(15,3)"},
    {"Name": "soma_variacao_participacao", "Type": "decimal(15,3)"},
    {"Name": "soma_variacao_qtd_teorica", "Type": "bigint"}
]
silver_columns = refined_columns + [
    {"Name": "variacao_participacao", "Type": "decimal(5,3)"},
    {"Name": "variacao_qtd_teorica", "Type": "bigint"},
    {"Name": "data_d-1", "Type": "string"}
]
partition_keys_silver = [{"Name": "data", "Type": "string"}, {"Name": "codigo", "Type": "string"}]
partition_keys_refined = [{"Name": "data", "Type": "string"}, {"Name": "codigo", "Type": "string"}]
partition_keys_gold = [{"Name": "data", "Type": "string"}, {"Name": "tipo", "Type": "string"}]

# Ensure tables exist in the Glue Catalog
ensure_table_exists(table_name, refined_columns, partition_keys_refined, output_path_refined)
ensure_table_exists(silver_table_name, silver_columns, partition_keys_silver, output_path_silver)
ensure_table_exists(gold_table_name, gold_columns, partition_keys_gold, output_path_gold)

# Input S3 path
input_path = "s3://vhts-fiap-tech-challenge2/bolsa_bovespa/raw/bolsa.parquet"

# Load Parquet as DynamicFrame
dynamic_frame = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [input_path]},
    format="parquet"
)

# Convert DynamicFrame to DataFrame and rename columns
refined_df = dynamic_frame.toDF().withColumnRenamed("Código", "codigo") \
    .withColumnRenamed("Ação", "acao") \
    .withColumnRenamed("Tipo", "tipo") \
    .withColumnRenamed("Qtde. Teórica", "qtd_teorica") \
    .withColumnRenamed("Part. (%)", "participacao") \
    .withColumnRenamed("Data", "data") \
    .withColumn("qtd_teorica", col("qtd_teorica").cast(LongType())) \
    .withColumn("participacao", col("participacao").cast(DecimalType(5, 3))) \
    .withColumn("tipo", F.regexp_replace(col("tipo"), r"\s+", "_"))

# Empty DataFrame to handle no prior data case
empty_schema = StructType([])
df_with_max_date = spark.createDataFrame([], empty_schema)

# Check if output_path_refined exists
if check_s3_path_exists(output_path_refined):
    print(f"Path {output_path_refined} exists. Retrieving most recent data.")

    # Load existing data
    existing_dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
        database=database_name,
        table_name=table_name
    )
    existing_df = existing_dynamic_frame.toDF()

    # Get the most recent partition date
    most_recent_partition = existing_df.agg(spark_max("data").alias("max_data")).collect()[0]["max_data"]
    df_with_max_date = existing_df.filter(col("data") == most_recent_partition)
else:
    print(f"Path {output_path_refined} does not exist. Skipping retrieval.")

# Write refined data
refined_df.write \
    .mode("append") \
    .partitionBy("data", "codigo") \
    .parquet(output_path_refined)

repair_table(database_name, table_name)

# Generate Silver data if prior data exists
if not df_with_max_date.rdd.isEmpty():
    silver_df = refined_df.alias("atual").join(
        df_with_max_date.alias("anterior"),
        on="codigo",
        how="left"
    ).select(
        col("atual.acao"),
        col("atual.tipo"),
        col("atual.qtd_teorica"),
        col("atual.participacao"),
        F.coalesce(
            (col("atual.participacao") - col("anterior.participacao")).cast(DecimalType(15, 3)), 
            F.lit(0).cast(DecimalType(15, 3))
        ).alias("variacao_participacao"),
        F.coalesce(
            (col("atual.qtd_teorica") - col("anterior.qtd_teorica")).cast(LongType()), 
            F.lit(0).cast(LongType())
        ).alias("variacao_qtd_teorica"),
        col("anterior.data").alias("data_d-1"),
        col("atual.data"),
        col("atual.codigo")
    )

    # Silver
    silver_df.write \
        .mode("append") \
        .partitionBy("data", "codigo") \
        .parquet(output_path_silver)

    repair_table(database_name, silver_table_name)

    # Gold
    gold_df = silver_df.groupBy("data", "tipo").agg(
        F.sum(col("qtd_teorica").cast(LongType())).alias("soma_qtd_teorica"),
        F.sum(col("participacao").cast(DecimalType(15, 3))).alias("soma_participacao"),
        F.sum(col("variacao_participacao").cast(DecimalType(15, 3))).alias("soma_variacao_participacao"),
        F.sum(col("variacao_qtd_teorica").cast(LongType())).alias("soma_variacao_qtd_teorica")
    )

    gold_df.write \
        .mode("append") \
        .partitionBy("data", "tipo") \
        .parquet(output_path_gold)

    repair_table(database_name, gold_table_name)

job.commit()
