import pandas as pd
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import certifi
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def query_influx_mean(parameters, start_date, end_date, sampling_rate):

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


    # Query numeric fields (downsampled)
    for param in numeric_params:
        query = f'''
        from(bucket: "{bucket}")
        |> range(start: {start_date}, stop: {end_date})
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
        |> range(start: {start_date}, stop: {end_date})
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

def query_influx_sum(parameters, start_date, end_date, sampling_rate):

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


    # Query numeric fields (downsampled)
    for param in numeric_params:
        query = f'''
        from(bucket: "{bucket}")
        |> range(start: {start_date}, stop: {end_date})
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["_field"] == "{param}")
        |> aggregateWindow(every: {sampling_rate}, fn: sum, createEmpty: false)
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
        |> range(start: {start_date}, stop: {end_date})
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

def get_first_and_last_date():

    parameters = 'Temp (°C)'
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

    query_api = client.query_api()

    # Query for the first timestamp
    first_date_query = f'''
        from(bucket: "{bucket}")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["_field"] == "{parameters}")
        |> sort(columns: ["_time"], desc: false)
        |> first()
        |> keep(columns: ["_time"])
    '''

    # Query for the last timestamp
    last_date_query = f'''
        from(bucket: "{bucket}")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["_field"] == "{parameters}")
        |> sort(columns: ["_time"], desc: true)
        |> first()
        |> keep(columns: ["_time"])
    '''
    
    # Execute queries
    first_tables = query_api.query(first_date_query)
    last_tables = query_api.query(last_date_query)

    client.close()

    # Extract timestamps
    first_date = first_tables[0].records[0]["_time"] if first_tables else None
    last_date = last_tables[0].records[0]["_time"] if last_tables else None

    # Convert to pandas Timestamp
    first_date = pd.to_datetime(first_date) if first_date else None
    last_date = pd.to_datetime(last_date) if last_date else None
    
    return first_date, last_date
