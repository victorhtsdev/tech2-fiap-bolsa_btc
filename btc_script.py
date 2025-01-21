import os
import requests
import json
from datetime import datetime
import boto3

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "your_access_key_id")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "your_secret_access_key")
AWS_REGION = "us-east-1"

firehose_client = boto3.client(
    "firehose",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)

firehose_stream_name = "btc_stream"  

def get_btc_price_from_coingecko():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            btc_price = data.get("bitcoin", {}).get("usd")
            if btc_price is not None:
                return float(btc_price)  
        else:
            print(f"Error accessing the CoinGecko API. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data from the CoinGecko API: {e}")
        return None

btc_price = get_btc_price_from_coingecko()

if btc_price is not None:
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")  
    current_time = now.strftime("%H:%M:%S")  

    data = {
        "date": current_date,
        "time": current_time,
        "btc_price_usd": f"{btc_price:,.2f}".replace(",", "") 
    }

    print("Captured data:", data)

    try:
        response = firehose_client.put_record(
            DeliveryStreamName=firehose_stream_name,
            Record={
                "Data": json.dumps(data)
            }
        )
        print("Data sent to Firehose:", response)
    except Exception as e:
        print("Error sending data to Firehose:", e)
else:
    print("Failed to capture Bitcoin price.")
