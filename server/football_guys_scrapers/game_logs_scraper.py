import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

teams = [
    ("ARI", "Arizona Cardinals"),
    ("ATL", "Atlanta Falcons"),
    ("BAL", "Baltimore Ravens"),
    ("BUF", "Buffalo Bills"),
    ("CAR", "Carolina Panthers"),
    ("CHI", "Chicago Bears"),
    ("CIN", "Cincinnati Bengals"),
    ("CLE", "Cleveland Browns"),
    ("DAL", "Dallas Cowboys"),
    ("DEN", "Denver Broncos"),
    ("DET", "Detroit Lions"),
    ("GB", "Green Bay Packers"),
    ("HOU", "Houston Texans"),
    ("IND", "Indianapolis Colts"),
    ("JAX", "Jacksonville Jaguars"),
    ("KC", "Kansas City Chiefs"),
    ("LAC", "Los Angeles Chargers"),
    ("LAR", "Los Angeles Rams"),
    ("LV", "Las Vegas Raiders"),
    ("MIA", "Miami Dolphins"),
    ("MIN", "Minnesota Vikings"),
    ("NE", "New England Patriots"),
    ("NO", "New Orleans Saints"),
    ("NYG", "New York Giants"),
    ("NYJ", "New York Jets"),
    ("PHI", "Philadelphia Eagles"),
    ("PIT", "Pittsburgh Steelers"),
    ("SEA", "Seattle Seahawks"),
    ("SF", "San Francisco 49ers"),
    ("TB", "Tampa Bay Buccaneers"),
    ("TEN", "Tennessee Titans"),
    ("WAS", "Washington Commanders"),
]

COLUMNS = [
    "Season", "Week", "Player", "Position", "Team", "Opponent",
    "Pass_Comp", "Pass_Att", "Pass_Yards", "Pass_TD", "Pass_Int",
    "Rush_Att", "Rush_Yards", "Rush_TD",
    "Rec_Targets", "Rec_Recep", "Rec_Yards", "Rec_TD",
    "PPR_Points", "PPR_Average", "Snapcount", "Reg_League_Avg", "Reg_Due_For"
]

BASE_URL = "https://www.footballguys.com/stats/game-logs/teams?team={team}&year=2024"

def parse_stat_block(block, num_fields):
    """Parse a stat block like '145-1-1' or '6-64-1' into a list of ints (or 0s if empty)."""
    if not block or block == "0":
        return [0] * num_fields
    # Remove any HTML tags or whitespace
    block = re.sub(r'<.*?>', '', block).strip()
    parts = re.split(r"[-]", block)
    # Only keep the first num_fields, pad with zeros if not enough
    parts = [p for p in parts if p != '']
    values = []
    for p in parts[:num_fields]:
        try:
            values.append(int(p))
        except Exception:
            values.append(0)
    while len(values) < num_fields:
        values.append(0)
    return values

def get_position_and_patterns(h2_text):
    """Return (position, stat_patterns) for a given table section."""
    if "Quarterback" in h2_text:
        return "QB", [("Pass_Yards", "Pass_TD", "Pass_Int"), ("Rush_Att", "Rush_Yards", "Rush_TD")]
    if "Running Back" in h2_text:
        return "RB", [("Rush_Att", "Rush_Yards", "Rush_TD"), ("Rec_Recep", "Rec_Yards", "Rec_TD")]
    if "Wide Receiver" in h2_text:
        return "WR", [("Rush_Att", "Rush_Yards", "Rush_TD"), ("Rec_Recep", "Rec_Yards", "Rec_TD")]
    if "Tight End" in h2_text:
        return "TE", [("Rec_Recep", "Rec_Yards", "Rec_TD")]
    return None, []

