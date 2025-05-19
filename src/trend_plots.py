import pandas as pd
from datetime import datetime, timedelta, UTC
import plotly.graph_objects as go
import math




# Colors
prevalon_purple = 'rgb(72,49,120)'
prevalon_lavender = 'rgb(166,153,193)'
prevalon_yellow = 'rgb(252,215,87)'
prevalon_cream = 'rgb(245,225,164)'
prevalon_slate = 'rgb(208,211,212)'
prevalon_gray = 'rgb(99,102,106)'

def generate_soc_plot(df):
    resting_soc = [df["avail soc %"].mean()] * len(df)
    contract_resting_soc = [50] * len(df)

    fig = go.Figure()
    fig.add_trace(go.Scatter(y = df["avail soc %"], x = df['_time'], \
                            mode = 'lines', name = 'State of Charge', line=dict(color=prevalon_purple)))

    fig.add_trace(go.Scatter(y = resting_soc, x = df['_time'], \
                            mode = 'lines', name = 'Average Resting SOC', line=dict(color=prevalon_cream)))

    fig.add_trace(go.Scatter(y = contract_resting_soc, x = df['_time'], \
                            mode = 'lines', name = 'Contractual resting SOC', line=dict(color='rgb(255, 0, 0)')))

    # Highlight "Standby" periods
    if 'cycle_marker' in df.columns:
        standby_mask = df['cycle_marker'] == "Standby"
        standby_periods = []
        start = None
        for i, is_standby in enumerate(standby_mask):
            if is_standby and start is None:
                start = df['_time'].iloc[i]
            elif not is_standby and start is not None:
                end = df['_time'].iloc[i-1]
                standby_periods.append((start, end))
                start = None
        if start is not None:
            standby_periods.append((start, df['_time'].iloc[-1]))
        for start, end in standby_periods:
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor="rgba(208,211,212,0.3)",  # prevalon_slate with transparency
                layer="below", line_width=0,
                annotation_text="Standby", annotation_position="top left"
            )

    fig.update_layout(
            plot_bgcolor='rgb(255, 255, 255)', # Light grey background 
            paper_bgcolor='rgb(255, 255, 255)', # Very light grey paper background
            
            xaxis=dict(showgrid=True, # Show gridlines 
                       gridcolor='rgb(200, 200, 200)', # Gridline color 
                       gridwidth=1, # Gridline width
                       zeroline=False, # Remove zero line
                       ),
            yaxis=dict(title_text = "State of Charge (%)",
                       title_font=dict(size=14),
                       title_standoff=10,
                       ),
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="bottom",  # Anchor to the bottom
                y=-0.2,  # Position below the plot
                xanchor="center",  # Center the legend
                x=0.5  # Center horizontally
            )
    )
    return fig

def generate_avail_plot(df):

    avail_percentage = [df["availability %"].mean()] * len(df)

    contract_avail_percentage = [97] * len(df)

    # Site Down Time
    downtime = round((df[df["availability %"] < 100]['_time'].count())/len(df), 2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(y = df['availability %'], x = df['_time'], \
                            mode = 'lines', name = 'Availability %', line=dict(color=prevalon_yellow)))

    fig.add_trace(go.Scatter(y = avail_percentage, x = df['_time'], \
                            mode = 'lines', name = 'Average availability', line=dict(color=prevalon_lavender)))
    
    fig.add_trace(go.Scatter(y = contract_avail_percentage, x = df['_time'], \
                            mode = 'lines', name = 'Contractual availability',  line=dict(color='rgb(255, 0, 0)')))

    fig.update_layout(
            plot_bgcolor='rgb(255, 255, 255)', # Light grey background 
            paper_bgcolor='rgb(255, 255, 255)', # Very light grey paper background
            
            xaxis=dict(showgrid=True, # Show gridlines 
                       gridcolor='rgb(200, 200, 200)', # Gridline color 
                       gridwidth=1, # Gridline width
                       zeroline=False, # Remove zero line
                       ),
            yaxis=dict(title_text = "availability (%)",
                       title_font=dict(size=14),
                       title_standoff=10,
                       ),
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="bottom",  # Anchor to the bottom
                y=-0.2,  # Position below the plot
                xanchor="center",  # Center the legend
                x=0.5  # Center horizontally
            )                      
    )

    return fig

def temp_aux_plot(df):

    fig = go.Figure()
    fig.add_trace(go.Bar(y = df['p_aux (w)']*0.001, x = df['_time'], \
                            name = 'P_Aux', marker_color=prevalon_yellow))

    fig.add_trace(go.Scatter(y = df['Temp (°C)'], x = df['_time'], \
                            mode = 'lines', name = 'Ambient Temperature', line=dict(color=prevalon_lavender), yaxis='y2'))
    
    # fig.add_trace(go.Scatter(y = df['SHGF (W/m²)']*0.001, x = df['_time'], \
    #                         mode = 'lines', name = 'SHGF',  line=dict(color=prevalon_slate), yaxis='y2'))

    fig.update_layout(
            plot_bgcolor='rgb(255, 255, 255)', # Light grey background 
            paper_bgcolor='rgb(255, 255, 255)', # Very light grey paper background
            
            xaxis=dict(showgrid=True, # Show gridlines 
                       gridcolor='rgb(200, 200, 200)', # Gridline color 
                       gridwidth=1, # Gridline width
                       zeroline=False, # Remove zero line
                       ),
            yaxis=dict(title_text = "P_Aux (kW)",
                       title_font=dict(size=14),
                       title_standoff=10,
                       ),
            yaxis2=dict(
                title="Temperature (°C)",
                overlaying='y',
                side='right'
            ),
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="bottom",  # Anchor to the bottom
                y=-0.2,  # Position below the plot
                xanchor="center",  # Center the legend
                x=0.5  # Center horizontally
            )                      
    )

    return fig
