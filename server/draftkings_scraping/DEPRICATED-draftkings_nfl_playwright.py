import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, ElementHandle, Error as PlaywrightError
import pandas as pd
import re
import os
import logging
from typing import List, Dict, Optional
import time
import sys

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

CSV_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "csv_output")
os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

# --- Virtual Environment Check ---
def check_virtualenv():
    venv_path = os.path.join(os.path.dirname(__file__), 'venv')
    if not hasattr(sys, 'real_prefix') and not os.environ.get('VIRTUAL_ENV'):
        print(f"[ERROR] Not running inside the expected virtual environment.\n"
              f"Please activate with: source {venv_path}/bin/activate\n"
              f"Current sys.executable: {sys.executable}\n"
              f"sys.path: {sys.path}")
        sys.exit(1)

check_virtualenv()

# --- Helper Functions for Modular Extraction ---
async def extract_bet_type_labels(template: ElementHandle) -> List[str]:
    logging.info("Entering extract_bet_type_labels")
    label_els = await template.query_selector_all('div.cb-market__label--text-center p.cb-market__label--truncate-strings')
    labels = [await (await label_el.get_property('innerText')).json_value() for label_el in label_els]
    logging.info(f"extract_bet_type_labels: labels={labels}")
    logging.info("Exiting extract_bet_type_labels")
    return labels

async def extract_player_info(player_label: ElementHandle) -> Dict[str, Optional[str]]:
    logging.info("Entering extract_player_info")
    name_el = await player_label.query_selector('p.cb-market__label--truncate-strings')
    player_name = (await name_el.inner_text()).strip() if name_el else None
    link_el = await player_label.query_selector('a.cb-player-page-link')
    player_link = await link_el.get_attribute('href') if link_el else None
    logging.info(f"extract_player_info: player_name={player_name}, player_link={player_link}")
    logging.info("Exiting extract_player_info")
    return {
        "player_name": player_name,
        "player_link": player_link
    }

async def extract_odds_from_buttons(buttons: List[ElementHandle]) -> List[Optional[str]]:
    logging.info("Entering extract_odds_from_buttons")
    odds_list = []
    for idx, btn in enumerate(buttons):
        odds_el = await btn.query_selector('[data-testid="button-odds-market-board"]')
        odds = (await odds_el.inner_text()).strip() if odds_el else None
        odds_list.append(odds)
        logging.info(f"extract_odds_from_buttons: idx={idx}, odds={odds}")
    logging.info(f"extract_odds_from_buttons: odds_list={odds_list}")
    logging.info("Exiting extract_odds_from_buttons")
    return odds_list

async def extract_td_scorer_section(template: ElementHandle) -> List[Dict[str, Optional[str]]]:
    logging.info("Entering extract_td_scorer_section")
    bet_type_labels = await extract_bet_type_labels(template)
    player_labels = await template.query_selector_all('div.cb-market__label--row.cb-market__label--text-left')
    all_buttons = await template.query_selector_all('button.cb-market__button')
    rows = []
    logging.info(f"TD Scorer: bet_type_labels={bet_type_labels}, player_labels={len(player_labels)}, all_buttons={len(all_buttons)}")
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
            logging.info(f"TD Scorer: row={row}")
            rows.append(row)
    if not rows:
        logging.warning("TD Scorer: No rows extracted.")
    logging.info(f"Exiting extract_td_scorer_section with {len(rows)} rows")
    return rows

