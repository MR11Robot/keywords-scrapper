# bot.py

import os
import time
import threading

from datetime import datetime
from src.services import (
    GoogleSheetsScraper,
    KeywordsManager,
    Database,
    Country
)
from .config import load_countries, BASE_DIR


# ── Shared state ─────────────────────────────────────────────────────────────
bot_running_event = threading.Event()

started_at = None
finished_at = None
current_keyword = ""
current_country = ""
current_country_progress = "N/A"


# ── Helpers ───────────────────────────────────────────────────────────────────
def _build_keywords_manager() -> KeywordsManager:
    """Create and configure the KeywordsManager with countries from JSON."""
    keywords_manager = KeywordsManager(
        row_range="Sheet1!A2:A",
        words_index=0,
        database=Database(
            name="data.db",
            keywords_table_name="keywords_collector_words"
        )
    )

    countries_data = load_countries()
    for c in countries_data:
        keywords_manager.excel.countries.append(
            Country(
                name=c["name"],
                code=c["code"],
                homepage=c["homepage"],
                inside=c["inside"],
                bottom=c["bottom"],
            )
        )

    return keywords_manager


def _process_country(country, keywords, keywords_manager, api: str) -> tuple[list, list]:
    """
    Iterate over all keywords for a single country.

    Returns:
        (keywords_failed, keywords_failed_bottom)
    """
    global current_country, current_country_progress, current_keyword

    keywords_failed = []
    keywords_failed_bottom = []
    keywords_done_count = 0

    for index, keyword in enumerate(keywords):
        if not bot_running_event.is_set():
            break

        # Rate-limit: rest every 10 keywords
        if keywords_done_count == 10:
            print("Resting for 10 seconds...")
            time.sleep(10)
            keywords_done_count = 0

        current_country = country.name
        current_country_progress = f"({index + 1}/{len(keywords)})"
        current_keyword = keyword

        keywords_related = []

        # ── Homepage ──────────────────────────────────────────────────────────
        print(f"Homepage: {keyword}")
        ok, results = keywords_manager.homepage(keyword=keyword, api=api, url=country.homepage)
        if ok and results:
            keywords_related.extend(results)
        elif not ok:
            keywords_failed.append(keyword)

        # ── Homepage + space ──────────────────────────────────────────────────
        print(f"Homepage Space: {keyword}")
        ok, results = keywords_manager.homepage(keyword=(keyword + "%20"), api=api, url=country.homepage)
        if ok and results:
            keywords_related.extend(results)
        elif not ok:
            keywords_failed.append(keyword)

        # ── Inside page ───────────────────────────────────────────────────────
        print(f"Inside Page: {keyword}")
        ok, results = keywords_manager.inside_page(keyword=keyword, api=api, url=country.inside)
        if ok and results:
            keywords_related.extend(results)
        elif not ok:
            keywords_failed.append(keyword)

        # ── Inside page + space ───────────────────────────────────────────────
        print(f"Inside Page Space: {keyword}")
        ok, results = keywords_manager.inside_page(keyword=(keyword + "%20"), api=api, url=country.inside)
        if ok and results:
            keywords_related.extend(results)
        elif not ok:
            keywords_failed.append(keyword)

        # ── Related bottom ────────────────────────────────────────────────────
        print(f"Related Bottom: {keyword}")
        ok, results = keywords_manager.related_bottom(keyword=keyword, api=api, url=country.bottom)
        if ok and results:
            keywords_related.extend(results)
        elif not ok:
            keywords_failed_bottom.append(keyword)

        # Deduplicate and write to Excel
        keywords_related = list(dict.fromkeys(keywords_related))
        for related in keywords_related:
            keywords_manager.excel.append_data(country.code, keyword.strip(), related.strip())

        keywords_done_count += 1
        print("------------------------------")

    return keywords_failed, keywords_failed_bottom


# ── Main bot loop ─────────────────────────────────────────────────────────────
def run_bot():
    global started_at, finished_at, current_keyword, current_country, current_country_progress

    bot_running_event.set()

    while bot_running_event.is_set():
        api = os.getenv("API")
        now = datetime.now()
        started_at = now.strftime("%Y/%m/%d %I:%M:%S %p")
        current_country = "Processing"
        current_country_progress = "Starting..."
        current_keyword = ""
        finished_at = "Processing"
        print(f"Started at: {started_at}")

        # ── Fetch data from Google Sheets ─────────────────────────────────────
        spreadsheet_id = os.getenv("SPREADSHEET_ID")

        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID is not set in environment variables")
        
        scraper = GoogleSheetsScraper(spreadsheet_id)
        headers, all_data = scraper.fetch_all_sheets_with_data()

        # ── Build manager (loads countries from JSON) ─────────────────────────
        keywords_manager = _build_keywords_manager()
        keywords_manager.database.delete_keywords()
        keywords_manager.database.insert_words_with_country(headers, all_data)
        keywords_manager.excel.create_sheets(headers, keywords_manager)

        # ── Process each country ──────────────────────────────────────────────
        all_failed = []
        all_failed_bottom = []

        for country in keywords_manager.excel.countries:
            keywords = keywords_manager.database.get_keywords(country.code)
            if not keywords:
                continue

            failed, failed_bottom = _process_country(country, keywords, keywords_manager, api)
            all_failed.extend(failed)
            all_failed_bottom.extend(failed_bottom)

            if not bot_running_event.is_set():
                break

        # ── Save output ───────────────────────────────────────────────────────
        keywords_manager.excel.workbook.save(
            keywords_manager.excel.output_path / keywords_manager.excel.name
        )
        keywords_manager.excel.workbook.close()
        time.sleep(1)

        # ── Report failures ───────────────────────────────────────────────────
        print(f"\nKeywords Failed To Scrape [{len(all_failed)}]")
        for i, fail in enumerate(all_failed):
            print(f"  [{i + 1}] {fail}")

        print(f"\nKeywords Failed (Bottom) [{len(all_failed_bottom)}]")
        for i, fail in enumerate(all_failed_bottom):
            print(f"  [{i + 1}] {fail}")

        # ── Reset state ───────────────────────────────────────────────────────
        now = datetime.now()
        current_keyword = "N/A"
        current_country = "N/A"
        current_country_progress = "N/A"
        finished_at = now.strftime("%Y/%m/%d %I:%M:%S %p")
        print(f"Finished at: {finished_at}")

        bot_running_event.clear()