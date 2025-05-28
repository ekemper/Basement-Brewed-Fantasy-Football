import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from typing import List, Dict, Optional

# Use the same team list from game_logs_scraper.py for consistency
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

BASE_URL = "https://www.footballguys.com/stats/snap-counts/teams?team={team}&year=2024"

def scrape_team_snapcounts(team_code: str, year: int = 2024) -> List[Dict]:
    """
    Scrape snapcount data for a specific team from Football Guys.
    
    Args:
        team_code (str): Team abbreviation (e.g., 'ARI', 'PHI')
        year (int): Season year, defaults to 2024
        
    Returns:
        List[Dict]: List of player snapcount records
    """
    url = BASE_URL.format(team=team_code)
    print(f"Scraping snapcounts for {team_code}: {url}")
    
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        return parse_snapcount_table(soup, team_code)
        
    except requests.RequestException as e:
        print(f"Error scraping {team_code} snapcounts: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error scraping {team_code} snapcounts: {e}")
        return []

def parse_snapcount_table(soup: BeautifulSoup, team_code: str) -> List[Dict]:
    """
    Parse the snapcount table from the Football Guys page.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content
        team_code (str): Team abbreviation
        
    Returns:
        List[Dict]: List of player snapcount records
    """
    all_rows = []
    
    # Look for the main data container
    data_div = soup.find("div", id="stats_snapcounts_data")
    if not data_div:
        print(f"No snapcount data div found for {team_code}")
        return []
    
    # Find the main table
    table = data_div.find("table")
    if not table:
        print(f"No snapcount table found for {team_code}")
        return []
    
    # Get all thead and tbody elements
    thead_elements = table.find_all("thead")
    tbody_elements = table.find_all("tbody")
    
    if len(thead_elements) != len(tbody_elements):
        print(f"Mismatch between thead and tbody elements for {team_code}: {len(thead_elements)} vs {len(tbody_elements)}")
        return []
    
    print(f"Processing {len(thead_elements)} position sections for {team_code}")
    
    # Process each position section
    for thead, tbody in zip(thead_elements, tbody_elements):
        # Get position from the first header cell (th elements are direct children of thead)
        header_cells = thead.find_all("th")
        if not header_cells:
            continue
            
        # First cell contains the position
        position_text = header_cells[0].text.strip()
        position = get_position_from_header(position_text)
        if not position:
            print(f"Could not determine position from header: {position_text}")
            continue
        
        print(f"Processing {position} ({position_text}) section")
        
        # Remaining cells contain week numbers
        weeks = []
        for i, cell in enumerate(header_cells[1:]):
            week_text = cell.text.strip()
            if week_text.lower() == "total":  # Skip the total column
                continue
            week_match = re.search(r'Wk\s*(\d+)', week_text)
            if week_match:
                weeks.append(int(week_match.group(1)))
        
        print(f"Found weeks: {weeks[:5]}..." if len(weeks) > 5 else f"Found weeks: {weeks}")
        
        # Process player rows in this tbody
        player_count = 0
        for tr in tbody.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if not cells:
                continue
            
            # First cell contains player name
            first_cell = cells[0]
            player_link = first_cell.find("a")
            player_name = player_link.text.strip() if player_link else first_cell.text.strip()
            if not player_name:
                continue
            
            player_count += 1
            
            # Extract snapcount data for each week
            snap_cells = cells[1:]
            
            for i, snap_cell in enumerate(snap_cells):
                if i >= len(weeks):
                    break
                
                week = weeks[i]
                
                # Extract snapcount value from div.text-secondary
                snapcount_div = snap_cell.find("div", class_="text-secondary")
                if snapcount_div:
                    snapcount = parse_snapcount_value(snapcount_div.text.strip())
                else:
                    # Fallback to cell text if no div found
                    snapcount = parse_snapcount_value(snap_cell.text.strip())
                
                # Only add records where snapcount > 0 to avoid empty entries
                if snapcount > 0:
                    # Create record matching target CSV format
                    row = {
                        "Season": 2024,
                        "Week": week,
                        "Player": player_name,
                        "Position": position,
                        "Team": team_code,
                        "Opponent": "",  # We'll need to get opponent info separately
                        "Snapcount": snapcount
                    }
                    
                    all_rows.append(row)
        
        print(f"Processed {player_count} players in {position} section")
    
    print(f"Total records extracted for {team_code}: {len(all_rows)}")
    return all_rows

def get_position_from_header(header_text: str) -> Optional[str]:
    """
    Extract position abbreviation from section header text.
    
    Args:
        header_text (str): Header text from the position section
        
    Returns:
        Optional[str]: Position abbreviation (QB, RB, WR, TE, etc.) or None
    """
    header_lower = header_text.lower()
    
    # Offensive positions
    if "quarterback" in header_lower:
        return "QB"
    elif "running back" in header_lower:
        return "RB"
    elif "wide receiver" in header_lower:
        return "WR"
    elif "tight end" in header_lower:
        return "TE"
    
    # Defensive positions
    elif "defensive tackle" in header_lower:
        return "DT"
    elif "defensive end" in header_lower:
        return "DE"
    elif "linebacker" in header_lower:
        return "LB"
    elif "cornerback" in header_lower:
        return "CB"
    elif "safety" in header_lower:
        return "S"
    
    return None

def parse_snapcount_value(snap_text: str) -> int:
    """
    Parse snapcount value from cell text, handling various formats.
    
    Args:
        snap_text (str): Raw text from snapcount cell
        
    Returns:
        int: Parsed snapcount value, 0 if invalid
    """
    if not snap_text or snap_text.strip() == "":
        return 0
        
    # Remove any HTML tags and extra whitespace
    clean_text = re.sub(r'<.*?>', '', snap_text).strip()
    
    # Extract numeric value
    match = re.search(r'(\d+)', clean_text)
    if match:
        return int(match.group(1))
    
    return 0

def get_all_snapcounts(year: int = 2024) -> List[Dict]:
    """
    Scrape snapcount data for all NFL teams.
    
    Args:
        year (int): Season year, defaults to 2024
        
    Returns:
        List[Dict]: Combined snapcount data for all teams
    """
    all_data = []
    
    for team_code, team_name in teams:
        try:
            team_data = scrape_team_snapcounts(team_code, year)
            all_data.extend(team_data)
            
            # Rate limiting - sleep between requests
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing team {team_code}: {e}")
            continue
    
    return all_data

def save_snapcount_data(data: List[Dict], filename: str = "snapcount_data.csv") -> None:
    """
    Save snapcount data to CSV file.
    
    Args:
        data (List[Dict]): Snapcount data
        filename (str): Output filename
    """
    if not data:
        print("No data to save")
        return
        
    df = pd.DataFrame(data)
    
    # Ensure consistent column order
    columns = ["Season", "Week", "Player", "Position", "Team", "Opponent", "Snapcount"]
    df = df.reindex(columns=columns, fill_value=0)
    
    # Sort by team, week, position, player for consistency
    df = df.sort_values(["Team", "Week", "Position", "Player"])
    
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} snapcount records to {filename}")

if __name__ == "__main__":
    # Test with a single team first
    print("Testing snapcount scraper with Arizona Cardinals...")
    test_data = scrape_team_snapcounts("ARI")
    
    if test_data:
        print(f"Successfully scraped {len(test_data)} records for ARI")
        print("Sample records:")
        for i, record in enumerate(test_data[:5]):
            print(f"  {i+1}: {record}")
    else:
        print("No data retrieved for test team") 