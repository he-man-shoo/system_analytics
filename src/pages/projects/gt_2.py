import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from datetime import datetime
from dash.exceptions import PreventUpdate



from trend_plots import generate_soc_plot, generate_avail_plot, temp_aux_plot, generate_rte_plot, generate_throughput_plot
from read_Influx_db import query_influx_mean, get_first_and_last_date, query_influx_sum
from table_layout import table_format

dash.register_page(__name__, name="Golden Triangle II", path="/projects/gt_2", order=0)

# Colors
prevalon_purple = 'rgb(72,49,120)'
prevalon_lavender = 'rgb(166,153,193)'
prevalon_yellow = 'rgb(252,215,87)'
prevalon_cream = 'rgb(245,225,164)'
prevalon_slate = 'rgb(208,211,212)'
prevalon_gray = 'rgb(99,102,106)'


default_button_style = {
            'backgroundColor': prevalon_yellow,  # Yellow background
            'padding': '10px',  # Padding to match button size
            'fontSize': '18px',  # Font size
            'fontWeight': 'bold',  # Bold text
            'color': prevalon_purple,  # Dark text color (adjust as needed)
            'textAlign': 'center',
            'textDecoration': 'none',
            'cursor': 'pointer',
            'borderRadius': '0',  # No rounding, matching the image
            'display': 'inline-block',
            'margin': '5px',  # Margin between buttons
        }

active_button_style = {
    **default_button_style,
    'backgroundColor': prevalon_purple,  # Purple background for active button
    "color": "white",  # White text for better contrast
    "fontWeight": "bold",
}

proj_name = "Golden Triangle II"
proj_details = pd.read_excel('Project Details.xlsx')
proj_details = proj_details[proj_details['Project'] == proj_name]

proj_details = proj_details.T

proj_details[1] = proj_details[0]
proj_details[0] = proj_details.index

# Convert 'In Operation since' to 'Month-Year' format
proj_details.loc['In Operation since', 1] = pd.to_datetime(proj_details.loc['In Operation since', 1]).strftime('%B-%Y')

proj_details.columns = proj_details.iloc[1]

proj_details = proj_details[2:]


project_image = Image.open("GT2_Site.jpg")

