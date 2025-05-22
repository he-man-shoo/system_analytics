import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash import dcc
import pandas as pd
import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import certifi


from trend_plots import generate_soc_plot, generate_avail_plot, temp_aux_plot
from read_Influx_db import query_influx


dash.register_page(__name__, name="Analytics", path="/", order=0)

# Colors
prevalon_purple = 'rgb(72,49,120)'
prevalon_lavender = 'rgb(166,153,193)'
prevalon_yellow = 'rgb(252,215,87)'
prevalon_cream = 'rgb(245,225,164)'
prevalon_slate = 'rgb(208,211,212)'
prevalon_gray = 'rgb(99,102,106)'


# Define the layout of the website
layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Analytics Dashboard", 
                        className='text-center text-primary-emphasis'),
                        xs=12, sm=12, md=12, lg=6, xl=6, style={'text-align': 'center'}),
    ], justify='around', align='center'),

    html.Br(),

    dbc.Row([
        dbc.Col([html.H5("Select Date Range",  
                        className='text-center text-primary-emphasis'),
                        ], xs=12, sm=12, md=12, lg=6, xl=6, style={'text-align': 'center'}),

        dbc.Col([html.H5("Select Sampling Rate",  
                        className='text-center text-primary-emphasis'),
                        ], xs=12, sm=12, md=12, lg=6, xl=6, style={'text-align': 'center'}),

                        ], justify='center', align='center'),

    dbc.Row([
        dbc.Col([
            html.A(children=dcc.DatePickerRange(
                                id='date_picker',
                                start_date='2025-04-20',  # Initial start date
                                end_date='2025-05-01',    # Initial end date
                                min_date_allowed='2024-05-01',
                                max_date_allowed='2025-05-01', 
                                style={'text-align': 'center'},), 
                                style={'text-align': 'center'})
                ], xs=12, sm=12, md=12, lg=6, xl=6),
        dbc.Col([
            dcc.Dropdown(
                id='dwn_sample_dropdown', 
                options=[
                    {'label': '1 min', 'value': '1m'},
                    {'label': '1 hr', 'value': '1h'},
                    {'label': '6 hr', 'value': '6h'},
                    {'label': '12 hr', 'value': '12h'},
                    {'label': '24 hr', 'value': '24h'},
                    {'label': '48 hr', 'value': '48h'},
                    {'label': '72 hr', 'value': '72h'},],
                value = '6h', 
                style={'text-align': 'center'}),  # Default value),
                ], xs=12, sm=12, md=12, lg=2, xl=2),

    ], justify='center', align='center'),

    html.Br(),

    dbc.Row([
        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "soc_trend", style = {"height":"80%", "width":"100%"},
                                    )
                        ),
                    ], xs=12, sm=12, md=12, lg=12, xl=12),
    ], justify='around', align='center'),

    dbc.Row([
        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "aux_temp_trend", style = {"height":"80%", "width":"100%"},
                                    )
                        ),
                    ], xs=12, sm=12, md=12, lg=12, xl=12),
    ], justify='around', align='center'),

    dbc.Row([
        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "avail_trend", style = {"height":"80%", "width":"100%"},
                                    )
                        ),
                    ], xs=12, sm=12, md=12, lg=12, xl=12),
    ], justify='around', align='center'),


    html.Br(),



], fluid=True),


@dash.callback(
    Output('soc_trend', 'figure'),
    Output('avail_trend', 'figure'),
    Output('aux_temp_trend', 'figure'),
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date'),
     Input('dwn_sample_dropdown', 'value')]
)
def update_plot(start_date, end_date, sampling_rate):

    return (
        generate_soc_plot(query_influx("avail soc %, cycle marker", start_date, end_date, sampling_rate)),
        generate_avail_plot(query_influx("availability %", start_date, end_date, sampling_rate)),
        temp_aux_plot(query_influx("p_aux (w), Temp (°C), SHGF (W/m²), cycle marker", start_date, end_date, sampling_rate))
    )