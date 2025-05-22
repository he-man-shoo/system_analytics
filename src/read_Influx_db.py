import pandas as pd
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import certifi
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def query_influx(parameters, start_date, end_date, sampling_rate):

    # Your InfluxDB Cloud credentials
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"  # Replace with your region
    token = os.environ.get('influx_token') # Replace with your token
    org = "System Analytics Tool"                                  # Replace with your org
    bucket = "site_data"                            # Replace with your bucket
    timeout=60_000  # in milliseconds
    ssl_ca_cert=certifi.where()
    measurement = "Origis_GT2_Test_2"

    # Initialize client
    client = InfluxDBClient(url=url, token=token, org=org, timeout=timeout, ssl_ca_cert=ssl_ca_cert)

    if isinstance(parameters, str):
        parameters = [p.strip() for p in parameters.split(",")]

    string_fields = ["cycle marker"]  # Add any other string fields here
    numeric_params = [p for p in parameters if p not in string_fields]
    dfs = []

    todays_date = pd.Timestamp.now().date().day

    # Query numeric fields (downsampled)
    for param in numeric_params:
        query = f'''
        from(bucket: "{bucket}")
        |> range(start: {start_date}T00:00:00Z, stop: {end_date}T23:59:59Z)
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["_field"] == "{param}")
        |> aggregateWindow(every: {sampling_rate}, fn: mean, createEmpty: false)
        |> keep(columns: ["_time", "_field", "_value"])
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        df = client.query_api().query_data_frame(query, org=org)
        dfs.append(df)

    # Merge numeric fields
    if dfs:
        df_merged = pd.concat(dfs, axis=1)
        df_merged = df_merged.loc[:,~df_merged.columns.duplicated()]
    else:
        df_merged = pd.DataFrame()

    # Query and downsample "cycle marker" (mode per window)
    if "cycle marker" in parameters:
        query = f'''
        from(bucket: "{bucket}")
        |> range(start: {start_date}T00:00:00Z, stop: {end_date}T23:59:59Z)
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["_field"] == "cycle marker")
        |> aggregateWindow(every: {sampling_rate}, fn: last, createEmpty: false)
        |> keep(columns: ["_time", "_field", "_value"])
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        df_cycle = client.query_api().query_data_frame(query, org=org)
        # Merge with numeric data on _time
        if not df_cycle.empty:
            df_merged = pd.merge(df_merged, df_cycle[["_time", "cycle marker"]], on="_time", how="outer")

    client.close()

    return df_merged