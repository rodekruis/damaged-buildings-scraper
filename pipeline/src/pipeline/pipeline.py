# -*- coding: utf-8 -*-
import os
import sys
import traceback
import pycurl
from io import BytesIO
import pandas as pd
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("requests_oauthlib").setLevel(logging.WARNING)

if os.path.exists("../credentials/.env"):
    load_dotenv(dotenv_path="../credentials/.env")
data_dir = '../data'


def get_blob_service_client(blob_path, container):
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("CONNECTION"))
    return blob_service_client.get_blob_client(container=container, blob=blob_path)


def upload_data(container, data_path='messages.csv', blob_path='messages.csv'):
    # upload data to azure blob storage
    blob_client = get_blob_service_client(blob_path, container)
    with open(data_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


def main():
    import datetime
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    count_skipped, count_translated, count_saved = 0, 0, 0

    try:
        # PART 1: DISTRICT SCRAPER
        provinces = pd.read_csv(os.path.join(data_dir, 'provinces.csv'))
        ilIds = provinces['id']
        url = "https://hasartespit.csb.gov.tr/query/counties?cityId=%d"
        ilId = ilIds[0]

        request = url % (ilId)

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, request)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        df = pd.json_normalize(pd.read_json(body.decode('utf-8'))['items'])
        df['province_id'] = ilId
        print(df)

        numberOfIds = len(ilIds)
        for i in range(1,numberOfIds):
            ilId = ilIds[i]
            print("%d out of %d" % (i, numberOfIds))
            request = url % (ilId)
            #print(request)
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, request)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            c.close()
            body = buffer.getvalue()
            df1 = pd.json_normalize(pd.read_json(body.decode('utf-8'))['items'])
            df1['province_id'] = ilId
            df = df.append(df1)

        df.to_csv(os.path.join(data_dir, 'districts.csv'), encoding='utf-8')

        # PART 2: NEIGHBORHOOD SCRAPER
        districts = pd.read_csv(os.path.join(data_dir, 'districts.csv'))
        ilIds = districts['province_id']
        ilceIds = districts['id']
        url = "https://hasartespit.csb.gov.tr/query/districts?countyId=%d"
        ilceId = ilceIds[0]

        request = url % (ilceId)

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, request)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        df = pd.json_normalize(pd.read_json(body.decode('utf-8'))['items'])
        df['province_id'] = ilIds[0]
        df['district_id'] = ilceId

        numberOfIds = len(ilceIds)
        for i in range(1, numberOfIds):
            ilceId = ilceIds[i]
            print("%d out of %d" % (i, numberOfIds))
            request = url % (ilceId)
            # print(request)
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, request)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            c.close()
            body = buffer.getvalue()
            df1 = pd.json_normalize(pd.read_json(body.decode('utf-8'))['items'])
            df1['province_id'] = ilIds[i]
            df1['district_id'] = ilceId
            df = df.append(df1)

        df.to_csv(os.path.join(data_dir, 'neighborhoods.csv'), encoding='utf-8')

        # PART 3: UPLOAD TO DATALAKE
        container = "emergencies"
        directory = "turkey-syria-earthquake-2023"
        upload_data(container, os.path.join(data_dir, 'districts.csv'), os.path.join(directory, 'districts.csv'))
        upload_data(container, os.path.join(data_dir, 'neighborhoods.csv'), os.path.join(directory, 'neighborhoods.csv'))

    except Exception as e:
        logging.error(f"{e}")
        traceback.print_exception(*sys.exc_info())

    logging.info("Pipeline ran at %s", utc_timestamp)
    logging.info(f"{count_skipped} articles skipped, {count_translated} translated, {count_saved} saved")


if __name__ == "__main__":
    main()
