# Keywords Scrapper 🔍
A scheduled web scraping bot that automatically collects keyword data across multiple countries and exports the results to Excel. Built as part of the [django-coupons](https://github.com/MR11Robot/django-coupons) ecosystem.

---

## What It Does
- Reads a list of **keywords and countries** to scrape
- Scrapes keyword data for each country combination
- Saves results and exports to **Excel**
- Runs automatically every **Thursday at 00:00** via a built-in scheduler
- Exposes a **REST API** to start/stop the bot and download reports

---

## Project Structure
```
├── app.py                  # Flask app & scheduler
├── src/
│   ├── bot.py              # Core bot logic & threading
│   └── config.py           # Paths & environment config
├── countries.json          # List of target countries
└── output/                 # Generated Excel files
    └── Keywords_Report.xlsx
```

---

## Requirements
- Python 3.14+
- [Poetry](https://python-poetry.org/)

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
  "started_at": "2026-03-26T00:00:00",
  "current_keyword": "example keyword",
  "current_country": "Egypt",
  "current_country_progress": 42
}
```

---

## Part of a Larger System
This bot is one of three automation tools managed by [django-coupons](https://github.com/MR11Robot/django-coupons), a Django dashboard that controls and monitors all bots from a single interface.

---

## License
MIT