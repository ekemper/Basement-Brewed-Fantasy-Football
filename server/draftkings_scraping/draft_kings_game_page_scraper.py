import asyncio
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
import pandas as pd
import sys
import re
import traceback
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

SECTION_TITLES = ["Pass Yards", "Rush Yards", "Receiving Yards", "TD Scorer", "Game"]

def filter_df(df):
    return df[df['odds'].notnull() & (df['odds'] != '')]

async def robust_click(element, page, description="element", max_retries=5):
    last_exception = None
    for attempt in range(max_retries):
        try:
            await element.scroll_into_view_if_needed()
            await element.click(timeout=5000)
            return True
        except PlaywrightError as e:
            last_exception = e
            # Only log and continue for recoverable errors (DOM detachment handled by caller)
            if hasattr(e, 'message') and 'Element is not attached to the DOM' in e.message:
                logging.info(f"[robust_click] Attempt {attempt+1} for {description}: Element detached, will retry if possible.")
                await page.wait_for_timeout(500)
                continue
            if hasattr(e, 'args') and any('Element is not attached to the DOM' in str(arg) for arg in e.args):
                logging.info(f"[robust_click] Attempt {attempt+1} for {description}: Element detached, will retry if possible.")
                await page.wait_for_timeout(500)
                continue
            # For other errors, log and create debug files
            screenshot_path = f"click_error_{description}_{attempt}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            logging.error(f"[robust_click] Attempt {attempt+1} failed for {description}: {e}. Screenshot: {screenshot_path}")
            dom_html = await page.content()
            with open(f"click_error_{description}_{attempt}.html", "w") as f:
                f.write(dom_html)
            await page.wait_for_timeout(1000)
    # If all retries fail, create error files for the last attempt
    screenshot_path = f"click_error_{description}_final.png"
    await page.screenshot(path=screenshot_path, full_page=True)
    dom_html = await page.content()
    with open(f"click_error_{description}_final.html", "w") as f:
        f.write(dom_html)
    raise Exception(f"[robust_click] Failed to click {description} after {max_retries} attempts. Last error: {last_exception}")

async def ensure_section_expanded(page, section_title):
    headers = await page.query_selector_all('h2.cb-collapsible-header[data-testid="collapsible-header"]')
    for idx, header in enumerate(headers):
        text = (await (await header.get_property('innerText')).json_value()).strip()
        if text.lower() == section_title.lower():
            parent = await header.evaluate_handle('el => el.parentElement')
            trigger = await parent.query_selector('button.cb-collapsible-trigger')
            if trigger:
                await robust_click(trigger, page, description=f"expand-{section_title}")
                await page.wait_for_timeout(500)
            return
    raise Exception(f"Section header '{section_title}' not found for expansion.")

async def extract_all_slider_options(slider, player_name, page):
    def is_detached_error(e):
        return (
            hasattr(e, 'message') and 'Element is not attached to the DOM' in e.message
        ) or (
            hasattr(e, 'args') and any('Element is not attached to the DOM' in str(arg) for arg in e.args)
        )

    seen = set()
    all_rows = []
    max_moves = 20
    moves = 0
    # Move to the leftmost position first
    while moves < max_moves:
        left_arrow = await slider.query_selector('button.cb-selection-picker__left-arrow')
        if not left_arrow:
            break
        class_val = await left_arrow.get_attribute('class') or ''
        if 'disabled' in class_val:
            break
        try:
            await robust_click(left_arrow, page, description=f"slider-left-arrow-{player_name}")
            await slider.wait_for_selector('button.cb-selection-picker__selection--focused', timeout=1000)
        except Exception as e:
            if is_detached_error(e):
                logging.info(f"Left arrow detached for {player_name}, re-querying and retrying...")
                continue  # re-query and retry
            logging.warning(f"Failed to click left arrow for {player_name}: {e}")
            break
        moves += 1
    # Now iterate right, collecting all options
    moves = 0
    while moves < max_moves:
        selections = await slider.query_selector_all('button.cb-selection-picker__selection')
        for btn in selections:
            label_el = await btn.query_selector('span.cb-selection-picker__selection-label')
            label = (await label_el.inner_text()).strip() if label_el else None
            odds_el = await btn.query_selector('span.cb-selection-picker__selection-odds')
            odds = (await odds_el.inner_text()).strip() if odds_el else None
            is_focused = 'cb-selection-picker__selection--focused' in (await btn.get_attribute('class') or '')
            key = (label, odds, is_focused)
            if label and key not in seen:
                all_rows.append({
                    'player': player_name,
                    'range': label,
                    'odds': odds,
                    'selected': is_focused
                })
                seen.add(key)
        right_arrow = await slider.query_selector('button.cb-selection-picker__right-arrow')
        if not right_arrow:
            break
        class_val = await right_arrow.get_attribute('class') or ''
        if 'disabled' in class_val:
            break
        try:
            await robust_click(right_arrow, page, description=f"slider-right-arrow-{player_name}")
            await slider.wait_for_selector('button.cb-selection-picker__selection--focused', timeout=1000)
        except Exception as e:
            if is_detached_error(e):
                logging.info(f"Right arrow detached for {player_name}, re-querying and retrying...")
                continue  # re-query and retry
            logging.warning(f"Failed to click right arrow for {player_name}: {e}")
            break
        moves += 1
    return all_rows

