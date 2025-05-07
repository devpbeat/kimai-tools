#!/usr/bin/env python3
# ————————————————————————————————————————————————
# Export Kimai Timesheet Report (CSV & Excel) — Typer CLI Version
# ————————————————————————————————————————————————
#
# This script fetches timesheet entries from a Kimai instance via its API
# for a given user and month/year, then exports the data to both CSV and Excel files.
# The Excel file includes a summary sheet with total hours worked.
#
# ————————————————————————————————————————————————
#
# Now supports auto-loading API_URL and API_TOKEN from a .env file using python-dotenv.
# If both are present in .env, you will NOT be prompted for them.
# If either is missing, you will be prompted as before.
#
# CSV files are saved in the 'csv/' folder, Excel files in the 'excel/' folder.
# Folders are created automatically if they do not exist.
#
# Example .env:
# API_URL   = "https://kimai.ignitesolutions.click/api/timesheets"
# API_TOKEN = "your_token_here"
# ————————————————————————————————————————————————

import requests
import csv
import pandas as pd
import typer
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from calendar import monthrange
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

app = typer.Typer(help="Export Kimai timesheet entries to CSV and Excel.")

# List of months in English and Spanish
MONTHS = [
    ("January",   "Enero"),
    ("February",  "Febrero"),
    ("March",     "Marzo"),
    ("April",     "Abril"),
    ("May",       "Mayo"),
    ("June",      "Junio"),
    ("July",      "Julio"),
    ("August",    "Agosto"),
    ("September", "Septiembre"),
    ("October",   "Octubre"),
    ("November",  "Noviembre"),
    ("December",  "Diciembre"),
]

def get_month_range(year: int, month: int) -> Tuple[str, str]:
    """
    Return the ISO 8601 datetime strings for the beginning and end of a given month/year.
    Example: ("2025-04-01T00:00:00", "2025-04-30T23:59:59")
    """
    begin = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59)
    return begin.isoformat(), end.isoformat()

def fetch_timesheets(
    api_url: str,
    api_token: str,
    user_id: int,
    date_begin: str,
    date_end: str
) -> List[Dict[str, Any]]:
    """
    Fetch timesheet entries from the Kimai API for a given user and date range.
    Returns a list of entry dictionaries.
    Raises an exception if the request fails.
    """
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    params = {
        "user": user_id,
        "begin": date_begin,
        "end": date_end,
        "full": 1
    }
    resp = requests.get(api_url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

def process_entries(entries: List[Dict[str, Any]]) -> Tuple[List[List[str]], float]:
    """
    Process Kimai timesheet entries into rows for export and sum total duration in hours.
    Returns a tuple: (rows, total_hours)
    - rows: List of lists, each representing a row for CSV/Excel
    - total_hours: Total duration in hours (float)
    """
    rows: List[List[str]] = []
    total_seconds: int = 0
    for e in entries:
        begin    = e.get("begin", "")
        end      = e.get("end", "")
        customer = e.get("project", {}).get("customer", {}).get("name", "")
        project  = e.get("project", {}).get("name", "")
        activity = e.get("activity", {}).get("name", "")
        desc     = (e.get("description") or "").replace("\r\n", " ").replace("\n", " ")
        duration = e.get("duration", 0)
        total_seconds += duration
        rows.append([begin, end, customer, project, activity, desc])
    total_hours = total_seconds / 3600
    return rows, total_hours

def write_csv(filename: str, rows: List[List[str]]) -> None:
    """
    Write the provided rows to a CSV file with a header row.
    """
    # Ensure the csv/ directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["begin","end","customer","project","activity","description"])
        writer.writerows(rows)

def write_excel(filename: str, rows: List[List[str]], total_hours: float) -> None:
    """
    Write the provided rows to an Excel file with two sheets:
    - 'Data': All timesheet entries
    - 'Summary': Total hours worked
    """
    # Ensure the excel/ directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df = pd.DataFrame(rows, columns=["begin","end","customer","project","activity","description"])
        df.to_excel(writer, sheet_name="Data", index=False)
        summary_df = pd.DataFrame([{"Total hours": total_hours}])
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

# ——— Typer CLI Command ———
@app.command()
def export(
    user_id: int = typer.Option(..., prompt=True, help="Kimai user ID to export timesheets for."),
    year: int = typer.Option(datetime.now().year, prompt=True, help="Year (e.g. 2025)"),
    month: Optional[int] = typer.Option(
        None,
        help="Month (1-12)",
    ),
    api_url: Optional[str] = typer.Option(
        None, help="Kimai API endpoint (e.g. https://kimai.example.com/api/timesheets)"
    ),
    api_token: Optional[str] = typer.Option(
        None, hide_input=True, help="Kimai API token (get from your Kimai profile)"
    ),
    output_csv: Optional[str] = typer.Option(None, help="Output CSV filename (optional)"),
    output_xlsx: Optional[str] = typer.Option(None, help="Output Excel filename (optional)")
) -> None:
    """
    Export Kimai timesheet entries for a user and month to CSV and Excel.
    Prompts for all required parameters if not provided as options.
    """
    # Print month selection menu if month is not provided
    if month is None:
        typer.echo("Select the month:")
        for idx, (en, es) in enumerate(MONTHS, 1):
            typer.echo(f"  {idx}. {en} / {es}")
        while True:
            try:
                month_input = typer.prompt("Enter the number of the month (1-12)")
                month = int(month_input)
                if 1 <= month <= 12:
                    break
                else:
                    typer.echo("Please enter a number between 1 and 12.")
            except ValueError:
                typer.echo("Invalid input. Please enter a number between 1 and 12.")

    # Load API_URL and API_TOKEN from environment if not provided
    env_api_url = os.getenv("API_URL")
    env_api_token = os.getenv("API_TOKEN")

    # Use .env values if present, otherwise prompt
    if not api_url:
        if env_api_url:
            api_url = env_api_url
        else:
            api_url = typer.prompt("Kimai API endpoint (e.g. https://kimai.example.com/api/timesheets)")
    if not api_token:
        if env_api_token:
            api_token = env_api_token
        else:
            api_token = typer.prompt("Kimai API token (get from your Kimai profile)", hide_input=True)

    # Set output file paths in csv/ and excel/ folders
    csv_dir = "csv"
    excel_dir = "excel"
    if not output_csv:
        output_csv = os.path.join(csv_dir, f"monthly-report-{year}-{int(month):02d}.csv")
    if not output_xlsx:
        output_xlsx = os.path.join(excel_dir, f"monthly-report-{year}-{int(month):02d}.xlsx")

    # Calculate date range for the selected month/year
    date_begin, date_end = get_month_range(year, int(month))

    typer.echo(f"Fetching timesheets for user {user_id}, {year}-{int(month):02d} ({MONTHS[int(month)-1][0]} / {MONTHS[int(month)-1][1]})...")
    entries = fetch_timesheets(api_url, api_token, user_id, date_begin, date_end)
    rows, total_hours = process_entries(entries)

    write_csv(output_csv, rows)
    typer.echo(f"→ CSV saved to {output_csv}")
    typer.echo(f"→ Total time: {total_hours:.2f} hours")

    write_excel(output_xlsx, rows, total_hours)
    typer.echo(f"→ Excel saved to {output_xlsx} (with 'Data' and 'Summary' sheets)")

if __name__ == "__main__":
    app()
