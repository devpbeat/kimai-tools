import preswald as pw
import pandas as pd
import glob
import os

# --- Load and combine all CSVs from the ../csv/ folder ---
csv_folder = os.path.join(os.path.dirname(__file__), '..', 'csv')
csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))

if not csv_files:
    pw.text('No CSV files found in ../csv/. Please export some reports first.')
    pw.stop()

# Concatenate all CSVs into a single DataFrame
df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

# Parse datetime columns and calculate duration (in hours) if not present
df['begin'] = pd.to_datetime(df['begin'])
df['end'] = pd.to_datetime(df['end'])
if 'duration' not in df.columns:
    df['duration'] = (df['end'] - df['begin']).dt.total_seconds() / 3600

# --- UI: Date range filter ---
min_date = df['begin'].min().date()
max_date = df['end'].max().date()
date_range = pw.date_range_input('Select date range', min_value=min_date, max_value=max_date, value=(min_date, max_date))
filtered = df[(df['begin'].dt.date >= date_range[0]) & (df['end'].dt.date <= date_range[1])]

# --- UI: Project filter ---
projects = ['All'] + sorted(filtered['project'].dropna().unique().tolist())
project = pw.selectbox('Project', options=projects)
if project != 'All':
    filtered = filtered[filtered['project'] == project]

# --- Show summary ---
pw.text(f"Total hours: {filtered['duration'].sum():.2f}")
pw.table(filtered[['begin', 'end', 'customer', 'project', 'activity', 'description', 'duration']])

# --- Plot: Hours per day ---
hours_per_day = filtered.groupby(filtered['begin'].dt.date)['duration'].sum()
pw.line_chart(hours_per_day, title='Hours per Day')

# --- Plot: Hours by activity ---
hours_by_activity = filtered.groupby('activity')['duration'].sum()
pw.bar_chart(hours_by_activity, title='Hours by Activity') 