async def extract_section(page, section_title):
    betting_sections = await page.query_selector_all('div.cb-subcategory[data-testid="component-builder-market"]')
    for section in betting_sections:
        section_title_el = await section.query_selector('h2.cb-collapsible-header[data-testid="collapsible-header"]')
        if not section_title_el:
            continue
        found_title = (await section_title_el.inner_text()).strip()
        if found_title.lower() == section_title.lower():
            await ensure_section_expanded(page, section_title)
            templates = await section.query_selector_all('div.cb-market__template')
            all_rows = []
            for template in templates:
                player_label = await template.query_selector('div.cb-market__label--row.cb-market__label--text-left')
                player_name = None
                if player_label:
                    name_el = await player_label.query_selector('p.cb-market__label--truncate-strings')
                    if name_el:
                        player_name = (await name_el.inner_text()).strip()
                slider = await template.query_selector('div.cb-market-buttons-slider .cb-selection-picker')
                if not slider:
                    logging.warning(f"No slider found for player {player_name} in section {section_title}")
                    continue
                player_rows = await extract_all_slider_options(slider, player_name, page)
                all_rows.extend(player_rows)
            if not all_rows:
                raise Exception(f"No data found in the section {section_title}.")
            df = pd.DataFrame(all_rows)
            df = filter_df(df)
            return df
    raise Exception(f"Could not find section titled '{section_title}'")

async def extract_td_scorer_section(page, section_title):
    betting_sections = await page.query_selector_all('div.cb-subcategory[data-testid="component-builder-market"]')
    for section in betting_sections:
        section_title_el = await section.query_selector('h2.cb-collapsible-header[data-testid="collapsible-header"]')
        if not section_title_el:
            continue
        found_title = (await section_title_el.inner_text()).strip()
        if found_title.lower() == section_title.lower():
            await ensure_section_expanded(page, section_title)
            template = await section.query_selector('div.cb-market__template')
            if not template:
                raise Exception(f"No market template found in {section_title} section.")
            # Get bet type labels (e.g., First TD Scorer, Anytime TD Scorer, 2+ TDs)
            bet_type_labels = []
            bet_type_els = await template.query_selector_all('div.cb-market__label.cb-market__label--text-center p.cb-market__label--truncate-strings')
            for el in bet_type_els:
                bet_type_labels.append((await el.inner_text()).strip())
            # Get all player rows and odds
            player_labels = await template.query_selector_all('div.cb-market__label.cb-market__label--row.cb-market__label--text-left')
            all_buttons = await template.query_selector_all('button.cb-market__button')
            rows = []
            for i, player_label in enumerate(player_labels):
                # Player name
                name_el = await player_label.query_selector('p.cb-market__label--truncate-strings')
                player_name = (await name_el.inner_text()).strip() if name_el else None
                # There are len(bet_type_labels) buttons per player
                btns = all_buttons[i*len(bet_type_labels):(i+1)*len(bet_type_labels)]
                for idx, btn in enumerate(btns):
                    odds_el = await btn.query_selector('span.cb-market__button-odds[data-testid="button-odds-market-board"]')
                    odds = (await odds_el.inner_text()).strip() if odds_el else None
                    rows.append({
                        'player': player_name,
                        'bet_type': bet_type_labels[idx] if idx < len(bet_type_labels) else None,
                        'odds': odds
                    })
            df = pd.DataFrame(rows)
            df = filter_df(df)
            return df
    raise Exception(f"Could not find section titled '{section_title}'")

