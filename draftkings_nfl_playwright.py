import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, ElementHandle
import pandas as pd
import re
import os
import logging
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

DK_URL = "https://sportsbook.draftkings.com/leagues/football/nfl?category=game-lines&subcategory=game"
BASE_URL = "https://sportsbook.draftkings.com"

# Table types to extract
TABLE_TYPES = [
    "Game Lines",
    "TD Scorers",
    "Passing Props",
    "Receiving Props",
    "Rushing Props"
]

# Helper to slugify game name for filenames
slugify = lambda s: re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-')

# --- Helper Functions for Modular Extraction ---
async def extract_bet_type_labels(template: ElementHandle) -> List[str]:
    label_els = await template.query_selector_all('div.cb-market__label--text-center p.cb-market__label--truncate-strings')
    return [await (await label_el.get_property('innerText')).json_value() for label_el in label_els]

async def extract_player_info(player_label: ElementHandle) -> Dict[str, Optional[str]]:
    name_el = await player_label.query_selector('p.cb-market__label--truncate-strings')
    player_name = (await name_el.inner_text()).strip() if name_el else None
    link_el = await player_label.query_selector('a.cb-player-page-link')
    player_link = await link_el.get_attribute('href') if link_el else None
    return {
        "player_name": player_name,
        "player_link": player_link
    }

async def extract_odds_from_buttons(buttons: List[ElementHandle]) -> List[Optional[str]]:
    odds_list = []
    for btn in buttons:
        odds_el = await btn.query_selector('[data-testid="button-odds-market-board"]')
        odds = (await odds_el.inner_text()).strip() if odds_el else None
        odds_list.append(odds)
    return odds_list

async def extract_td_scorer_section(template: ElementHandle) -> List[Dict[str, Optional[str]]]:
    bet_type_labels = await extract_bet_type_labels(template)
    player_labels = await template.query_selector_all('div.cb-market__label--row.cb-market__label--text-left')
    all_buttons = await template.query_selector_all('button.cb-market__button')
    rows = []
    if len(player_labels) * len(bet_type_labels) != len(all_buttons):
        logging.warning(f"TD Scorer: Mismatch between player labels ({len(player_labels)}) × bet types ({len(bet_type_labels)}) and buttons ({len(all_buttons)}). Data may be incomplete.")
    for i, player_label in enumerate(player_labels):
        player_info = await extract_player_info(player_label)
        btns = all_buttons[i*len(bet_type_labels):(i+1)*len(bet_type_labels)]
        odds_list = await extract_odds_from_buttons(btns)
        for idx, odds in enumerate(odds_list):
            row = {
                **player_info,
                "bet_type": bet_type_labels[idx] if idx < len(bet_type_labels) else None,
                "odds": odds
            }
            rows.append(row)
    if not rows:
        logging.warning("TD Scorer: No rows extracted.")
    return rows

# --- New: Player Prop Section Extraction ---
async def extract_all_prop_odds_from_slider(slider):
    prop_buttons = await slider.query_selector_all('button.cb-selection-picker__selection')
    prop_labels = []
    for btn in prop_buttons:
        label_el = await btn.query_selector('span.cb-selection-picker__selection-label')
        label = (await label_el.inner_text()).strip() if label_el else None
        prop_labels.append(label)
    odds_results = []
    right_arrow = await slider.query_selector('button.cb-selection-picker__right-arrow')
    left_arrow = await slider.query_selector('button.cb-selection-picker__left-arrow')
    # Move to the leftmost label
    for _ in range(len(prop_labels)):
        focused_btn = await slider.query_selector('button.cb-selection-picker__selection--focused')
        focused_label_el = await focused_btn.query_selector('span.cb-selection-picker__selection-label')
        focused_label = (await focused_label_el.inner_text()).strip() if focused_label_el else None
        if focused_label == prop_labels[0]:
            break
        if left_arrow:
            await left_arrow.click()
            await slider.wait_for_selector('button.cb-selection-picker__selection--focused', timeout=1000)
    # Iterate through all labels, clicking right each time
    for i, label in enumerate(prop_labels):
        focused_btn = await slider.query_selector('button.cb-selection-picker__selection--focused')
        odds_el = await focused_btn.query_selector('span.cb-selection-picker__selection-odds')
        odds = (await odds_el.inner_text()).strip() if odds_el else None
        odds_results.append({'prop_label': label, 'odds': odds})
        if i < len(prop_labels) - 1 and right_arrow:
            await right_arrow.click()
            await slider.wait_for_selector('button.cb-selection-picker__selection--focused', timeout=1000)
    return odds_results

