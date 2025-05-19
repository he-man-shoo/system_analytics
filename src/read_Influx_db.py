import pandas as pd
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import certifi


def query_influx(parameters, days, dwn_sample):
    # Your InfluxDB Cloud credentials
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"  # Replace with your region
    token = "HTQqAand6fDNv3-MN7xaJChz6tmrECXrcqEKI56Qzu8imWH5PxIyPR4W0Luse3nWm9LK2Qk_Ip1oMAP9V8BbfQ=="                               # Replace with your token
    org = "System Analytics Tool"                                  # Replace with your org
    bucket = "site_data"                            # Replace with your bucket
    timeout=60_000  # in milliseconds
    ssl_ca_cert=certifi.where()
    measurement = "Origis_GT2_Test_2"

    # Initialize client
    client = InfluxDBClient(url=url, token=token, org=org, timeout=timeout, ssl_ca_cert=ssl_ca_cert)

    if isinstance(parameters, str):
        parameters = [p.strip() for p in parameters.split(",")]

    dfs = []
    string_fields = ["cycle marker"]  # Add any other string fields here

    for param in parameters:
        if param in string_fields:
            query = f'''
            from(bucket: "{bucket}")
            |> range(start: -{days}d)
            |> filter(fn: (r) => r["_measurement"] == "{measurement}")
            |> filter(fn: (r) => r["_field"] == "{param}")
            |> keep(columns: ["_time", "_field", "_value"])
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
        else:
            query = f'''
            from(bucket: "{bucket}")
            |> range(start: -{days}d)
            |> filter(fn: (r) => r["_measurement"] == "{measurement}")
            |> filter(fn: (r) => r["_field"] == "{param}")
            |> aggregateWindow(every: {dwn_sample}h, fn: mean, createEmpty: false)
            |> keep(columns: ["_time", "_field", "_value"])
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''

        df = client.query_api().query_data_frame(query, org=org)
        dfs.append(df)

        if dfs:
            df_merged = pd.concat(dfs, axis=1)
            df_merged = df_merged.loc[:,~df_merged.columns.duplicated()]  # Remove duplicate columns
        else:
            df_merged = pd.DataFrame()

    client.close()

    print(df_merged.head())

    return df_merged