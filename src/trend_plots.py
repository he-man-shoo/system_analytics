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

def add_period_overlay(fig, df, marker, color, name):
    if 'cycle marker' not in df.columns:
        return
    mask = df['cycle marker'] == marker
    periods = []
    start = None
    for i, is_period in enumerate(mask):
        if is_period and start is None:
            start = df['_time'].iloc[i]
        elif not is_period and start is not None:
            end = df['_time'].iloc[i]
            periods.append((start, end))
            start = None
    if start is not None:
        periods.append((start, df['_time'].iloc[-1]))
    for start, end in periods:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor=color,
            layer="below", line_width=0,
        )
    # Add dummy trace for legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='lines',
        line=dict(width=10, color=color),
        name=name
    ))

def generate_soc_plot(df):
    resting_soc = [df["avail soc %"].mean()] * len(df)
    contract_resting_soc = [50] * len(df)

    fig = go.Figure()
    fig.add_trace(go.Scatter(y = df["avail soc %"], x = df['_time'],
                            mode = 'lines', name = 'State of Charge', line=dict(color=prevalon_purple)))
    fig.add_trace(go.Scatter(y = resting_soc, x = df['_time'],
                            mode = 'lines', name = 'Average Resting SOC', line=dict(color=prevalon_cream)))
    fig.add_trace(go.Scatter(y = contract_resting_soc, x = df['_time'],
                            mode = 'lines', name = 'Contractual resting SOC', line=dict(color='rgb(255, 0, 0)')))

    add_period_overlay(fig, df, "Charging", "rgba(166,153,193,0.4)", "Charging Period")
    add_period_overlay(fig, df, "Discharging", "rgba(252,215,87,0.4)", "Discharging Period")
    add_period_overlay(fig, df, "Standby", "rgba(208,211,212,0.5)", "Standby Period")

    fig.update_layout(
        title="State of Charge Trend",
        plot_bgcolor='rgb(255, 255, 255)',
        paper_bgcolor='rgb(255, 255, 255)',
        xaxis=dict(showgrid=True, gridcolor='rgb(200, 200, 200)', gridwidth=1, zeroline=False),
        yaxis=dict(title_text = "State of Charge (%)", title_font=dict(size=14), title_standoff=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def generate_avail_plot(df):

    avail_percentage = [df["availability %"].mean()] * len(df)

    contract_avail_percentage = [97] * len(df)

    # Site Down Time
    downtime = round((df[df["availability %"] < contract_avail_percentage]['_time'].count())/len(df), 2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(y = df['availability %'], x = df['_time'], \
                            mode = 'lines', name = 'Availability %', line=dict(color=prevalon_yellow)))

    fig.add_trace(go.Scatter(y = avail_percentage, x = df['_time'], \
                            mode = 'lines', name = 'Average availability', line=dict(color=prevalon_lavender)))
    
    fig.add_trace(go.Scatter(y = contract_avail_percentage, x = df['_time'], \
                            mode = 'lines', name = 'Contractual availability',  line=dict(color='rgb(255, 0, 0)')))

    fig.update_layout(
            title=f"Availability Trend (Downtime: {downtime*100:.2f}%)",
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

    df['_time'] = pd.to_datetime(df['_time'])

    # Aux Energy values are always in kWh. Thus, we need to resample the data to 1 hour intervals
    # and aggregate the values accordingly.
    df_dwnsample = df.set_index('_time')

    # For numeric columns, use mean; for categorical, use first or last
    downsampled = df_dwnsample.resample('1h').agg({
        'p_aux (w)': 'mean',  # or 'last'
        # add other columns as needed
    })
    # Backfill NA values
    downsampled = downsampled.bfill()
    downsampled = downsampled.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(y = downsampled['p_aux (w)']*0.001, x = downsampled['_time'], \
                            name = 'Aux Energy (kWh)', marker_color=prevalon_yellow))

    fig.add_trace(go.Scatter(y = df['Temp (°C)'], x = df['_time'], \
                            mode = 'lines', name = 'Ambient Temperature', line=dict(color=prevalon_lavender), yaxis='y2'))
    
    # fig.add_trace(go.Scatter(y = df['SHGF (W/m²)']*0.001, x = df['_time'], \
    #                         mode = 'lines', name = 'SHGF',  line=dict(color=prevalon_slate), yaxis='y2'))
    
    add_period_overlay(fig, df, "Charging", "rgba(166,153,193,0.4)", "Charging Period")
    add_period_overlay(fig, df, "Discharging", "rgba(252,215,87,0.4)", "Discharging Period")
    add_period_overlay(fig, df, "Standby", "rgba(208,211,212,0.5)", "Standby Period")


    fig.update_layout(
            title="Auxiliary Power and Ambient Temperature Trend",
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
