import gspread
from google.oauth2.service_account import Credentials
import time


class SheetClient:
    def __init__(self, spreadsheet_id: str, creds_path: str):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(creds)
        self.sheet = client.open_by_key(spreadsheet_id).sheet1
        self.ensure_headers()

    def ensure_headers(self):
        headers = [
            "client_id",
            "name",
            "email",
            "phone",
            "address",
            "created_at",
            "updated_at",
        ]
        existing = self.sheet.row_values(1)
        if existing != headers:
            self.sheet.update("A1:G1", [headers])

    def build_index(self):
        index = {}
        rows = self.sheet.get_all_values()
        for i, row in enumerate(rows[1:], start=2):
            if row and row[0]:
                index[row[0]] = i
        return index

    def upserts(self, rows: list[dict]):
        if not rows:
            return
        index = self.build_index()
        headers = [
            "client_id",
            "name",
            "email",
            "phone",
            "address",
            "created_at",
            "updated_at",
        ]
        updates = []
        inserts = []
        for r in rows:
            values = [r.get(h, "") for h in headers]
            if r["client_id"] in index:
                updates.append((index[r["client_id"]], values))
            else:
                inserts.append(values)
        if updates:
            data = [
                {"range": f"A{row}:G{row}", "values": [vals]} for row, vals in updates
            ]
            for attempt in range(5):
                try:
                    self.sheet.batch_update(data)
                    break
                except Exception:
                    time.sleep(2**attempt)
        if inserts:
            for attempt in range(5):
                try:
                    self.sheet.append_rows(inserts, value_input_option="RAW")
                    break
                except Exception:
                    time.sleep(2**attempt)

    def ping(self) -> bool:
        try:
            self.sheet.row_values(1)
            return True
        except Exception:
            return False
