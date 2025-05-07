from preswald import text, plotly, table
import pandas as pd
import plotly.express as px
import glob
import os

text("# Kimai Dashboard")
text("This dashboard loads all your Kimai CSV exports from ../csv/ and shows a summary, table, and chart.")

# --- Load and combine all CSVs from the ../csv/ folder ---
csv_folder = os.path.abspath(os.path.join(os.getcwd(), '..', 'csv'))
csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))

if not csv_files:
    text('No CSV files found in ../csv/. Please export some reports first.')
else:
    # Concatenate all CSVs into a single DataFrame
    df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

    # Parse datetime columns and calculate duration (in hours) if not present
    df['begin'] = pd.to_datetime(df['begin'])
    df['end'] = pd.to_datetime(df['end'])
    if 'duration' not in df.columns:
        df['duration'] = (df['end'] - df['begin']).dt.total_seconds() / 3600

    # Show summary
    total_hours = df['duration'].sum()
    text(f"**Total hours:** {total_hours:.2f}")

    # Convert datetime columns to string for display in the table
    display_df = df.copy()
    display_df['begin'] = display_df['begin'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['end'] = display_df['end'].dt.strftime('%Y-%m-%d %H:%M')
    table(display_df[['begin', 'end', 'customer', 'project', 'activity', 'description', 'duration']])

    # Plot: Hours per day
    hours_per_day = df.groupby(df['begin'].dt.date)['duration'].sum().reset_index()
    fig = px.line(hours_per_day, x='begin', y='duration', markers=True,
                  title='Hours per Day', labels={'begin': 'Date', 'duration': 'Total Hours'})
    plotly(fig)

    # --- Plot: Activity % per month ---
    # Add year-month column
    df['year_month'] = df['begin'].dt.to_period('M').astype(str)
    months = df['year_month'].unique()
    for ym in months:
        month_df = df[df['year_month'] == ym]
        activity_summary = month_df.groupby('activity')['duration'].sum().reset_index()
        total = activity_summary['duration'].sum()
        activity_summary['percent'] = 100 * activity_summary['duration'] / total if total > 0 else 0
        pie = px.pie(activity_summary, names='activity', values='percent',
                     title=f'Activity % Breakdown for {ym}',
                     labels={'percent': '% of Hours', 'activity': 'Activity'},
                     hole=0.4)
        plotly(pie)