async def extract_game_section(page, section_title):
    betting_sections = await page.query_selector_all('div.cb-subcategory[data-testid="component-builder-market"]')
    for section in betting_sections:
        section_title_el = await section.query_selector('h2.cb-collapsible-header[data-testid="collapsible-header"]')
        if not section_title_el:
            continue
        found_title = (await section_title_el.inner_text()).strip()
        if found_title.lower() == section_title.lower():
            await ensure_section_expanded(page, section_title)
            templates = await section.query_selector_all('div.cb-market__template')
            if not templates:
                raise Exception(f"No market templates found in {section_title} section.")
            # Get bet type labels (e.g., Spread, Total, Moneyline)
            bet_type_els = await templates[0].query_selector_all('div.cb-market__label.cb-market__label--text-center p.cb-market__label--truncate-strings')
            bet_type_labels = [(await el.inner_text()).strip() for el in bet_type_els]
            rows = []
            for template, team_idx in zip(templates, range(len(templates))):
                # Team name
                team_label_el = await template.query_selector('span.cb-market__label-inner.cb-market__label-inner--parlay')
                team_name = (await team_label_el.inner_text()).strip() if team_label_el else None
                # All buttons for this team
                btns = await template.query_selector_all('button.cb-market__button')
                for idx, btn in enumerate(btns):
                    points_el = await btn.query_selector('span.cb-market__button-points[data-testid="button-points-market-board"]')
                    points = (await points_el.inner_text()).strip() if points_el else None
                    odds_el = await btn.query_selector('span.cb-market__button-odds[data-testid="button-odds-market-board"]')
                    odds = (await odds_el.inner_text()).strip() if odds_el else None
                    title_el = await btn.query_selector('span.cb-market__button-title[data-testid="button-title-market-board"]')
                    title = (await title_el.inner_text()).strip() if title_el else None
                    bet_type = bet_type_labels[idx] if idx < len(bet_type_labels) else None
                    rows.append({
                        'team': team_name,
                        'bet_type': bet_type,
                        'points': points,
                        'odds': odds,
                        'title': title
                    })
            df = pd.DataFrame(rows)
            df = filter_df(df)
            return df
    raise Exception(f"Could not find section titled '{section_title}'")

async def scrape_game_sections(page, url, game_meta):
    result = {"url": url}
    for k, v in game_meta.items():
        result[k] = v
    for section_title in SECTION_TITLES:
        try:
            if section_title == "TD Scorer":
                df = await extract_td_scorer_section(page, section_title)
            elif section_title == "Game":
                df = await extract_game_section(page, section_title)
            else:
                df = await extract_section(page, section_title)
                if 'selected' in df.columns:
                    df = df.drop(columns=['selected'])
            # Store as dict (records) for easier aggregation
            result[section_title] = df.to_dict(orient='records')
        except Exception as e:
            logging.error(f"Error extracting {section_title} for {url}: {e}")
            result[section_title] = None
    return result

async def scrape_all_games_from_csv(csv_path):
    df_games = pd.read_csv(csv_path)
    results = []
    os.makedirs('server/csv_output', exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for idx, row in df_games.iterrows():
            url = row['game_url']
            game_meta = row.drop('game_url').to_dict()
            logging.info(f"Scraping game {idx+1}/{len(df_games)}: {url}")
            try:
                await page.goto(url)
                await page.wait_for_timeout(8000)
                game_result = await scrape_game_sections(page, url, game_meta)
                results.append(game_result)
                # Combine all sections into one DataFrame with a 'section' column
                section_dfs = []
                for section in SECTION_TITLES:
                    section_data = game_result.get(section)
                    if section_data is not None:
                        section_df = pd.DataFrame(section_data)
                        section_df['section'] = section
                        section_dfs.append(section_df)
                if section_dfs:
                    combined_df = pd.concat(section_dfs, ignore_index=True, sort=False)
                    # Add game metadata columns to every row
                    for meta_key, meta_val in game_meta.items():
                        combined_df[meta_key] = meta_val
                    combined_df['url'] = url
                    base_name = f"{row['date']}_{row['team1']}_vs_{row['team2']}".replace(' ', '_').replace('/', '-')
                    base_name = re.sub(r'[^A-Za-z0-9_\-]', '', base_name)
                    combined_csv_path = f"server/csv_output/{base_name}.csv"
                    combined_df.to_csv(combined_csv_path, index=False)
            except Exception as e:
                logging.error(f"Failed to scrape {url}: {e}")
                continue
        await browser.close()
    return results

async def main():
    csv_path = "server/draftkings_scraping/draftkings_nfl_games.csv"
    all_game_data = await scrape_all_games_from_csv(csv_path)
    # Flatten for DataFrame: each row is a game, columns are meta + each section as a list of dicts
    df = pd.DataFrame(all_game_data)
    print(df)
    df.to_json("draftkings_nfl_games_sections.json", orient="records", indent=2)
    df.to_pickle("draftkings_nfl_games_sections.pkl")

if __name__ == "__main__":
    asyncio.run(main()) 