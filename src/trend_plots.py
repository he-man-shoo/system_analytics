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

    df = df.loc[df['cycle marker'] == 'Standby']


    avg_resting_soc = df["avail soc %"].mean()

    avg_resting_soc_list = [avg_resting_soc] * len(df)

    contract_resting_soc = 50
        
    contract_resting_soc_list = [contract_resting_soc] * len(df)

    if (avg_resting_soc - contract_resting_soc) < 0:
        resting_soc_string = f"{abs(avg_resting_soc - contract_resting_soc):.2f}% lower than contractual resting SOC limit"
    else:
        resting_soc_string = f"{abs(avg_resting_soc - contract_resting_soc):.2f}% higher than contractual resting SOC"

    fig = go.Figure()
    fig.add_trace(go.Scatter(y = df["avail soc %"], x = df['_time'],
                            mode = 'lines', name = 'Resting SOC', line=dict(color=prevalon_purple)))
    fig.add_trace(go.Scatter(y = avg_resting_soc_list, x = df['_time'],
                            mode = 'lines', name = 'Average resting SOC', line=dict(color=prevalon_yellow)))
    fig.add_trace(go.Scatter(y = contract_resting_soc_list, x = df['_time'],
                            mode = 'lines', name = 'Contractual resting SOC', line=dict(color='rgb(255, 0, 0)')))


    fig.update_layout(
        title=f"Resting State of Charge Trend - Average: {avg_resting_soc:.2f}%, {resting_soc_string}",
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

    # Average and Site Down Time
    average_availability = df["availability %"].mean()

    if (average_availability - 97) < 0:
        availability_string = f"{abs(average_availability - 97):.2f}% lower than contractual availability limit" 
    else:
        availability_string = f"{abs(average_availability - 97):.2f}% higher than contractual availability"

    fig = go.Figure()
    fig.add_trace(go.Scatter(y = df['availability %'], x = df['_time'], \
                            mode = 'lines', name = 'Availability %', line=dict(color=prevalon_purple)))

    fig.add_trace(go.Scatter(y = avail_percentage, x = df['_time'], \
                            mode = 'lines', name = 'Average availability', line=dict(color=prevalon_yellow)))
    
    fig.add_trace(go.Scatter(y = contract_avail_percentage, x = df['_time'], \
                            mode = 'lines', name = 'Contractual availability',  line=dict(color='rgb(255, 0, 0)')))

    fig.update_layout(
            title=f"Availability Trend - Average: {average_availability:.2f}%, {availability_string}",
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

def generate_rte_plot(start_time, end_time):

    
    start_time =  pd.to_datetime(start_time).tz_localize(None).strftime("%Y-%m-%d %H:%M:%S")
    end_time = pd.to_datetime(end_time).tz_localize(None).strftime("%Y-%m-%d %H:%M:%S")

    rte_trend_data = pd.read_excel('RTE_filtered.xlsx')

    rte_trend_data['Start Time'] = pd.to_datetime(rte_trend_data['Start Time'])
    rte_trend_data['End Time'] = pd.to_datetime(rte_trend_data['End Time'])

    rte_trend_data.loc[rte_trend_data['year_month'] == "2024-08", 'tested_rte'] = 0.88
    rte_trend_data.loc[rte_trend_data['year_month'] == "2025-05", 'tested_rte'] = 0.873
    
    rte_trend_data['tested_rte'] = (
        rte_trend_data['tested_rte'].interpolate(method='linear')
    )
    
    rte_trend_data['contracted_rte'] = [0.832] * len(rte_trend_data)

    rte_trend_data = rte_trend_data[
        (rte_trend_data['Start Time'] >= start_time) &
        (rte_trend_data['End Time']   <= end_time)
    ]
    
    # Getting Median RTE for each month
    rte_trend_data['median_RTE_by_month'] = rte_trend_data.groupby('year_month')['RTE'] \
                                .transform('median')

    # Getting Median Tested RTE for each month
    rte_trend_data['tested_rte'] = rte_trend_data.groupby('year_month')['tested_rte'] \
                                .transform('median')
    fig = go.Figure()

    # Add scatter for median_rte
    fig.add_trace(go.Scatter(
        x=rte_trend_data['year_month'],
        y=rte_trend_data['median_RTE_by_month'],
        mode='lines + markers',
        name='Calculated RTE',
        marker=dict(color=prevalon_purple, symbol='circle'),
        line=dict(color=prevalon_purple), 
        connectgaps=True  # <-- This connects points even with None/NaN values

    ))

    # Add scatter for tested_rte
    fig.add_trace(go.Scatter(
        x=rte_trend_data['year_month'],
        y=rte_trend_data['tested_rte'],
        mode='lines',
        name='Tested RTE',
        line=dict(color=prevalon_yellow, dash='dash'), 
        connectgaps=True  # <-- This connects points even with None/NaN values
    ))

    # Add scatter for contracted_rte
    fig.add_trace(go.Scatter(
        x=rte_trend_data['year_month'],
        y=rte_trend_data['contracted_rte'],
        mode='lines',
        name='Contracted RTE',
        line=dict(color='red'), 
        connectgaps=True  # <-- This connects points even with None/NaN values
    ))

    # Show Y axis as percentage and display legend
    fig.update_layout(
        plot_bgcolor='rgb(255, 255, 255)',
        paper_bgcolor='rgb(255, 255, 255)',
        title='Monthly RTE Trend',
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

    return fig

def generate_throughput_plot(df, proj_energy, num_cyc):

    df['_time'] = pd.to_datetime(df['_time'])
    number_of_days = math.ceil((df['_time'].max() - df['_time'].min())/pd.Timedelta(days=1))
    
    expected_throughput = (num_cyc * proj_energy) * (number_of_days / 365)

    df['MWh discharged @ timestamp'] = df['kwh discharged @ timestamp'] / 1000  # Convert kWh to MWh

    total_throughput = sum(df['MWh discharged @ timestamp'])  # Calculate total throughput

    
    if total_throughput - expected_throughput > 0:
        expected_throughput_str = f"{abs(total_throughput - expected_throughput)*100/expected_throughput:.2f}% higher than expected"
    else:
        expected_throughput_str = f"{abs(total_throughput - expected_throughput)*100/expected_throughput:.2f}% lower than expected"

    equivalent_cycles = total_throughput / proj_energy  # Calculate equivalent cycles

    equivalent_cycles_str = f"{equivalent_cycles:.2f} equivalent cycles"
    # Create the bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['_time'],
        y=df['MWh discharged @ timestamp'],
        name='Throughput (MWh)',
        marker=dict(color=prevalon_purple)  # Using a yellow color similar to prevalon_yellow
    ))

    # Update layout to match the original
    fig.update_layout(
        title=f"Throughput Trend - Total Throughput: {total_throughput:,.2f} MWh; {equivalent_cycles_str} ; {expected_throughput_str}" ,
        plot_bgcolor='rgb(255, 255, 255)',  # White background
        paper_bgcolor='rgb(255, 255, 255)',  # White paper background
        xaxis=dict(
            showgrid=True,  # Show gridlines
            gridcolor='rgb(200, 200, 200)',  # Gridline color
            gridwidth=1,  # Gridline width
            zeroline=False,  # Remove zero line
        ),
        yaxis=dict(
            title_text="Throughput (MWh)",
            title_font=dict(size=14),
            title_standoff=10,
            showgrid=True,
            gridcolor='rgb(200, 200, 200)',
            gridwidth=1
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