# Define the layout of the website
layout = dbc.Container([
    
    dbc.Row([
        dbc.Col(html.H2("Golden Triangle II", 
                        className='text-center text-primary-emphasis'),
                        xs=12, sm=12, md=12, lg=6, xl=6, style={'text-align': 'center'}),
    ], justify='around', align='center'),
    
    html.Br(),

    dbc.Row([
        dbc.Col(
            html.Img(src=project_image, style={'width': '100%', 'height': '100%'}),
            width=6
        ),

        dbc.Col([
            html.H3("Project Details :", style={'color':prevalon_purple, 'display': 'inline-block'}),
            html.Br(),
            html.Br(),

            dbc.Container(
            [
                html.P(id='proj_details_table', children=table_format(proj_details)), 
            ]),
            html.Br(),

            html.H4("Click on the links below to see As-Built GA, SAT results, etc. :", style={'color':prevalon_purple, 'display': 'inline-block'}),
            
            html.Br(),
            html.Br(),

            html.Div([
                html.A(
                    html.Img(
                        src="/assets/icon_layout.png",
                        style={"height": "90px", "verticalAlign": "middle"}
                    ),
                    href="https://prevalonenergy.sharepoint.com/:b:/r/sites/Proposals/Shared%20Documents/General/System%20Analytics%20Tool%20-%20Attachments/BC-C01-02_%20BESS%20-%20GOLDEN%20TRIANGLE%202%20GT2%20GENERAL%20ARRANGEMENT%20Rev.0%20markup.pdf?csf=1&web=1&e=yi2GQn",
                    target="_blank",
                    title="General Arrangement Drawing of the Site",  # Hover text
                    style={"display": "inline-block",}
                ),
                html.A("", style={"display": "inline-block", "width": "60px"}),  # Spacer
                html.A(
                    html.Img(
                        src="/assets/icon_sat.png",
                        style={"height": "90px", "verticalAlign": "middle"}
                    ),
                    href="https://prevalonenergy.sharepoint.com/:x:/r/sites/Proposals/Shared%20Documents/General/System%20Analytics%20Tool%20-%20Attachments/GT2%20Performance%20Test%20Report%20REV3.xlsx?d=wb33885c67aef43aca3b3c647b71a5fca&csf=1&web=1&e=4SpIsQ",
                    target="_blank",
                    title="Site Acceptance Test Result",  # Hover text
                    style={"display": "inline-block"}
                ),
                # html.A("", style={"display": "inline-block", "width": "60px"}),  # Spacer
            ], style={"textAlign": "center"}),



        ], width=6, style={'text-align': 'left', 'margin-top': '10px'})
    ]),
    

    html.Br(),


    dbc.Row([
        dbc.Col([
                html.A(children=[
                    html.Button('1 Day', id='btn_1D', n_clicks=0, style = default_button_style),
                    html.Button('1 Week', id='btn_1W', n_clicks=0, style = default_button_style),
                    html.Button('1 Month', id='btn_1M', n_clicks=0, style = default_button_style),
                    html.Button('3 Months', id='btn_3M', n_clicks=0, style = default_button_style),
                    html.Button('Year to Date', id='btn_YTD', n_clicks=0, style = default_button_style),
                    html.Button('1 Year', id='btn_1Y', n_clicks=0, style = default_button_style),
                    html.Button('All Time', id='btn_ALL', n_clicks=0, style = default_button_style),
                    ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin-top': '25px'}
                ),
                ], xs=12, sm=12, md=12, lg=8, xl=8),

    ], justify='center', align='center'),

    html.Br(),

    dbc.Row([
        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "avail_trend", style = {"height":"80%", "width":"100%"},
                                    )
                        ),
                    ], xs=12, sm=12, md=12, lg=6, xl=6),
        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "throughput_trend", style = {"height":"80%", "width":"100%"},
                                    )
                        ),
                    ], xs=12, sm=12, md=12, lg=6, xl=6),
    ], justify='around', align='center'),

    html.Br(),

    dbc.Row([

        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "rte_trend", style = {"height":"100%", "width":"100%"},
                                  figure =generate_rte_plot()
                                    )
                        ),
                    ], xs=12, sm=12, md=12, lg=6, xl=6),

        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "e", style = {"height":"100%", "width":"100%"},
                                figure = go.Figure().update_layout(title=f"Development in Progress - Average Resting SOC"))

                        )
                    ], xs=12, sm=12, md=12, lg=6, xl=6),

    ], justify='around', align='center'),

    dbc.Row([

        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "f", style = {"height":"100%", "width":"100%"},
                                  figure = go.Figure().update_layout(title=f"Development in Progress - SOH"))
                        ),
                    ], xs=12, sm=12, md=12, lg=6, xl=6),

        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "g", style = {"height":"100%", "width":"100%"},
                                figure = go.Figure().update_layout(title=f"Development in Progress - Revenue Generated $$"))
                        ),
                    ], xs=12, sm=12, md=12, lg=6, xl=6),

    ], justify='around', align='center'),

    dbc.Row([

        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "i", style = {"height":"100%", "width":"100%"},
                                  figure = go.Figure().update_layout(title=f"Development in Progress - Temp and Voltage"))
                        ),
                    ], xs=12, sm=12, md=12, lg=6, xl=6),

        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "j", style = {"height":"100%", "width":"100%"},
                                figure = go.Figure().update_layout(title=f"Development in Progress - CO2 emissions avoided"))
                        ),
                    ], xs=12, sm=12, md=12, lg=6, xl=6),

    ], justify='around', align='center'),

], fluid=True),

