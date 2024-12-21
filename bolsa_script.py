from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time
import pandas as pd
import boto3
from datetime import datetime
import unidecode

load_dotenv()

S3_BUCKET_NAME = "vhts-fiap-tech-challenge2"
S3_REGION = "us-east-1"
S3_RAW_PREFIX = "bolsa_bovespa/raw"

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "your_access_key_id")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "your_secret_access_key")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", None)


def init_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    current_dir = os.getcwd()
    download_dir = os.path.join(current_dir, "downloads")
    os.makedirs(download_dir, exist_ok=True)
    prefs = {"download.default_directory": download_dir, "download.prompt_for_download": False}
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver, download_dir


def download_csv_b3():
    url = "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br"
    driver, download_dir = init_webdriver()
    try:
        driver.get(url)
        time.sleep(5)

        download_button = driver.find_element(By.LINK_TEXT, "Download")
        download_button.click()
        print(f"Download started! The file will be saved to: {download_dir}")

        time.sleep(10)

        csv_file = max([os.path.join(download_dir, f) for f in os.listdir(download_dir)], key=os.path.getctime)
        print(f"File downloaded: {csv_file}")
        return csv_file

    except Exception as e:
        print(f"Error downloading the CSV: {e}")
    finally:
        driver.quit()


def extract_date_from_filename(filename):
    try:
        basename = os.path.basename(filename)
        date_str = basename.split("_")[-1].replace(".csv", "")
        formatted_date = datetime.strptime(date_str, "%d-%m-%y").strftime("%Y-%m-%d")
        return formatted_date
    except Exception as e:
        print(f"Error extracting date from filename: {e}")
        return None


def preprocess_csv(file_path):
    try:
        print(f"Preprocessing CSV file: {file_path}")

        with open(file_path, "r", encoding="latin-1") as f:
            lines = f.readlines()

        lines = lines[1:-2]

        lines = [line.rstrip(";\n") + "\n" for line in lines]

        processed_file_path = file_path.replace(".csv", "_processed.csv")
        with open(processed_file_path, "w", encoding="latin-1") as f:
            f.writelines(lines)

        print(f"Preprocessed CSV saved to: {processed_file_path}")
        return processed_file_path

    except Exception as e:
        print(f"Error preprocessing CSV: {e}")
        return None


def convert_to_parquet(csv_file, date_partition):
    try:

        processed_file = preprocess_csv(csv_file)
        if not processed_file:
            print("Error preprocessing the CSV file.")
            return None


        df = pd.read_csv(processed_file, encoding='latin-1', sep=';')

        df["Qtde. Teórica"] = (
            df["Qtde. Teórica"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        df["Part. (%)"] = (
            df["Part. (%)"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        df["Data"] = date_partition


        parquet_file = csv_file.replace(".csv", ".parquet")
        df.to_parquet(parquet_file, engine="pyarrow", index=False)

        print(f"File successfully converted to Parquet: {parquet_file}")
        return parquet_file

    except Exception as e:
        print(f"Error converting to Parquet: {e}")
        return None


def upload_to_s3(file_path, s3_prefix, date_partition, is_parquet=False):
    try:
        s3_client = boto3.client(
            "s3",
            region_name=S3_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            aws_session_token=AWS_SESSION_TOKEN
        )

        partition = f"data_carteira={date_partition}"

        if is_parquet:

            s3_key = f"{s3_prefix}/bolsa.parquet"
        else:

            s3_key = f"{s3_prefix}/{partition}/{os.path.basename(file_path)}"


        s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        print(f"File uploaded to S3: s3://{S3_BUCKET_NAME}/{s3_key}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")


if __name__ == "__main__":
    csv_file = download_csv_b3()
    if csv_file:

        date_partition = extract_date_from_filename(csv_file)
        if not date_partition:
            print("Error: Could not extract date from filename.")
            exit(1)


        parquet_file = convert_to_parquet(csv_file, date_partition)
        if parquet_file:

            upload_to_s3(csv_file, S3_RAW_PREFIX, date_partition)
            upload_to_s3(parquet_file, S3_RAW_PREFIX, date_partition, is_parquet=True)