async def extract_player_prop_section(template: ElementHandle) -> List[Dict[str, Optional[str]]]:
    player_label = await template.query_selector('div.cb-market__label--row.cb-market__label--text-left')
    player_info = await extract_player_info(player_label) if player_label else {}
    slider = await template.query_selector('div.cb-market-buttons-slider .cb-selection-picker')
    rows = []
    if slider:
        odds_results = await extract_all_prop_odds_from_slider(slider)
        for result in odds_results:
            rows.append({
                **player_info,
                "prop_label": result["prop_label"],
                "odds": result["odds"]
            })
    return rows

# --- Modular Betting Section Extraction ---
async def extract_betting_sections(page):
    betting_sections = await page.query_selector_all('div.cb-subcategory[data-testid="component-builder-market"]')
    section_dfs = {}
    for betting_section in betting_sections:
        section_title_el = await betting_section.query_selector('h2.cb-collapsible-header[data-testid="collapsible-header"]')
        section_title = (await section_title_el.inner_text()).strip() if section_title_el else "Betting Section"
        logging.info(f"Extracting betting section: {section_title}")
        team_bet_rows = await betting_section.query_selector_all('div.cb-market__template')
        # --- TD Scorer Section ---
        if section_title.lower() == "td scorer" and team_bet_rows:
            all_rows = []
            for template in team_bet_rows:
                rows = await extract_td_scorer_section(template)
                all_rows.extend(rows)
            if all_rows:
                df = pd.DataFrame(all_rows)
                sheet_name = section_title.replace(' ', '_')[:31]
                section_dfs[sheet_name] = df
                logging.info(f"Extracted {len(all_rows)} rows for betting section: {section_title}")
            else:
                logging.info(f"No rows found for betting section: {section_title}")
        # --- Game Section ---
        elif section_title.lower() == "game" and team_bet_rows:
            bet_category_labels = await extract_bet_type_labels(team_bet_rows[0])
            rows = []
            for team_bet_row in team_bet_rows:
                team_name_el = await team_bet_row.query_selector('.cb-market__label-inner--parlay')
                team_name = (await team_name_el.inner_text()).strip() if team_name_el else None
                bet_buttons = await team_bet_row.query_selector_all('button.cb-market__button')
                for idx, btn in enumerate(bet_buttons):
                    points = odds = title = None
                    points_el = await btn.query_selector('[data-testid="button-points-market-board"]')
                    if points_el:
                        points = (await points_el.inner_text()).strip()
                    odds_el = await btn.query_selector('[data-testid="button-odds-market-board"]')
                    if odds_el:
                        odds = (await odds_el.inner_text()).strip()
                    title_el = await btn.query_selector('[data-testid="button-title-market-board"]')
                    if title_el:
                        title = (await title_el.inner_text()).strip()
                    bet_category = bet_category_labels[idx] if idx < len(bet_category_labels) else None
                    rows.append({
                        "team": team_name,
                        "bet_category": bet_category,
                        "points": points,
                        "odds": odds,
                        "title": title
                    })
            if rows:
                df = pd.DataFrame(rows)
                sheet_name = section_title.replace(' ', '_')[:31]
                section_dfs[sheet_name] = df
                logging.info(f"Extracted {len(rows)} rows for betting section: {section_title}")
            else:
                logging.info(f"No rows found for betting section: {section_title}")
        # --- Player Prop Sections (Pass Yards, Receiving Yards, Rushing Yards, etc.) ---
        elif any(x in section_title.lower() for x in ["pass yards", "receiving yards", "rushing yards"]) and team_bet_rows:
            all_rows = []
            for template in team_bet_rows:
                rows = await extract_player_prop_section(template)
                all_rows.extend(rows)
            if all_rows:
                df = pd.DataFrame(all_rows)
                sheet_name = section_title.replace(' ', '_')[:31]
                section_dfs[sheet_name] = df
                logging.info(f"Extracted {len(all_rows)} rows for betting section: {section_title}")
            else:
                logging.info(f"No rows found for betting section: {section_title}")
        # --- Other Sections ---
        else:
            rows = []
            for team_bet_row in team_bet_rows:
                team_name_el = await team_bet_row.query_selector('.cb-market__label-inner--parlay')
                team_name = (await team_name_el.inner_text()).strip() if team_name_el else None
                bet_buttons = await team_bet_row.query_selector_all('button.cb-market__button')
                for btn in bet_buttons:
                    points = odds = title = None
                    points_el = await btn.query_selector('[data-testid="button-points-market-board"]')
                    if points_el:
                        points = (await points_el.inner_text()).strip()
                    odds_el = await btn.query_selector('[data-testid="button-odds-market-board"]')
                    if odds_el:
                        odds = (await odds_el.inner_text()).strip()
                    title_el = await btn.query_selector('[data-testid="button-title-market-board"]')
                    if title_el:
                        title = (await title_el.inner_text()).strip()
                    rows.append({
                        "team": team_name,
                        "points": points,
                        "odds": odds,
                        "title": title
                    })
            if rows:
                df = pd.DataFrame(rows)
                sheet_name = section_title.replace(' ', '_')[:31]
                section_dfs[sheet_name] = df
                logging.info(f"Extracted {len(rows)} rows for betting section: {section_title}")
            else:
                logging.info(f"No rows found for betting section: {section_title}")
    return section_dfs