@dash.callback(
    Output('avail_trend', 'figure'),
    Output('throughput_trend', 'figure'),
    Output("btn_1D", "style"),
    Output("btn_1W", "style"),
    Output("btn_1M", "style"),
    Output("btn_3M", "style"),
    Output("btn_YTD","style"),
    Output("btn_1Y", "style"),
    Output("btn_ALL","style"),
    [Input('btn_1D', 'n_clicks'),
     Input('btn_1W', 'n_clicks'),
     Input('btn_1M', 'n_clicks'),
     Input('btn_3M', 'n_clicks'),
     Input('btn_YTD', 'n_clicks'),
     Input('btn_1Y', 'n_clicks'),
     Input('btn_ALL', 'n_clicks')]
)
def update_plot(btn_1D, btn_1W, btn_1M, btn_3M, btn_YTD, btn_1Y, btn_ALL):
    ctx = dash.callback_context
    first_date, last_date = get_first_and_last_date()

    if not ctx.triggered or ctx.triggered[0]['prop_id'] == '.':
        start_date = last_date - pd.offsets.MonthEnd(1) # Default
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_date = last_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        btn_ids = ["btn_1D","btn_1W","btn_1M","btn_3M","btn_YTD","btn_1Y","btn_ALL"]
        button_id = "btn_1M"  # Default button
        styles = [
        active_button_style if btn == button_id else default_button_style
        for btn in btn_ids
        ]
        return generate_avail_plot(query_influx_mean("availability %", start_date, last_date, '1h')), generate_throughput_plot(query_influx_sum("kwh discharged @ timestamp", start_date, last_date, '1d')), *styles

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # build style list: active_style for the clicked one, default for the rest
    btn_ids = ["btn_1D","btn_1W","btn_1M","btn_3M","btn_YTD","btn_1Y","btn_ALL"]
    styles = [
        active_button_style if btn == button_id else default_button_style
        for btn in btn_ids
    ]
    
    if button_id == 'btn_1D':
        start_date = last_date - pd.Timedelta(days=1)
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_date = last_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        return generate_avail_plot(query_influx_mean("availability %", start_date, last_date, '5m')), generate_throughput_plot(query_influx_sum("kwh discharged @ timestamp", start_date, last_date, '1h')), *styles
    if button_id == 'btn_1W':
        start_date = last_date - pd.Timedelta(days=7)
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_date = last_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        return generate_avail_plot(query_influx_mean("availability %", start_date, last_date, '1h')), generate_throughput_plot(query_influx_sum("kwh discharged @ timestamp", start_date, last_date, '1d')), *styles
    if button_id == 'btn_1M':
        start_date = last_date - pd.offsets.MonthEnd(1)
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_date = last_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        return generate_avail_plot(query_influx_mean("availability %", start_date, last_date, '1h')), generate_throughput_plot(query_influx_sum("kwh discharged @ timestamp", start_date, last_date, '1w')), *styles
    elif button_id == 'btn_3M':
        start_date = last_date - pd.offsets.MonthEnd(3)
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_date = last_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        return generate_avail_plot(query_influx_mean("availability %", start_date, last_date, '1d')), generate_throughput_plot(query_influx_sum("kwh discharged @ timestamp", start_date, last_date, '1mo')), *styles
    elif button_id == 'btn_YTD':
        start_date = last_date - pd.offsets.YearBegin(1)
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_date = last_date.strftime('%Y-%m-%dT%H:%M:%SZ')    
        return generate_avail_plot(query_influx_mean("availability %", start_date, last_date, '1d')), generate_throughput_plot(query_influx_sum("kwh discharged @ timestamp", start_date, last_date, '1mo')), *styles
    elif button_id == 'btn_1Y':
        start_date = last_date - pd.Timedelta(days=365)
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_date = last_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        return generate_avail_plot(query_influx_mean("availability %", start_date, last_date, '1d')), generate_throughput_plot(query_influx_sum("kwh discharged @ timestamp", start_date, last_date, '1mo')), *styles
    elif button_id == 'btn_ALL':
        start_date = first_date
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        last_date = last_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        return generate_avail_plot(query_influx_mean("availability %", start_date, last_date, '1d')), generate_throughput_plot(query_influx_sum("kwh discharged @ timestamp", start_date, last_date, '1mo')), *styles
    else:
        raise PreventUpdate
