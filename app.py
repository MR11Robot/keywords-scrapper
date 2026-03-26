# app.py

import json
import os
import threading
import argparse
import schedule

from collections import OrderedDict
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, send_file

import src.bot as bot_module
from src.bot import bot_running_event, run_bot
from src.config import BASE_DIR



load_dotenv()

app = Flask(__name__)


# ── Scheduler ─────────────────────────────────────────────────────────────────
def start_scheduled_bot():
    if not bot_running_event.is_set():
        print("Starting scheduled bot...")
        threading.Thread(target=run_bot).start()
    else:
        print("Bot is already running, skipping scheduled run.")


def run_scheduler():
    while True:
        schedule.run_pending()
        import time; time.sleep(1)


schedule.every().thursday.at("00:00").do(start_scheduled_bot)


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/status/", methods=["GET"])
def get_bot_status():
    status_data = OrderedDict([
        ("status", bot_running_event.is_set()),
        ("started_at", bot_module.started_at),
        ("current_keyword", bot_module.current_keyword),
        ("current_country", bot_module.current_country),
        ("current_country_progress", bot_module.current_country_progress),
    ])

    if not bot_running_event.is_set():
        status_data["finished_at"] = bot_module.finished_at

    return Response(json.dumps(status_data), mimetype="application/json")


@app.route("/start/", methods=["POST"])
def start_bot():
    if bot_running_event.is_set():
        return jsonify({"message": "Bot is already running"}), 400

    bot_running_event.set()
    threading.Thread(target=run_bot).start()
    return jsonify({"message": "Bot started successfully"}), 200


@app.route("/stop/", methods=["POST"])
def stop_bot():
    if not bot_running_event.is_set():
        return jsonify({"message": "Bot is already stopped"}), 400

    bot_running_event.clear()
    return jsonify({"message": "Bot stopped successfully"}), 200


@app.route("/download/", methods=["GET"])
def download_excel():
    file_path = BASE_DIR / "output" / "Keywords_Report.xlsx"
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, as_attachment=True)




def main():
    parser = argparse.ArgumentParser(description="Run Flask App")

    parser.add_argument("--host", type=str, help="Host to run the server on")
    parser.add_argument("--port", type=int, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    host = args.host or os.getenv("HOST", "127.0.0.1")
    port = args.port or int(os.getenv("PORT", 5000))
    debug = args.debug or os.getenv("DEBUG", "False").lower() == "true"

    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    app.run(debug=debug, host=host, port=port)

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()