import json
import boto3
import re

s3 = boto3.resource('s3', region='us-east-1')
glue = boto3.resource('glue', region='us-east-1')

def lambda_handler(event, context):
    try:

        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']
            

            match = re.match(r'bolsa_bovespa/raw/data_carteira=(\d{4}-\d{2}-\d{2})/', object_key)
            if not match:
                print("Arquivo fora do padrão esperado. Ignorando.")
                continue
            
            data_carteira = match.group(1)
            print(f"Nova data detectada: {data_carteira}")

            response = s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix='bolsa_bovespa/raw/data_carteira='
            )
            
            datas_existentes = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    if 'data_carteira=' in obj['Key']:
                        existing_date = re.search(r'data_carteira=(\d{4}-\d{2}-\d{2})/', obj['Key'])
                        if existing_date:
                            datas_existentes.append(existing_date.group(1))
            
            if len(datas_existentes) == 1 and data_carteira not in datas_existentes:
                job_name = 'bolsa_carteira_teorica_transform-init'
            else:
                job_name = 'bolsa_carteira_teorica_transform'
            
            print(f"Invocando job Glue: {job_name}")
            glue.start_job_run(JobName=job_name)
            print(f"Job {job_name} iniciado com sucesso.")
    
    except Exception as e:
        print(f"Erro ao processar evento: {str(e)}")
        raise