# --- New: Player Prop Section Extraction ---
async def robust_click(element, page, description="element", max_retries=5):
    for attempt in range(max_retries):
        try:
            await element.scroll_into_view_if_needed()
            await element.click(timeout=5000)
            return True
        except PlaywrightError as e:
            # Check for overlays or intercepting elements
            overlays = await page.query_selector_all('[style*="pointer-events: auto"], .modal, .overlay, .sb-modal, .sb-overlay')
            if overlays:
                for overlay in overlays:
                    try:
                        await page.evaluate('(el) => el.style.display = "none"', overlay)
                    except Exception:
                        pass
            # Take screenshot and log DOM for debugging
            screenshot_path = os.path.join(CSV_OUTPUT_DIR, f"click_error_{description}_{attempt}.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            logging.error(f"[robust_click] Attempt {attempt+1} failed for {description}: {e}. Screenshot: {screenshot_path}")
            # Log DOM structure
            dom_html = await page.content()
            with open(os.path.join(CSV_OUTPUT_DIR, f"click_error_{description}_{attempt}.html"), "w") as f:
                f.write(dom_html)
            await page.wait_for_timeout(1000)
    raise Exception(f"[robust_click] Failed to click {description} after {max_retries} attempts.")

async def ensure_sections_present(page):
    for attempt in range(MAX_SECTION_RETRIES):
        await page.wait_for_selector('h2.cb-collapsible-header[data-testid="collapsible-header"]', timeout=10000)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        triggers = await page.query_selector_all('button.cb-collapsible-trigger')
        for idx, trigger in enumerate(triggers):
            try:
                await robust_click(trigger, page, description=f"collapsible-trigger-{idx}")
            except Exception as e:
                logging.warning(f"Failed to click trigger {idx}: {e}")
        headers = await page.query_selector_all('h2.cb-collapsible-header[data-testid="collapsible-header"]')
        titles = [((await (await h.get_property('innerText')).json_value()).strip()) for h in headers]
        norm_titles = [t.lower() for t in titles]
        logging.info(f"[Section Check Attempt {attempt+1}] Found section titles: {titles}")
        if len(set(norm_titles)) != len(norm_titles):
            logging.warning(f"Duplicate section titles found: {titles}")
        missing = [s for s in REQUIRED_SECTIONS if s.lower() not in norm_titles]
        if not missing:
            return titles
        logging.warning(f"Missing sections: {missing}. Retrying in {RETRY_DELAY_SEC}s...")
        await page.wait_for_timeout(RETRY_DELAY_SEC * 1000)
    raise Exception(f"Missing required sections after {MAX_SECTION_RETRIES} retries: {missing}. Found: {titles}")

async def extract_all_prop_odds_from_slider(slider, prop_label, page=None):
    logging.info(f"Entering extract_all_prop_odds_from_slider for prop_label={prop_label}")
    prop_buttons = await slider.query_selector_all('button.cb-selection-picker__selection')
    prop_values = []
    for btn in prop_buttons:
        label_el = await btn.query_selector('span.cb-selection-picker__selection-label')
        label = (await label_el.inner_text()).strip() if label_el else None
        prop_values.append(label)
        logging.info(f"Slider: prop_value={label}")
    odds_results = []
    right_arrow = await slider.query_selector('button.cb-selection-picker__right-arrow')
    left_arrow = await slider.query_selector('button.cb-selection-picker__left-arrow')
    logging.info(f"Slider: right_arrow={right_arrow is not None}, left_arrow={left_arrow is not None}")
    for _ in range(len(prop_values)):
        focused_btn = await slider.query_selector('button.cb-selection-picker__selection--focused')
        focused_label_el = await focused_btn.query_selector('span.cb-selection-picker__selection-label')
        focused_label = (await focused_label_el.inner_text()).strip() if focused_label_el else None
        logging.info(f"Slider: focused_label={focused_label}")
        if focused_label == prop_values[0]:
            break
        if left_arrow:
            await robust_click(left_arrow, page, description="slider-left-arrow")
            await slider.wait_for_selector('button.cb-selection-picker__selection--focused', timeout=1000)
    for i, label in enumerate(prop_values):
        focused_btn = await slider.query_selector('button.cb-selection-picker__selection--focused')
        odds_el = await focused_btn.query_selector('span.cb-selection-picker__selection-odds')
        odds = (await odds_el.inner_text()).strip() if odds_el else None
        odds_results.append({prop_label: label, 'odds': odds})
        logging.info(f"Slider: i={i}, label={label}, odds={odds}")
        if i < len(prop_values) - 1 and right_arrow:
            await robust_click(right_arrow, page, description="slider-right-arrow")
            await slider.wait_for_selector('button.cb-selection-picker__selection--focused', timeout=1000)
    logging.info(f"Exiting extract_all_prop_odds_from_slider with {len(odds_results)} results")
    return odds_results

async def extract_player_prop_section(template: ElementHandle, prop_label: str, page=None) -> List[Dict[str, Optional[str]]]:
    logging.info(f"Entering extract_player_prop_section for prop_label={prop_label}")
    player_label = await template.query_selector('div.cb-market__label--row.cb-market__label--text-left')
    player_info = await extract_player_info(player_label) if player_label else {}
    slider = await template.query_selector('div.cb-market-buttons-slider .cb-selection-picker')
    rows = []
    if slider:
        odds_results = await extract_all_prop_odds_from_slider(slider, prop_label, page=page)
        for result in odds_results:
            row = {
                **player_info,
                prop_label: result[prop_label],
                "odds": result["odds"]
            }
            logging.info(f"Player Prop: row={row}")
            rows.append(row)
    logging.info(f"Exiting extract_player_prop_section with {len(rows)} rows")
    return rows

# --- Modular Betting Section Extraction ---
async def extract_td_scorer_section_to_df(team_bet_rows, section_title):
    logging.info(f"Entering extract_td_scorer_section_to_df for section_title={section_title}")
    all_rows = []
    for idx, template in enumerate(team_bet_rows):
        logging.info(f"TD Scorer Section: template idx={idx}")
        rows = await extract_td_scorer_section(template)
        all_rows.extend(rows)
    if all_rows:
        df = pd.DataFrame(all_rows)
        sheet_name = section_title.replace(' ', '_')[:31]
        logging.info(f"Extracted {len(all_rows)} rows for betting section: {section_title}")
        logging.info(f"Exiting extract_td_scorer_section_to_df with DataFrame shape={df.shape}")
        return sheet_name, df
    else:
        logging.info(f"No rows found for betting section: {section_title}")
        logging.info("Exiting extract_td_scorer_section_to_df with no data")
    return None

async def extract_game_section_to_df(team_bet_rows, section_title):
    logging.info(f"Entering extract_game_section_to_df for section_title={section_title}")
    bet_category_labels = await extract_bet_type_labels(team_bet_rows[0])
    rows = []
    for idx, team_bet_row in enumerate(team_bet_rows):
        logging.info(f"Game Section: team_bet_row idx={idx}")
        team_name_el = await team_bet_row.query_selector('.cb-market__label-inner--parlay')
        team_name = (await team_name_el.inner_text()).strip() if team_name_el else None
        bet_buttons = await team_bet_row.query_selector_all('button.cb-market__button')
        for btn_idx, btn in enumerate(bet_buttons):
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
            bet_category = bet_category_labels[btn_idx] if btn_idx < len(bet_category_labels) else None
            row = {
                "team": team_name,
                "bet_category": bet_category,
                "points": points,
                "odds": odds,
                "title": title
            }
            logging.info(f"Game Section: row={row}")
            rows.append(row)
    if rows:
        df = pd.DataFrame(rows)
        sheet_name = section_title.replace(' ', '_')[:31]
        logging.info(f"Extracted {len(rows)} rows for betting section: {section_title}")
        logging.info(f"Exiting extract_game_section_to_df with DataFrame shape={df.shape}")
        return sheet_name, df
    else:
        logging.info(f"No rows found for betting section: {section_title}")
        logging.info("Exiting extract_game_section_to_df with no data")
    return None

async def extract_player_prop_section_to_df(team_bet_rows, section_title, prop_label, page=None):
    logging.info(f"Entering extract_player_prop_section_to_df for section_title={section_title}, prop_label={prop_label}")
    all_rows = []
    for idx, template in enumerate(team_bet_rows):
        logging.info(f"Player Prop Section: template idx={idx}")
        rows = await extract_player_prop_section(template, prop_label, page=page)
        all_rows.extend(rows)
    if all_rows:
        df = pd.DataFrame(all_rows)
        sheet_name = section_title.replace(' ', '_')[:31]
        logging.info(f"Extracted {len(all_rows)} rows for betting section: {section_title}")
        logging.info(f"Exiting extract_player_prop_section_to_df with DataFrame shape={df.shape}")
        return sheet_name, df
    else:
        logging.info(f"No rows found for betting section: {section_title}")
        logging.info("Exiting extract_player_prop_section_to_df with no data")
    return None

async def extract_other_section_to_df(team_bet_rows, section_title):
    logging.info(f"Entering extract_other_section_to_df for section_title={section_title}")
    rows = []
    for idx, team_bet_row in enumerate(team_bet_rows):
        logging.info(f"Other Section: team_bet_row idx={idx}")
        team_name_el = await team_bet_row.query_selector('.cb-market__label-inner--parlay')
        team_name = (await team_name_el.inner_text()).strip() if team_name_el else None
        bet_buttons = await team_bet_row.query_selector_all('button.cb-market__button')
        for btn_idx, btn in enumerate(bet_buttons):
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
            row = {
                "team": team_name,
                "points": points,
                "odds": odds,
                "title": title
            }
            logging.info(f"Other Section: row={row}")
            rows.append(row)
    if rows:
        df = pd.DataFrame(rows)
        sheet_name = section_title.replace(' ', '_')[:31]
        logging.info(f"Extracted {len(rows)} rows for betting section: {section_title}")
        logging.info(f"Exiting extract_other_section_to_df with DataFrame shape={df.shape}")
        return sheet_name, df
    else:
        logging.info(f"No rows found for betting section: {section_title}")
        logging.info("Exiting extract_other_section_to_df with no data")
    return None

def match_section(title, patterns):
    logging.info(f"match_section: title={title}, patterns={patterns}")
    for pat in patterns:
        if re.search(pat, title, re.IGNORECASE):
            logging.info(f"match_section: matched pattern={pat}")
            return True
    logging.info("match_section: no match")
    return False

REQUIRED_SECTIONS = ["Game", "TD Scorer", "Pass Yards", "Receiving Yards", "Rush Yards"]
MAX_SECTION_RETRIES = 3
RETRY_DELAY_SEC = 2

async def is_section_expanded(header_el):
    # Check aria-expanded or class/state to determine if expanded
    aria_expanded = await header_el.get_attribute('aria-expanded')
    if aria_expanded is not None:
        return aria_expanded == 'true'
    # Fallback: check for a class or style indicating expanded
    class_val = await header_el.get_attribute('class')
    if class_val and 'expanded' in class_val:
        return True
    return False

async def ensure_section_expanded(page, section_title):
    headers = await page.query_selector_all('h2.cb-collapsible-header[data-testid="collapsible-header"]')
    for idx, header in enumerate(headers):
        text = (await (await header.get_property('innerText')).json_value()).strip()
        if text.lower() == section_title.lower():
            expanded = await is_section_expanded(header)
            logging.info(f"Section '{section_title}' expanded state before click: {expanded}")
            if not expanded:
                parent = await header.evaluate_handle('el => el.parentElement')
                trigger = await parent.query_selector('button.cb-collapsible-trigger')
                if trigger:
                    await robust_click(trigger, page, description=f"expand-{section_title}")
                    await page.wait_for_timeout(500)  # Wait for animation
                    expanded_after = await is_section_expanded(header)
                    logging.info(f"Section '{section_title}' expanded state after click: {expanded_after}")
                else:
                    logging.warning(f"No trigger found for section '{section_title}'")
            else:
                logging.info(f"Section '{section_title}' already expanded, no click needed.")
            return
    logging.warning(f"Section header '{section_title}' not found for expansion.")

async def extract_betting_sections(page):
    logging.info("Entering extract_betting_sections")
    section_titles = await ensure_sections_present(page)
    betting_sections = await page.query_selector_all('div.cb-subcategory[data-testid="component-builder-market"]')
    if not betting_sections:
        raise Exception("No betting sections found on the page.")
    logging.info(f"Found {len(betting_sections)} betting_sections")
    section_dfs = {}
    found_sections = []
    for idx, betting_section in enumerate(betting_sections):
        section_title_el = await betting_section.query_selector('h2.cb-collapsible-header[data-testid="collapsible-header"]')
        if not section_title_el:
            raise Exception(f"Section header not found for section index {idx}")
        section_title = (await section_title_el.inner_text()).strip()
        found_sections.append(section_title)
        norm_title = section_title.lower()
        logging.info(f"Extracting betting section: {section_title}")
        # Ensure section is expanded before extracting
        await ensure_section_expanded(page, section_title)
        team_bet_rows = await betting_section.query_selector_all('div.cb-market__template')
        if not team_bet_rows:
            raise Exception(f"No market templates found for section '{section_title}'")
        if norm_title == "td scorer" and team_bet_rows:
            result = await extract_td_scorer_section_to_df(team_bet_rows, section_title)
        elif norm_title == "game" and team_bet_rows:
            result = await extract_game_section_to_df(team_bet_rows, section_title)
        elif any(p in norm_title for p in ["pass yards", "passing yards", "pass yds"]):
            result = await extract_player_prop_section_to_df(team_bet_rows, section_title, "passing_yards", page=page)
        elif any(p in norm_title for p in ["receiving yards", "receiving yds"]):
            result = await extract_player_prop_section_to_df(team_bet_rows, section_title, "receiving_yards", page=page)
        elif any(p in norm_title for p in ["rush yards", "rushing yards", "rush yds"]):
            result = await extract_player_prop_section_to_df(team_bet_rows, section_title, "rushing_yards", page=page)
        else:
            result = await extract_other_section_to_df(team_bet_rows, section_title)
        if result:
            sheet_name, df = result
            section_dfs[sheet_name] = df
            logging.info(f"Added DataFrame for sheet_name={sheet_name}, shape={df.shape}")
        else:
            raise Exception(f"No DataFrame returned for required section '{section_title}'")
    found_norm = [s.lower() for s in found_sections]
    missing_sections = [s for s in REQUIRED_SECTIONS if s.lower() not in found_norm]
    if missing_sections:
        raise Exception(f"Missing required sections: {missing_sections}")
    logging.info(f"Exiting extract_betting_sections with {len(section_dfs)} DataFrames")
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
        excel_filename = os.path.join(CSV_OUTPUT_DIR, f"{game_slug}.xlsx")
        with pd.ExcelWriter(excel_filename) as writer:
            for sheet_name, df in section_dfs.items():
                logging.info(f"Writing sheet '{sheet_name}' to {excel_filename}")
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                # Write CSV for each sheet, including game_slug in the filename
                csv_name = os.path.join(CSV_OUTPUT_DIR, f"{game_slug}_{slugify(sheet_name)}.csv")
                df.to_csv(csv_name, index=False)
                logging.info(f"Wrote CSV: {csv_name} shape={df.shape}")
        logging.info(f"Saved all tables for {game_slug} to {excel_filename}")
    else:
        logging.info(f"No tables found for {game_slug}, nothing written.")
    await browser.close()

async def scrape_draftkings_nfl():
    logging.info("Entering scrape_draftkings_nfl")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(DK_URL)
        await page.screenshot(path="draftkings_nfl_screenshot.png", full_page=True)

        games = []
        sections = await page.query_selector_all('table[data-testid="sportsbook-table"]')
        logging.info(f"Found {len(sections)} sportsbook-table sections")
        first_game_scraped = False
        for section_idx, section in enumerate(sections):
            if first_game_scraped:
                break
            logging.info(f"Processing sportsbook-table section_idx={section_idx}")
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
                if first_game_scraped:
                    break
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
                    logging.info(f"Parsed game: {games[-1]}")
                    if game_url and not first_game_scraped:
                        first_game_scraped = True
                        game_slug = slugify(f"{team1_name}-{team2_name}")
                        await scrape_game_tables_to_excel(p, game_url, game_slug)
                        
                        break  # Break inner while
                    i += 2
                except Exception as e:
                    logging.error(f"Error parsing section group: {e}")
                    i += 2
            if first_game_scraped:
                break  # Break outer for
        await browser.close()
        logging.info("Exiting scrape_draftkings_nfl")
        return games

def main():
    logging.info("Starting main()")
    games = asyncio.run(scrape_draftkings_nfl())
    df = pd.DataFrame(games)
    print(df)
    df.to_csv("draftkings_nfl_games.csv", index=False)
    logging.info("main() complete")

if __name__ == "__main__":
    main() 