import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

CSV_DIR = os.path.join(os.path.dirname(__file__), '../csv_output')

# Map month abbreviations to full names
MONTHS = {
    'JAN': 'January', 'FEB': 'February', 'MAR': 'March', 'APR': 'April',
    'MAY': 'May', 'JUN': 'June', 'JUL': 'July', 'AUG': 'August',
    'SEP': 'September', 'OCT': 'October', 'NOV': 'November', 'DEC': 'December'
}

def extract_date_from_filename(filename):
    # Example: SUN_SEP_7TH_CAR_Panthers_vs_JAX_Jaguars.csv
    m = re.match(r'\w+_([A-Z]{3})_(\d+)[A-Z]{2}', filename)
    if not m:
        return None
    month_abbr, day = m.groups()
    month = MONTHS.get(month_abbr)
    if not month:
        return None
    # Guess year (use 2024 as default, or infer from context if needed)
    year = 2024
    try:
        date = datetime.strptime(f"{month_abbr} {day} {year}", "%b %d %Y")
    except Exception:
        return None
    return date

def organize_files_by_week():
    files = []
    for root, _, filenames in os.walk(CSV_DIR):
        for f in filenames:
            if f.endswith('.csv'):
                files.append(os.path.relpath(os.path.join(root, f), CSV_DIR))
    # Group by month
    month_files = defaultdict(list)
    for rel_path in files:
        f = os.path.basename(rel_path)
        date = extract_date_from_filename(f)
        if date:
            month_files[date.strftime('%B')].append((date, rel_path))
    result = {}
    for month, date_files in month_files.items():
        date_files.sort()
        # Find all Sundays in the month
        sundays = []
        if not date_files:
            continue
        year = date_files[0][0].year
        month_num = date_files[0][0].month
        d = datetime(year, month_num, 1)
        while d.month == month_num:
            if d.weekday() == 6:
                sundays.append(d)
            d += timedelta(days=1)
        weeks = defaultdict(list)
        for date, rel_path in date_files:
            week_idx = None
            for i, sunday in enumerate(sundays):
                if date <= sunday:
                    week_idx = i + 1
                    break
            if week_idx is None:
                week_idx = len(sundays)
            weeks[f"Week {week_idx}"].append(rel_path)
        result[month] = dict(weeks)
    return result

if __name__ == "__main__":
    import json
    import sys
    week_map = organize_files_by_week()
    if len(sys.argv) > 1 and sys.argv[1] == '--move':
        # Move files into subdirectories by month/week
        with open(os.path.join(CSV_DIR, 'csv_by_week.json')) as f:
            mapping = json.load(f)
        for month, weeks in mapping.items():
            for week, files in weeks.items():
                target_dir = os.path.join(CSV_DIR, month, week)
                os.makedirs(target_dir, exist_ok=True)
                for fname in files:
                    src = os.path.join(CSV_DIR, fname)
                    dst = os.path.join(target_dir, fname)
                    if os.path.exists(src):
                        os.rename(src, dst)
        print('Files have been organized into subdirectories by month and week.')
    else:
        print(json.dumps(week_map, indent=2)) 