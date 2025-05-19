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
            html.P("Last 30 days", id='btn_30d', n_clicks=0, className="btn btn-warning m-2"),
            html.P("Last 60 days", id='btn_60d', n_clicks=0, className="btn btn-warning m-2"),
            html.P("Last 90 days", id='btn_90d', n_clicks=0, className="btn btn-warning m-2"),
            html.P("Last 365 days", id='btn_365d', n_clicks=0, className="btn btn-warning m-2"),
    ]),

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
            dbc.Spinner(dcc.Graph(id = "avail_trend", style = {"height":"80%", "width":"100%"},
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

    html.Br(),



], fluid=True), 


@dash.callback(
    Output('soc_trend', 'figure'),
    Output('avail_trend', 'figure'),
    Output('aux_temp_trend', 'figure'),
    [Input('btn_30d', 'n_clicks'),
     Input('btn_60d', 'n_clicks'),
     Input('btn_90d', 'n_clicks'),
     Input('btn_365d', 'n_clicks'),]
)
def update_plot(btn_30d, btn_60d, btn_90d, btn_365d):
    ctx = dash.callback_context

    if not ctx.triggered:
        return generate_soc_plot(query_influx("avail soc %, cycle marker", 60, 1)), generate_avail_plot(query_influx("availability %", 60, 1)), temp_aux_plot(query_influx("p_aux (w), Temp (°C), SHGF (W/m²)", 60, 1))

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn_30d':
        return generate_soc_plot(query_influx("avail soc %, cycle marker", 30, 1)), generate_avail_plot(query_influx("availability %", 30, 1)), temp_aux_plot(query_influx("p_aux (w), Temp (°C), SHGF (W/m²)", 30, 1))
    elif button_id == 'btn_60d':
        return generate_soc_plot(query_influx("avail soc %, cycle marker", 60, 1)), generate_avail_plot(query_influx("availability %", 60, 1)), temp_aux_plot(query_influx("p_aux (w), Temp (°C), SHGF (W/m²)", 60, 1))
    elif button_id == 'btn_90d':
        return generate_soc_plot(query_influx("avail soc %, cycle marker", 90, 1)), generate_avail_plot(query_influx("availability %", 90, 1)), temp_aux_plot(query_influx("p_aux (w), Temp (°C), SHGF (W/m²)", 90, 1))
    elif button_id == 'btn_365d':
        return generate_soc_plot(query_influx("avail soc %, cycle marker", 365, 1)), generate_avail_plot(query_influx("availability %", 365, 1)), temp_aux_plot(query_influx("p_aux (w), Temp (°C), SHGF (W/m²)", 365, 1))
    else:
        raise PreventUpdate
    
