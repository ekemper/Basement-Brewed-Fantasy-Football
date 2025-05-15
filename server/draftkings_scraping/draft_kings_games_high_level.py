import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

DK_URL = "https://sportsbook.draftkings.com/leagues/football/nfl?category=game-lines&subcategory=game"
BASE_URL = "https://sportsbook.draftkings.com"

async def scrape_draftkings_nfl():
    logging.info("Entering scrape_draftkings_nfl")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(DK_URL)
        await page.wait_for_timeout(5000)

        games = []
        sections = await page.query_selector_all('table[data-testid="sportsbook-table"]')
        logging.info(f"Found {len(sections)} sportsbook-table sections")
        for section_idx, section in enumerate(sections):
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
                    i += 2
                except Exception as e:
                    logging.error(f"Error parsing section group: {e}")
                    i += 2
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