def scrape_team(team_code, team_name):
    url = BASE_URL.format(team=team_code)
    print(f"Scraping {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    div = soup.find("div", id="stats_gamelogs_team_data")
    if not div:
        print(f"No data div found for {team_code}")
        return []

    all_rows = []
    for section in div.find_all("div", class_="row"):
        h2 = section.find("h2")
        if not h2:
            continue
        position, patterns = get_position_and_patterns(h2.text)
        if not position:
            continue

        table = section.find_next("table")
        if not table:
            continue

        # Get week numbers and opponent codes
        thead = table.find("thead")
        week_row = thead.find_all("tr")[0]
        opp_row = thead.find_all("tr")[1]
        weeks = [th.text.replace("Wk ", "") for th in week_row.find_all("th")[1:]]
        opps = [th.text for th in opp_row.find_all("th")[1:]]

        # Get player rows
        for tr in table.find("tbody").find_all("tr"):
            player_cell = tr.find("td")
            player_link = player_cell.find("a")
            player_name = player_link.text.strip() if player_link else player_cell.text.strip()
            tds = tr.find_all("td")[1:]
            for i, td in enumerate(tds):
                week = i + 1
                opp = opps[i] if i < len(opps) else ""
                stat_text = td.decode_contents().replace("<br>", "\n").strip()
                stat_lines = [line.strip() for line in stat_text.split("\n") if line.strip()]
                # Default all stats to 0
                stats = {
                    "Pass_Comp": 0, "Pass_Att": 0, "Pass_Yards": 0, "Pass_TD": 0, "Pass_Int": 0,
                    "Rush_Att": 0, "Rush_Yards": 0, "Rush_TD": 0,
                    "Rec_Targets": 0, "Rec_Recep": 0, "Rec_Yards": 0, "Rec_TD": 0
                }
                if position == "QB":
                    if len(stat_lines) == 2:
                        pass_yards, pass_td, pass_int = parse_stat_block(stat_lines[0], 3)
                        rush_att, rush_yds, rush_td = parse_stat_block(stat_lines[1], 3)
                        stats.update({
                            "Pass_Yards": pass_yards, "Pass_TD": pass_td, "Pass_Int": pass_int,
                            "Rush_Att": rush_att, "Rush_Yards": rush_yds, "Rush_TD": rush_td
                        })
                    elif len(stat_lines) == 1 and stat_lines[0] != "0":
                        pass_yards, pass_td, pass_int = parse_stat_block(stat_lines[0], 3)
                        stats.update({
                            "Pass_Yards": pass_yards, "Pass_TD": pass_td, "Pass_Int": pass_int
                        })
                elif position in ("RB", "WR"):
                    if len(stat_lines) == 2:
                        rush_att, rush_yds, rush_td = parse_stat_block(stat_lines[0], 3)
                        rec_rec, rec_yds, rec_td = parse_stat_block(stat_lines[1], 3)
                        stats.update({
                            "Rush_Att": rush_att, "Rush_Yards": rush_yds, "Rush_TD": rush_td,
                            "Rec_Recep": rec_rec, "Rec_Yards": rec_yds, "Rec_TD": rec_td
                        })
                    elif len(stat_lines) == 1 and stat_lines[0] != "0":
                        rush_att, rush_yds, rush_td = parse_stat_block(stat_lines[0], 3)
                        stats.update({
                            "Rush_Att": rush_att, "Rush_Yards": rush_yds, "Rush_TD": rush_td
                        })
                elif position == "TE":
                    if len(stat_lines) == 1 and stat_lines[0] != "0":
                        rec_rec, rec_yds, rec_td = parse_stat_block(stat_lines[0], 3)
                        stats.update({
                            "Rec_Recep": rec_rec, "Rec_Yards": rec_yds, "Rec_TD": rec_td
                        })
                # Compose row
                row = {
                    "Season": 2024,
                    "Week": week,
                    "Player": player_name,
                    "Position": position,
                    "Team": team_code,
                    "Opponent": opp,
                    "Pass_Comp": stats["Pass_Comp"],
                    "Pass_Att": stats["Pass_Att"],
                    "Pass_Yards": stats["Pass_Yards"],
                    "Pass_TD": stats["Pass_TD"],
                    "Pass_Int": stats["Pass_Int"],
                    "Rush_Att": stats["Rush_Att"],
                    "Rush_Yards": stats["Rush_Yards"],
                    "Rush_TD": stats["Rush_TD"],
                    "Rec_Targets": 0,
                    "Rec_Recep": stats["Rec_Recep"],
                    "Rec_Yards": stats["Rec_Yards"],
                    "Rec_TD": stats["Rec_TD"],
                    "PPR_Points": "",
                    "PPR_Average": "",
                    "Snapcount": "",
                    "Reg_League_Avg": "",
                    "Reg_Due_For": ""
                }
                all_rows.append(row)
    return all_rows

all_data = []
for team_code, team_name in teams:
    try:
        all_data.extend(scrape_team(team_code, team_name))
        time.sleep(1)
    except Exception as e:
        print(f"Error scraping {team_code}: {e}")

df = pd.DataFrame(all_data, columns=COLUMNS)

df.to_csv("../football_guys_scrapers/data/fbg_game_logs.csv", index=False)
df.to_json("../football_guys_scrapers/data/fbg_game_logs.json", orient="records", indent=2)

print("Saved game_logs.csv and game_logs.json")