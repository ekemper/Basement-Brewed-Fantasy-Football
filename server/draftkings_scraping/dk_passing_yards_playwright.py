import asyncio
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
import pandas as pd
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

PASS_YARDS_SECTION_TITLE = "Pass Yards"

async def robust_click(element, page, description="element", max_retries=5):
    for attempt in range(max_retries):
        try:
            await element.scroll_into_view_if_needed()
            await element.click(timeout=5000)
            return True
        except PlaywrightError as e:
            screenshot_path = f"click_error_{description}_{attempt}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            logging.error(f"[robust_click] Attempt {attempt+1} failed for {description}: {e}. Screenshot: {screenshot_path}")
            dom_html = await page.content()
            with open(f"click_error_{description}_{attempt}.html", "w") as f:
                f.write(dom_html)
            await page.wait_for_timeout(1000)
    raise Exception(f"[robust_click] Failed to click {description} after {max_retries} attempts.")

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
    # Move to the leftmost position first
    left_arrow = await slider.query_selector('button.cb-selection-picker__left-arrow')
    right_arrow = await slider.query_selector('button.cb-selection-picker__right-arrow')
    seen = set()
    all_rows = []
    max_moves = 20  # safety to avoid infinite loop
    moves = 0
    # Move left until can't anymore
    while left_arrow and moves < max_moves:
        class_val = await left_arrow.get_attribute('class') or ''
        if 'disabled' in class_val:
            break
        try:
            await robust_click(left_arrow, page, description=f"slider-left-arrow-{player_name}")
            await slider.wait_for_selector('button.cb-selection-picker__selection--focused', timeout=1000)
        except Exception as e:
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
        # Try to move right
        if right_arrow:
            class_val = await right_arrow.get_attribute('class') or ''
            if 'disabled' in class_val:
                break
            try:
                await robust_click(right_arrow, page, description=f"slider-right-arrow-{player_name}")
                await slider.wait_for_selector('button.cb-selection-picker__selection--focused', timeout=1000)
            except Exception as e:
                logging.warning(f"Failed to click right arrow for {player_name}: {e}")
                break
        else:
            break
        moves += 1
    return all_rows

async def extract_passing_yards_section(page):
    # Find all betting sections
    betting_sections = await page.query_selector_all('div.cb-subcategory[data-testid="component-builder-market"]')
    for section in betting_sections:
        section_title_el = await section.query_selector('h2.cb-collapsible-header[data-testid="collapsible-header"]')
        if not section_title_el:
            continue
        section_title = (await section_title_el.inner_text()).strip()
        if section_title.lower() == PASS_YARDS_SECTION_TITLE.lower():
            await ensure_section_expanded(page, PASS_YARDS_SECTION_TITLE)
            # Now extract all player rows in this section
            templates = await section.query_selector_all('div.cb-market__template')
            all_rows = []
            for template in templates:
                # Player name
                player_label = await template.query_selector('div.cb-market__label--row.cb-market__label--text-left')
                player_name = None
                if player_label:
                    name_el = await player_label.query_selector('p.cb-market__label--truncate-strings')
                    if name_el:
                        player_name = (await name_el.inner_text()).strip()
                # Slider for passing yards
                slider = await template.query_selector('div.cb-market-buttons-slider .cb-selection-picker')
                if not slider:
                    logging.warning(f"No slider found for player {player_name}")
                    continue
                # Extract all options by clicking through the slider
                player_rows = await extract_all_slider_options(slider, player_name, page)
                all_rows.extend(player_rows)
            if not all_rows:
                raise Exception("No passing yards data found in the section.")
            df = pd.DataFrame(all_rows)
            # Filter out rows where odds is None or empty
            df = df[df['odds'].notnull() & (df['odds'] != '')]
            return df
    raise Exception(f"Could not find section titled '{PASS_YARDS_SECTION_TITLE}'")

async def main():
    url = "https://sportsbook.draftkings.com/event/dal-cowboys-%40-phi-eagles/32225662"
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            logging.info(f"Navigating to {url}")
            await page.goto(url)
            await page.wait_for_timeout(8000)  # ample time for JS to load
            df = await extract_passing_yards_section(page)
            print(df)
            await browser.close()
    except Exception as e:
        logging.error(f"Error in main: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 