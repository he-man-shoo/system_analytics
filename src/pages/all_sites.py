import dash
from dash import html
import dash_bootstrap_components as dbc
from PIL import Image


dash.register_page(__name__, name="Entire Fleet", path="/", order=1)

# Colors
prevalon_purple = 'rgb(72,49,120)'
prevalon_lavender = 'rgb(166,153,193)'
prevalon_yellow = 'rgb(252,215,87)'
prevalon_cream = 'rgb(245,225,164)'
prevalon_slate = 'rgb(208,211,212)'
prevalon_gray = 'rgb(99,102,106)'


microgrid_icon = Image.open("microgrid_icon.png")
solar_panel_icon = Image.open("solar_panel_icon.png")
energy_icon = Image.open("energy_icon.png")


# Define the layout of the website
layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.Img(src = microgrid_icon, style={'width': '48px', 'height': '48px'}),            
            html.H3("Boulevard", style={'color': '#6B46C1'}),
            html.Ul([
                html.Li("Location: San Diego County, California"),
                html.Li("Size: 10 MW / 50 MWh"),
                html.Li("Application: Microgrid"),
                html.Li("Long-Term Service Agreement: 10 years"),
                html.Li("Emergency Backup Power for Critical Public Services")
            ])
        ], width=5, style={'padding': '10px', 'background-color': '#F7FAFC', 'margin': '10px'}),

        dbc.Col([
            html.Img(src = energy_icon, style={'width': '48px', 'height': '48px'}),            
            html.H3("Pala Gomez-Creek", style={'color': '#6B46C1'}),
            html.Ul([
                html.Li("Location: San Diego Region, California"),
                html.Li("Size: 10 MW / 60 MWh"),
                html.Li("Application: Resource Adequacy"),
                html.Li("Long-Term Service Agreement: 10 years"),
                html.Li("Designed to high seismic performance qualification level in accordance with IEEE 693-2018")
            ])
        ], width=5, style={'padding': '10px', 'background-color': '#F7FAFC', 'margin': '10px'})

    ], justify='around', align='center'),

    dbc.Row([
        dbc.Col([
            html.Img(src = solar_panel_icon, style={'width': '48px', 'height': '48px'}),            
            html.A(html.H3("Golden Triangle II", style={'color': '#6B46C1'}), href="projects/gt_2"),
            html.Ul([
                html.Li("Location: Lowndes County, Mississippi"),
                html.Li("Size: 50 MW / 200 MWh"),
                html.Li("Application: Solar + Storage"),
                html.Li("Long-Term Service Agreement: 10 years"),
                html.Li("Reducing curtailment of excess renewable generation")
            ])
        ], width=5, style={'padding': '10px', 'background-color': '#F7FAFC', 'margin': '10px'}),

        dbc.Col([
            html.Img(src = solar_panel_icon, style={'width': '48px', 'height': '48px'}),            
            html.H3("Salvador", style={'color': '#6B46C1'}),
            html.Ul([
                html.Li("Location: Atacama Region, Chile"),
                html.Li("Size: 50 MW / 250 MWh"),
                html.Li("Application: Solar + Storage & Grid Firming"),
                html.Li("Supporting Chile's national decarbonization goals to achieve 80% clean electric by 2030 and 100% by 2050")
            ])
        ], width=5, style={'padding': '10px', 'background-color': '#F7FAFC', 'margin': '10px'})
    ], justify='around', align='center'),

    dbc.Row([
        dbc.Col([
            html.Img(src = solar_panel_icon, style={'width': '48px', 'height': '48px'}),            
            html.H3("Golden Triangle I", style={'color': '#6B46C1'}),
            html.Ul([
                html.Li("Location: Lowndes County, Mississippi"),
                html.Li("Size: 50 MW / 200 MWh"),
                html.Li("Application: Solar + Storage"),
                html.Li("Long-Term Service Agreement: 10 years"),
                html.Li("Reducing curtailment of excess renewable generation")
            ])
        ], width=5, style={'padding': '10px', 'background-color': '#F7FAFC', 'margin': '10px'}),

        dbc.Col([
            html.Img(src = solar_panel_icon, style={'width': '48px', 'height': '48px'}),            
            html.H3("San Andres", style={'color': '#6B46C1'}),
            html.Ul([
                html.Li("Location: Atacama Region, Chile"),
                html.Li("Size: 35 MW / 175 MWh"),
                html.Li("Application: Solar + Storage & Grid Firming"),
                html.Li("Supporting Chile's national decarbonization goals to achieve 80% clean electric by 2030 and 100% by 2050")
            ])
        ], width=5, style={'padding': '10px', 'background-color': '#F7FAFC', 'margin': '10px'})
    ], justify='around', align='center'),

    dbc.Row([

        dbc.Col([
            html.Img(src = solar_panel_icon, style={'width': '48px', 'height': '48px'}),            
            html.H3("Happy Valley BESS", style={'color': '#6B46C1'}),
            html.Ul([
                html.Li("Location: Nampa, Idaho"),
                html.Li("Size: 82 MW / 328 MWh"),
                html.Li("Application: Resource Adequacy"),
                html.Li("Supporting Idaho's decarbonization goal of delivering 100% clean energy by 2045.")
            ])
        ], width=5, style={'padding': '10px', 'background-color': '#F7FAFC', 'margin': '10px'})
    ], justify='around', align='center'),

], fluid=True),


