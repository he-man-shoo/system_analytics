import pandas as pd
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import certifi
import os
from dotenv import load_dotenv
from functools import lru_cache

# Load environment variables from .env file
load_dotenv()

# InfluxDB connection settings
_url = "https://us-east-1-1.aws.cloud2.influxdata.com"
_token = os.environ.get('influx_token')
_org = "System Analytics Tool"
_bucket = "site_data"
_timeout = 60_000
_ssl_ca_cert = certifi.where()
_measurement = "Origis_GT2_Test_3"

# Singleton client and query API
_client = InfluxDBClient(
    url=_url,
    token=_token,
    org=_org,
    timeout=_timeout,
    ssl_ca_cert=_ssl_ca_cert
)
_query_api = _client.query_api()

def query_influx_database(parameters, agg_function, start_date, end_date, sampling_rate):

    if isinstance(parameters, str):
        parameters = [p.strip() for p in parameters.split(",")]

    string_fields = ["cycle marker"]  # Add any other string fields here
    numeric_fields = [p for p in parameters if p not in string_fields]

    numeric_fields_filter = " or ".join(f'r._field == "{p}"' for p in numeric_fields)
    string_fields_filter = " or ".join(f'r._field == "{p}"' for p in string_fields)

    # Query numeric fields (downsampled)
    query = f'''
        from(bucket: "{_bucket}")
        |> range(start: {start_date}, stop: {end_date})
        |> filter(fn: (r) => r["_measurement"] == "{_measurement}" and ({numeric_fields_filter}))
        |> aggregateWindow(every: {sampling_rate}, fn: {agg_function}, createEmpty: false)
        |> keep(columns: ["_time", "_field", "_value"])
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
    df = _query_api.query_data_frame(query, org=_org)

    # Merge numeric fields
    if len(df) > 1:
        df_merged = df
        df_merged = df_merged.loc[:,~df_merged.columns.duplicated()]
    else:
        df_merged = pd.DataFrame()

    # Query and downsample "cycle marker" (last per window)
    if string_fields:
        query = f'''
        from(bucket: "{_bucket}")
        |> range(start: {start_date}, stop: {end_date})
        |> filter(fn: (r) => r["_measurement"] == "{_measurement}" and ({string_fields_filter}))
        |> aggregateWindow(every: {sampling_rate}, fn: last, createEmpty: false)
        |> keep(columns: ["_time", "_field", "_value"])
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        df_cycle = _query_api.query_data_frame(query, org=_org)
        # Merge with numeric data on _time
        if not df_cycle.empty:
            df_merged = pd.merge(df_merged, df_cycle, on="_time", how="outer")

    return df_merged

@lru_cache(maxsize=1)
def get_first_and_last_date():

    parameters = 'Temp (°C)'

    # Query for the first timestamp
    first_date_query = f'''
        from(bucket: "{_bucket}")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "{_measurement}")
        |> filter(fn: (r) => r["_field"] == "{parameters}")
        |> sort(columns: ["_time"], desc: false)
        |> first()
        |> keep(columns: ["_time"])
    '''

    # Query for the last timestamp
    last_date_query = f'''
        from(bucket: "{_bucket}")
        |> range(start: 0, stop: now())
        |> filter(fn: (r) => r["_measurement"] == "{_measurement}")
        |> filter(fn: (r) => r["_field"] == "{parameters}")
        |> sort(columns: ["_time"], desc: true)
        |> first()
        |> keep(columns: ["_time"])
    '''
    
    # Execute queries
    first_tables = _query_api.query(first_date_query, org=_org)
    last_tables = _query_api.query(last_date_query, org=_org)

    # Extract timestamps
    first_date = first_tables[0].records[0]["_time"] if first_tables else None
    last_date = last_tables[0].records[0]["_time"] if last_tables else None

    # Convert to pandas Timestamp
    first_date = pd.to_datetime(first_date) if first_date else None
    last_date = pd.to_datetime(last_date) if last_date else None
    
    return first_date, last_date

_client.close()
