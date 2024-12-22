import boto3
import re

# Initialize S3 and Glue clients
s3 = boto3.client('s3')
glue = boto3.client('glue')

# Glue Job Name
GLUE_JOB_NAME = 'bolsa_carteira_teorica_transform'

def lambda_handler(event, context):
    try:
        # Process each S3 event received
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']
            
            print(f"File detected: s3://{bucket_name}/{object_key}")
            
            # Check if the file is bolsa.parquet
            if object_key.endswith('bolsa.parquet'):
                print(f"File bolsa.parquet detected. Starting Glue Job: {GLUE_JOB_NAME}")
                
                # Start the Glue Job
                response = glue.start_job_run(JobName=GLUE_JOB_NAME)
                print(f"Glue Job started successfully. ID: {response['JobRunId']}")
            else:
                print(f"File {object_key} does not match the expected pattern. Skipping.")
    
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        raise
