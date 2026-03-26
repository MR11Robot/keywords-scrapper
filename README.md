# Keywords Scrapper 🔍
A scheduled web scraping bot that automatically collects keyword suggestions from Google across multiple countries and exports the results to Excel. Built as part of the [django-coupons](https://github.com/MR11Robot/django-coupons) ecosystem.

---

## What It Does
- Reads **keywords and target countries** from **Google Sheets**
- For each keyword, scrapes Google suggestions using **3 methods**:
  - **Homepage** — autocomplete suggestions from the Google homepage
  - **Inside Page** — suggestions from Google's internal search page
  - **Related Bottom** — related searches at the bottom of results (via **ScrapeOps proxy**)
- Deduplicates results and saves them to **SQLite**
- Exports a structured **Excel report** with each country as a sheet and each keyword as a column
- Runs automatically every **Thursday at 00:00** via a built-in scheduler
- Exposes a **REST API** to start/stop the bot and download the report

---

## Requirements
- Python 3.14+
- [Poetry](https://python-poetry.org/)
- A [ScrapeOps](https://scrapeops.io/) API key
- A Google Cloud service account with **Sheets API** access

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/MR11Robot/keywords-scrapper.git
cd keywords-scrapper
```

**2. Install dependencies**
```bash
poetry install
```

**3. Configure environment variables**

Create a `.env` file in the root:
```env
HOST=127.0.0.1
PORT=5000
DEBUG=False

API=your_scrapeops_api_key
SPREADSHEET_ID=your_google_spreadsheet_id
GOOGLE_CREDENTIALS=keys.json   # optional, defaults to keys.json
```

**4. Add Google Sheets credentials**

Place your Google service account JSON file as `keys.json` in the root directory.

**5. Configure countries**

Edit `countries.json` to define your target countries. Each entry requires:
```json
[
  {
    "name": "Egypt",
    "code": "EG",
    "homepage": "https://...",
    "inside": "https://...",
    "bottom": "https://..."
  }
]
```

---

## Running
```bash
# Default settings (from .env)
poetry run app

# Custom options
poetry run app --host 0.0.0.0 --port 8080 --debug
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/status/` | Get current bot status and progress |
| POST | `/start/` | Start the bot manually |
| POST | `/stop/` | Stop the bot |
| GET | `/download/` | Download the Excel report |

### Status Response Example
```json
{
  "status": true,
  "started_at": "2026-03-26 09:00:00 PM",
  "current_keyword": "example keyword",
  "current_country": "Egypt",
  "current_country_progress": "(5/120)"
}
```

---

## Part of a Larger System
This bot is one of three automation tools managed by [django-coupons](https://github.com/MR11Robot/django-coupons), a Django dashboard that controls and monitors all bots from a single interface.

---

## License
MIT