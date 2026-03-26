# google_sheets.py

import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

from src.config import BASE_DIR

SERVICE_ACCOUNT_FILE = BASE_DIR / os.getenv("GOOGLE_CREDENTIALS", "keys.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

class GoogleSheetsScraper:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.sheets_data = {}
        self.sheets_headers = {}

    def fetch_all_sheets_with_data(self):
        

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        metadata = sheet.get(spreadsheetId=self.spreadsheet_id).execute()
        sheets = metadata.get('sheets', [])
        for sheet_meta in sheets:
            sheet_name = sheet_meta['properties']['title']
            print(f"Fetching data from sheet: {sheet_name}")
            
            range_to_fetch = f"{sheet_name}"
            result = service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range=range_to_fetch
            ).execute()
            data = result.get('values', [])
            
            if data:
                header = [cell.strip() for cell in data[0] if cell.strip()]
                self.sheets_headers[sheet_name] = header
                
                self.sheets_data[sheet_name] = data[1:]
                # self.sheets_data[sheet_name] = data[1:3]
            else:
                self.sheets_headers[sheet_name] = []
                self.sheets_data[sheet_name] = []

        return self.sheets_headers, self.sheets_data