# --- Main Scraping Logic (no table extraction) ---
async def scrape_game_tables_to_excel(playwright, game_url, game_slug):
    logging.info(f"\n--- Scraping game page: {game_url} ---")
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(game_url)
    await page.wait_for_timeout(5000)  # Wait for JS to load content
    section_dfs = await extract_betting_sections(page)
    if section_dfs:
        excel_filename = f"{game_slug}.xlsx"
        with pd.ExcelWriter(excel_filename) as writer:
            for sheet_name, df in section_dfs.items():
                logging.info(f"Writing sheet '{sheet_name}' to {excel_filename}")
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        logging.info(f"Saved all tables for {game_slug} to {excel_filename}")
    else:
        logging.info(f"No tables found for {game_slug}, nothing written.")
    await browser.close()

async def scrape_draftkings_nfl():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(DK_URL)
        await page.screenshot(path="draftkings_nfl_screenshot.png", full_page=True)

        games = []
        sections = await page.query_selector_all('table[data-testid="sportsbook-table"]')
        first_game_scraped = False
        for section in sections:
            date = None
            thead = await section.query_selector('thead')
            if thead:
                date_el = await thead.query_selector('span span')
                if date_el:
                    date = (await date_el.inner_text()).strip()
            tbody = await section.query_selector('tbody.sportsbook-table__body')
            if not tbody:
                continue
            rows = await tbody.query_selector_all('tr')
            i = 0
            while i < len(rows) - 1:
                try:
                    row1 = rows[i]
                    th1 = await row1.query_selector('th.sportsbook-table__column-row')
                    team1_name = (await (await th1.query_selector('.event-cell__name-text')).inner_text()).strip() if th1 else None
                    start_time_el = await th1.query_selector('.event-cell__start-time') if th1 else None
                    start_time = (await start_time_el.inner_text()).strip() if start_time_el else None
                    event_link_el = await th1.query_selector('a.event-cell-link') if th1 else None
                    game_url = None
                    if event_link_el:
                        href = await event_link_el.get_attribute('href')
                        if href:
                            game_url = BASE_URL + href.split('?')[0] + '?category=odds&subcategory=popular'
                    tds1 = await row1.query_selector_all('td.sportsbook-table__column-row')
                    spread1 = (await (await tds1[0].query_selector('[data-testid="sportsbook-outcome-cell-line"]')).inner_text()).strip() if len(tds1) >= 3 and await tds1[0].query_selector('[data-testid="sportsbook-outcome-cell-line"]') else None
                    odds_spread1 = (await (await tds1[0].query_selector('[data-testid="sportsbook-odds"]')).inner_text()).strip() if len(tds1) >= 3 and await tds1[0].query_selector('[data-testid="sportsbook-odds"]') else None
                    total1 = (await (await tds1[1].query_selector('[data-testid="sportsbook-outcome-cell-line"]')).inner_text()).strip() if len(tds1) >= 3 and await tds1[1].query_selector('[data-testid="sportsbook-outcome-cell-line"]') else None
                    odds_total1 = (await (await tds1[1].query_selector('[data-testid="sportsbook-odds"]')).inner_text()).strip() if len(tds1) >= 3 and await tds1[1].query_selector('[data-testid="sportsbook-odds"]') else None
                    moneyline1 = (await (await tds1[2].query_selector('[data-testid="sportsbook-odds"]')).inner_text()).strip() if len(tds1) >= 3 and await tds1[2].query_selector('[data-testid="sportsbook-odds"]') else None

                    row2 = rows[i+1]
                    th2 = await row2.query_selector('th.sportsbook-table__column-row')
                    team2_name = (await (await th2.query_selector('.event-cell__name-text')).inner_text()).strip() if th2 else None
                    tds2 = await row2.query_selector_all('td.sportsbook-table__column-row')
                    spread2 = (await (await tds2[0].query_selector('[data-testid="sportsbook-outcome-cell-line"]')).inner_text()).strip() if len(tds2) >= 3 and await tds2[0].query_selector('[data-testid="sportsbook-outcome-cell-line"]') else None
                    odds_spread2 = (await (await tds2[0].query_selector('[data-testid="sportsbook-odds"]')).inner_text()).strip() if len(tds2) >= 3 and await tds2[0].query_selector('[data-testid="sportsbook-odds"]') else None
                    total2 = (await (await tds2[1].query_selector('[data-testid="sportsbook-outcome-cell-line"]')).inner_text()).strip() if len(tds2) >= 3 and await tds2[1].query_selector('[data-testid="sportsbook-outcome-cell-line"]') else None
                    odds_total2 = (await (await tds2[1].query_selector('[data-testid="sportsbook-odds"]')).inner_text()).strip() if len(tds2) >= 3 and await tds2[1].query_selector('[data-testid="sportsbook-odds"]') else None
                    moneyline2 = (await (await tds2[2].query_selector('[data-testid="sportsbook-odds"]')).inner_text()).strip() if len(tds2) >= 3 and await tds2[2].query_selector('[data-testid="sportsbook-odds"]') else None

                    games.append({
                        "date": date,
                        "start_time": start_time,
                        "game_url": game_url,
                        "team1": team1_name,
                        "spread1": spread1,
                        "odds_spread1": odds_spread1,
                        "total1": total1,
                        "odds_total1": odds_total1,
                        "moneyline1": moneyline1,
                        "team2": team2_name,
                        "spread2": spread2,
                        "odds_spread2": odds_spread2,
                        "total2": total2,
                        "odds_total2": odds_total2,
                        "moneyline2": moneyline2,
                    })
                    if game_url and not first_game_scraped:
                        game_slug = slugify(f"{team1_name}-{team2_name}")
                        await scrape_game_tables_to_excel(p, game_url, game_slug)
                        first_game_scraped = True
                    i += 2
                except Exception as e:
                    logging.error(f"Error parsing section group: {e}")
                    i += 2

        await browser.close()
        return games

def main():
    games = asyncio.run(scrape_draftkings_nfl())
    df = pd.DataFrame(games)
    print(df)
    df.to_csv("draftkings_nfl_games.csv", index=False)

if __name__ == "__main__":
    main() 