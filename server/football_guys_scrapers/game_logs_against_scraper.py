import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Hardcoded list of (value, text) tuples for NFL teams
teams = [
    ("ARI", "Arizona Cardinals"),
    ("ATL", "Atlanta Falcons"),
    ("BAL", "Baltimore Ravens"),
    ("BUF", "Buffalo Bills"),
    # ("CAR", "Carolina Panthers"),
    # ("CHI", "Chicago Bears"),
    # ("CIN", "Cincinnati Bengals"),
    # ("CLE", "Cleveland Browns"),
    # ("DAL", "Dallas Cowboys"),
    # ("DEN", "Denver Broncos"),
    # ("DET", "Detroit Lions"),
    # ("GB", "Green Bay Packers"),
    # ("HOU", "Houston Texans"),
    # ("IND", "Indianapolis Colts"),
    # ("JAX", "Jacksonville Jaguars"),
    # ("KC", "Kansas City Chiefs"),
    # ("LAC", "Los Angeles Chargers"),
    # ("LAR", "Los Angeles Rams"),
    # ("LV", "Las Vegas Raiders"),
    # ("MIA", "Miami Dolphins"),
    # ("MIN", "Minnesota Vikings"),
    # ("NE", "New England Patriots"),
    # ("NO", "New Orleans Saints"),
    # ("NYG", "New York Giants"),
    # ("NYJ", "New York Jets"),
    # ("PHI", "Philadelphia Eagles"),
    # ("PIT", "Pittsburgh Steelers"),
    # ("SEA", "Seattle Seahawks"),
    # ("SF", "San Francisco 49ers"),
    # ("TB", "Tampa Bay Buccaneers"),
    # ("TEN", "Tennessee Titans"),
    # ("WAS", "Washington Commanders"),
]

BASE_URL = "https://www.footballguys.com/stats/game-logs-against/teams?team={team}&year=2024"

def get_team_tables(team_code):
    url = BASE_URL.format(team=team_code)
    print(f"Scraping {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    div = soup.find("div", id="stats_game_logs_against_data")
    if not div:
        print(f"No data div found for {team_code}")
        return {}

    tables = {}
    # Find all h2s and the table that follows each
    for h2 in div.find_all("h2"):
        table_title = h2.get_text(strip=True)
        table = h2.find_next("table")
        if not table:
            continue
        # Parse table headers
        headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
        # Parse table rows
        rows = []
        for tr in table.find("tbody").find_all("tr"):
            row = []
            for td in tr.find_all("td"):
                # If the cell contains a link, get the text
                a = td.find("a")
                if a:
                    row.append(a.get_text(strip=True))
                else:
                    row.append(td.get_text(strip=True))
            rows.append(row)
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        tables[table_title] = df
    return tables

# Main scraping loop
all_data = {}
for team_code, team_name in teams:
    try:
        team_tables = get_team_tables(team_code)
        all_data[team_code] = team_tables
        time.sleep(1)  # Be polite to the server
    except Exception as e:
        print(f"Error scraping {team_code}: {e}")

# Example: Accessing the Quarterbacks table for ARI
# df = all_data["ARI"]["Quarterbacks vs. ARI"]
# print(df.head())

# Optionally, save to CSVs
for team_code, tables in all_data.items():
    for table_name, df in tables.items():
        safe_table_name = table_name.replace(" ", "_").replace(".", "")
        df.to_csv(f"../football_guys_scrapers/data/game_logs_against/{team_code}_{safe_table_name}.csv", index=False)