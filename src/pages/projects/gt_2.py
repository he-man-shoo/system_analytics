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
from dash import callback_context as ctx



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

proj_power = float(proj_details.loc['Rated Power', 1].split()[0])  # in MW
proj_energy = float(proj_details.loc['Rated Energy', 1].split()[0])  # in MWh
proj_num_cyc = float(proj_details.loc['BESS Expected number of cycles/year', 1])

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
                                    )
                        ),
                    ], xs=12, sm=12, md=12, lg=6, xl=6),

        dbc.Col([ 
            dbc.Spinner(dcc.Graph(id = "resting_soc", style = {"height":"100%", "width":"100%"}
            )
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
    Output('rte_trend', 'figure'),
    Output('resting_soc', 'figure'),
    Output("btn_1D", "style"),
    Output("btn_1W", "style"),
    Output("btn_1M", "style"),
    Output("btn_3M", "style"),
    Output("btn_YTD","style"),
    Output("btn_1Y", "style"),
    Output("btn_ALL","style"),
    Input('btn_1D', 'n_clicks'),
    Input('btn_1W', 'n_clicks'),
    Input('btn_1M', 'n_clicks'),
    Input('btn_3M', 'n_clicks'),
    Input('btn_YTD', 'n_clicks'),
    Input('btn_1Y', 'n_clicks'),
    Input('btn_ALL', 'n_clicks'),
)
def update_plot(btn_1D, btn_1W, btn_1M, btn_3M, btn_YTD, btn_1Y, btn_ALL):
    # 1) Figure out which button was clicked (None if first load)
    triggered = None
    if ctx.triggered:
        prop = ctx.triggered[0].get("prop_id", "")
        if "." in prop:
            triggered = prop.split(".")[0]

    # 2) Whitelist & default
    valid = ["btn_1D","btn_1W","btn_1M","btn_3M","btn_YTD","btn_1Y","btn_ALL"]
    button_id = triggered if triggered in valid else "btn_1Y"

    # 3) Date bounds
    first_date, last_date = get_first_and_last_date()

    # 4) Map each button to its start‐offset & Flux windows
    cfg = {
        "btn_1D":  {"start": last_date - pd.Timedelta(days=1),    "freqs":("5m","1h")},
        "btn_1W":  {"start": last_date - pd.Timedelta(days=7),    "freqs":("1h","1d")},
        "btn_1M":  {"start": last_date - pd.offsets.MonthEnd(1),  "freqs":("1h","1w")},
        "btn_3M":  {"start": last_date - pd.offsets.MonthEnd(3),  "freqs":("1d","1mo")},
        "btn_YTD": {"start": last_date - pd.offsets.YearBegin(1), "freqs":("1d","1mo")},
        "btn_1Y":  {"start": last_date - pd.Timedelta(days=365),  "freqs":("1d","1mo")},
        "btn_ALL": {"start": first_date,                          "freqs":("1d","1mo")},
    }[button_id]

    # 5) Format ISO strings
    start_iso = cfg["start"].strftime('%Y-%m-%dT%H:%M:%SZ')
    end_iso   = last_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    # 6) Build figures
    freq_a, freq_t = cfg["freqs"]
    fig_avail   = generate_avail_plot(
        query_influx_mean("availability %", start_iso, end_iso, freq_a)
    )


    fig_through = generate_throughput_plot(
        query_influx_sum("kwh discharged @ timestamp", start_iso, end_iso, freq_t), 
        proj_energy, 
        proj_num_cyc,
    )

    fig_rte = generate_rte_plot(start_iso, end_iso)

    fig_resting_soc = generate_soc_plot(
        query_influx_mean(["avail soc %", "cycle marker"], start_iso, end_iso, freq_a), 
    )


    # 7) Highlight the active button
    default = default_button_style
    active  = active_button_style
    styles = [ active if btn==button_id else default
               for btn in valid ]

    return fig_avail, fig_through, fig_rte, fig_resting_soc, *styles