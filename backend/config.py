from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl
from pathlib import Path
import os

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    stel_base_url: HttpUrl
    stel_api_key: str
    stel_page_size: int = Field(200, ge=1)
    db_path: str = str(BASE_DIR / "tekno.db")
    sheets_spreadsheet_id: str
    google_application_credentials: str
    sync_interval_seconds: int = Field(60, ge=1)
    backend_host: str = "0.0.0.0"
    backend_port: int = Field(8000, ge=1)


def load_settings() -> Settings:
    return Settings(
        stel_base_url=os.getenv("STEL_BASE_URL", "https://app.stelorder.com/app"),
        stel_api_key=os.getenv("STEL_API_KEY", ""),
        stel_page_size=int(os.getenv("STEL_PAGE_SIZE", "200")),
        db_path=os.getenv("DB_PATH", str(BASE_DIR / "tekno.db")),
        sheets_spreadsheet_id=os.getenv("SHEETS_SPREADSHEET_ID", ""),
        google_application_credentials=os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS", "./service_account.json"
        ),
        sync_interval_seconds=int(os.getenv("SYNC_INTERVAL_SECONDS", "60")),
        backend_host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        backend_port=int(os.getenv("BACKEND_PORT", "8000")),
    )


settings = load_settings()
