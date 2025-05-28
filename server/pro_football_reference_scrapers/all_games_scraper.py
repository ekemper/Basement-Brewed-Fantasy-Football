import requests
import time
import random
from bs4 import BeautifulSoup, Comment
from typing import List, Dict, Optional
import re

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

BASE_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
}

def safe_get(url, max_retries=8, delay=10):
    session = requests.Session()
    for attempt in range(max_retries):
        try:
            headers = dict(BASE_HEADERS)
            headers["User-Agent"] = random.choice(USER_AGENTS)
            response = session.get(url, headers=headers)
            if response.status_code == 429:
                print(f"429 Too Many Requests for {url}, sleeping {delay * (attempt + 1)}s...")
                time.sleep(delay * (attempt + 1))
                continue
            response.raise_for_status()
            time.sleep(delay)  # Always sleep after a request
            return response
        except requests.RequestException as e:
            print(f"Request error: {e}")
            time.sleep(delay * (attempt + 1))
    return None

def get_week_links(url: str = "https://www.pro-football-reference.com/years/2024/") -> List[Dict[str, Optional[str]]]:
    try:
        response = safe_get(url)
        if response is None:
            return []
    except Exception as e:
        print(f"Error fetching page: {e}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    section = soup.find('div', id='div_week_games')
    if not section:
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            section = comment_soup.find('div', id='div_week_games')
            if section:
                break
    if not section:
        print("No div_week_games section found.")
        return []
    filter_div = section.find('div', class_='filter')
    if not filter_div:
        print("No filter div found inside div_week_games.")
        return []
    week_links = []
    for div in filter_div.find_all('div', recursive=False):
        a = div.find('a')
        if a:
            text = a.get_text(strip=True)
            link = a.get('href')
            match = re.match(r"Week (\d+)", text)
            week = int(match.group(1)) if match else None
            week_links.append({
                'week': week,
                'text': text,
                'link': link
            })
    return week_links

def get_game_summaries_for_week(week_url: str, base_url: str = "https://www.pro-football-reference.com") -> List[Dict[str, Optional[str]]]:
    response = safe_get(base_url + week_url)
    if response is None:
        print(f"Error fetching week page {week_url}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    game_summaries = soup.find('div', class_='game_summaries')
    if not game_summaries:
        print(f"No game_summaries found for {week_url}")
        return []
    games = []
    for game_div in game_summaries.find_all('div', class_='game_summary'):
        date_tr = game_div.find('tr', class_='date')
        date = date_tr.td.get_text(strip=True) if date_tr and date_tr.td else None
        teams_table = game_div.find('table', class_='teams')
        team_rows = teams_table.find_all('tr') if teams_table else []
        teams = []
        for row in team_rows:
            if 'winner' in row.get('class', []) or 'loser' in row.get('class', []):
                tds = row.find_all('td')
                if len(tds) >= 2:
                    team_name = tds[0].get_text(strip=True)
                    score = tds[1].get_text(strip=True)
                    teams.append({'team': team_name, 'score': score})
        gamelink_td = game_div.find('td', class_='gamelink')
        game_link = None
        if gamelink_td:
            a = gamelink_td.find('a')
            if a and 'Final' in a.get_text():
                game_link = a.get('href')
        if game_link and len(teams) == 2:
            games.append({
                'date': date,
                'team1': teams[0]['team'],
                'score1': teams[0]['score'],
                'team2': teams[1]['team'],
                'score2': teams[1]['score'],
                'game_link': game_link
            })
    return games

def extract_player_offense_table(game_url: str, base_url: str = "https://www.pro-football-reference.com") -> Optional[list]:
    response = safe_get(base_url + game_url)
    if response is None:
        print(f"Error fetching game page {game_url}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    table_wrapper = soup.find('div', id='all_player_offense')
    if not table_wrapper:
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            table_wrapper = comment_soup.find('div', id='all_player_offense')
            if table_wrapper:
                break
    if not table_wrapper:
        print(f"No player offense table found for {game_url}")
        return None
    table = table_wrapper.find('table', id='player_offense')
    if not table:
        print(f"No player_offense table found for {game_url}")
        return None
    headers = []
    thead = table.find('thead')
    if thead:
        header_row = thead.find_all('tr')[-1]
        for th in header_row.find_all(['th', 'td']):
            stat = th.get('data-stat')
            headers.append(stat)
    player_stats = []
    tbody = table.find('tbody')
    for row in tbody.find_all('tr', attrs={'data-row': True}):
        stat_dict = {}
        for i, cell in enumerate(row.find_all(['th', 'td'])):
            stat_name = headers[i] if i < len(headers) else None
            if stat_name:
                stat_dict[stat_name] = cell.get_text(strip=True)
        player_stats.append(stat_dict)
    return player_stats

def get_all_game_summaries(weeks: List[Dict[str, Optional[str]]], base_url: str = "https://www.pro-football-reference.com") -> List[Dict[str, Optional[str]]]:
    all_games = []
    for week in weeks[:2]:
        week_link = week.get('link')
        if not week_link:
            continue
        game_summaries = get_game_summaries_for_week(week_link, base_url)
        for game in game_summaries:
            game_info = dict(week)
            game_info.update(game)
            player_offense = extract_player_offense_table(game['game_link'], base_url)
            game_info['player_offense'] = player_offense
            all_games.append(game_info)
    return all_games

if __name__ == "__main__":
    weeks = get_week_links()
    all_games = get_all_game_summaries(weeks)
    for g in all_games[0:5]:
        print(g)
