# kimai-tools

## Export Kimai Timesheet Report (Typer CLI)

This repository contains a modern CLI tool (using [Typer](https://github.com/fastapi/typer)) to export timesheet entries from a Kimai instance via its API. The tool fetches all time entries for a specified user and month, then exports the data to both CSV and Excel files. The Excel file includes a summary sheet with the total hours worked.

---

## Features
- Interactive CLI: prompts for API URL, API token, user ID, year, and month (unless set in `.env`)
- Auto-loads API URL and token from `.env` if present (using [python-dotenv](https://pypi.org/project/python-dotenv/))
- Month selection (1–12) with auto-calculated date range
- Output filenames are auto-named by year/month (customizable)
- Exports data to CSV and Excel (XLSX)
- Excel file includes a summary sheet with total hours
- DRY, modular codebase

---

## Requirements
- Python 3.7+
- [requests](https://pypi.org/project/requests/)
- [pandas](https://pypi.org/project/pandas/)
- [openpyxl](https://pypi.org/project/openpyxl/) (for Excel export)
- [typer](https://typer.tiangolo.com/) (for CLI)
- [python-dotenv](https://pypi.org/project/python-dotenv/) (for .env support)

Install dependencies with:

```bash
pip install requests pandas openpyxl typer python-dotenv
```

---

## .env File (Optional)

You can create a `.env` file in the same directory as the script to store your Kimai API URL and token:

```
API_URL="https://kimai.ignitesolutions.click/api/timesheets"
API_TOKEN="your_token_here"
```

If both variables are set in `.env`, the CLI will use them automatically and will NOT prompt you for them. If either is missing, you will be prompted as before.

---

## Usage

Run the CLI:

```bash
python export_kimai_report.py export
```

You will be interactively prompted for:
- Kimai user ID
- Year (e.g. 2025)
- Month (1–12, with a menu in English/Spanish)
- Kimai API endpoint and token (only if not set in `.env`)
- (Optional) Output CSV and Excel filenames (auto-named if left blank)

Example session:
```
$ python export_kimai_report.py export
Kimai user ID to export timesheets for: 1
Year (e.g. 2025): 2025
Select the month:
  1. January / Enero
  2. February / Febrero
  ...
 12. December / Diciembre
Enter the number of the month (1-12): 4
Fetching timesheets for user 1, 2025-04 (April / Abril)...
→ CSV saved to monthly-report-2025-04.csv
→ Total time: 123.45 hours
→ Excel saved to monthly-report-2025-04.xlsx (with 'Data' and 'Summary' sheets)
```

---

## Configuration
- All configuration is prompted interactively at runtime unless set in `.env`.
- Output filenames are auto-generated as `monthly-report-YYYY-MM.csv` and `.xlsx` unless you specify custom names.

---

## Notes
- Your API token is sensitive—do not share it or commit it to public repositories.
- You can adjust the user ID, year, and month to export different reports.
- The script is easily customizable for other fields or formats.

---

## License
MIT

---

## Powered by [Typer](https://github.com/fastapi/typer) ([MIT License](https://github.com/fastapi/typer/blob/master/LICENSE))