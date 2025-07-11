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
import plotly.express as px
import plotly.graph_objects as go




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

df_rte_analysis = pd.read_excel('RTE_filtered.xlsx')

df_rte_analysis['Start Time'] = pd.to_datetime(df_rte_analysis['Start Time'])
df_rte_analysis['year_month'] = df_rte_analysis['Start Time'].dt.to_period('M')

# Get unique year_month values and sort them
year_months = sorted(df_rte_analysis['year_month'].astype(str).unique())
slider_marks = {i: ym for i, ym in enumerate(year_months)}

rte_trend_data = pd.read_excel('rte_trend_data.xlsx')

fig_2 = go.Figure()

# Add scatter for median_rte
fig_2.add_trace(go.Scatter(
    x=rte_trend_data['year_month'],
    y=rte_trend_data['median_rte'],
    mode='lines + markers',
    name='Median RTE from Analysis',
    marker=dict(color=prevalon_yellow, symbol='circle'),
    line=dict(color=prevalon_yellow), 
    connectgaps=True  # <-- This connects points even with None/NaN values

))

# Add scatter for tested_rte
fig_2.add_trace(go.Scatter(
    x=rte_trend_data['year_month'],
    y=rte_trend_data['tested_rte'],
    mode='lines+markers',
    name='Tested RTE',
    marker=dict(color=prevalon_purple, symbol='diamond'),
    line=dict(color=prevalon_purple, dash='dash'), 
    connectgaps=True  # <-- This connects points even with None/NaN values
))

# Add scatter for tested_rte
fig_2.add_trace(go.Scatter(
    x=rte_trend_data['year_month'],
    y=rte_trend_data['contracted_rte'],
    mode='lines+markers',
    name='Contracted RTE',
    marker=dict(color='red', symbol='diamond'),
    line=dict(color='red', dash='dash'), 
    connectgaps=True  # <-- This connects points even with None/NaN values
))

# Show Y axis as percentage and display legend
fig_2.update_layout(
    plot_bgcolor='rgb(255, 255, 255)',
    paper_bgcolor='rgb(255, 255, 255)',
    title='RTE Trend over time',
    xaxis_title='Month',
    yaxis_title='RTE (%)',
    yaxis_tickformat='.2%',
    showlegend=True,
    legend=dict(
        orientation="h",  # Horizontal legend
        yanchor="bottom",  # Anchor to the bottom
        y=-0.5,  # Position below the plot
        xanchor="center",  # Center the legend
        x=0.5  # Center horizontally
    ),      
)

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

    dbc.Row([
        dbc.Col([
            html.H5("Round Trip Efficiency",),
        ], xs=12, sm=12, md=12, lg=12, xl=12), 
    ], justify='around', align='center'),
    
    html.Br(),

    dbc.Row([
        dbc.Col([
            html.H6("Monthly RTE Distribution",),
        ], xs=12, sm=12, md=12, lg=12, xl=12), 
    ], justify='center', align='center'),
    
    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Div(
                dcc.Slider(
                    min=0,
                    max=len(year_months)-1,
                    step=1,
                    value=0,
                    marks=slider_marks,
                    id='month_slider',
                    included=False
                ),
                style={"whiteSpace": "nowrap", "width": "100%"}
            ),

        ], xs=12, sm=12, md=12, lg=6, xl=6),

    ], justify='left', align='left'),


    dbc.Row([
        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "monthly_rte", style = {"height":"80%", "width":"100%"},
                                    )
                        ),
                    ], xs=12, sm=12, md=12, lg=6, xl=6),
        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "rte_trend", style = {"height":"80%", "width":"100%"},
                                  figure=fig_2
                                    )
                        ),
                    ], xs=12, sm=12, md=12, lg=6, xl=6),
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

@dash.callback(
    Output('monthly_rte', 'figure'),
    [Input('month_slider', 'value'),]
)
def update_plot(slider_value):

    year_month = year_months[slider_value]

    df_monthly_rte = df_rte_analysis.copy()
    df_monthly_rte = df_monthly_rte.loc[df_monthly_rte['year_month'] == year_month]

    # Convert RTE to percent
    df_monthly_rte['RTE_percent'] = df_monthly_rte['RTE'] * 100
    median_rte = df_monthly_rte['RTE_percent'].median()

    # Plot histogram for the month using Plotly Express
    fig = px.histogram(
        df_monthly_rte,
        x='RTE_percent',
        nbins=10,
        labels={'RTE_percent': 'RTE (%)', 'count': 'Count'},
        color_discrete_sequence=['skyblue'], 
        title=f"Round Trip Efficiency Distribution for {year_month}. Median RTE: {median_rte:.2f}%",
    )

    fig.update_layout(
        plot_bgcolor='rgb(255,255,255)',  # or prevalon_cream, prevalon_slate
        paper_bgcolor='rgb(255,255,255)',
        bargap=0.1, 
        xaxis=dict(range=[60, 100])  # Set x-axis range from 60% to 100%
    )

    
    # Ensure 'year_month' is string for plotting
    rte_trend_data['year_month'] = rte_trend_data['year_month'].astype(str)

    return fig