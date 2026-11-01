"""Application configuration for Campus AI Backend."""

import os
from pathlib import Path
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parents[1]
    CAMPUS_ROOT = Path(__file__).resolve().parents[2]
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    BASE_DIR = Path(__file__).resolve().parents[1]
    CAMPUS_ROOT = Path(__file__).resolve().parents[2]

# Ensure robust database path pointing to CAMPUS AI/campusai.db
DEFAULT_DB_FILE = CAMPUS_ROOT / "campusai.db"
if not DEFAULT_DB_FILE.exists() and (BASE_DIR / "campusai.db").exists():
    DEFAULT_DB_FILE = BASE_DIR / "campusai.db"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_FILE.as_posix()}"


class Settings(BaseModel):
    PROJECT_NAME: str = "Campus AI Backend"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "campusai-super-secret-dev-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # SQLite Database configuration (enforced SQLite as requested)
    DATABASE_URL: str = os.getenv("DATABASE_URL") or DEFAULT_DB_URL

    # Allowed CORS Origins (allows Android emulator 10.0.2.2, localhost, and local network)
    CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://10.0.2.2",
        "http://10.0.2.2:8000",
        "*",
    ]

    # File storage directory for notes
    STORAGE_DIR: Path = BASE_DIR / "storage"

    # External API Keys (Loaded from .env)
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    NOTION_API_KEY: str | None = os.getenv("NOTION_API_KEY")
    NOTION_DATABASE_ID: str | None = os.getenv("NOTION_DATABASE_ID")
    GMAIL_CLIENT_ID: str | None = os.getenv("GMAIL_CLIENT_ID")
    GMAIL_CLIENT_SECRET: str | None = os.getenv("GMAIL_CLIENT_SECRET")
    GMAIL_REFRESH_TOKEN: str | None = os.getenv("GMAIL_REFRESH_TOKEN")

    # Google Calendar & Gmail OAuth 2.0 Configuration
    GOOGLE_CALENDAR_CLIENT_ID: str | None = os.getenv("GOOGLE_CALENDAR_CLIENT_ID")
    GOOGLE_CALENDAR_CLIENT_SECRET: str | None = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")
    GOOGLE_CALENDAR_REDIRECT_URI: str = (
        os.getenv("GOOGLE_CALENDAR_REDIRECT_URI") or "http://localhost:8000/api/v1/calendar/callback"
    )
    GOOGLE_CALENDAR_SCOPE: str = "https://www.googleapis.com/auth/calendar.readonly"
    GMAIL_SCOPE: str = "https://www.googleapis.com/auth/gmail.readonly"
    GOOGLE_COMBINED_SCOPE: str = "https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/gmail.readonly"



# Automatically discover client_secret.json or credentials.json if present
for secret_filename in ["client_secret.json", "credentials.json", "oauth_credentials.json"]:
    secret_path = BASE_DIR / secret_filename
    if secret_path.exists():
        try:
            import json
            with open(secret_path, "r", encoding="utf-8") as f:
                secret_data = json.load(f)
            web_cfg = secret_data.get("web") or secret_data.get("installed") or secret_data
            if "client_id" in web_cfg and not os.getenv("GOOGLE_CALENDAR_CLIENT_ID"):
                os.environ["GOOGLE_CALENDAR_CLIENT_ID"] = web_cfg["client_id"]
                os.environ["GMAIL_CLIENT_ID"] = web_cfg["client_id"]
            if "client_secret" in web_cfg and not os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET"):
                os.environ["GOOGLE_CALENDAR_CLIENT_SECRET"] = web_cfg["client_secret"]
                os.environ["GMAIL_CLIENT_SECRET"] = web_cfg["client_secret"]
            if "redirect_uris" in web_cfg and web_cfg["redirect_uris"]:
                os.environ["GOOGLE_CALENDAR_REDIRECT_URI"] = web_cfg["redirect_uris"][0]
        except Exception:
            pass
        break

settings = Settings(
    GOOGLE_CALENDAR_CLIENT_ID=os.getenv("GOOGLE_CALENDAR_CLIENT_ID"),
    GOOGLE_CALENDAR_CLIENT_SECRET=os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET"),
    GOOGLE_CALENDAR_REDIRECT_URI=os.getenv("GOOGLE_CALENDAR_REDIRECT_URI", "http://localhost:8000/api/v1/calendar/callback"),
    GMAIL_CLIENT_ID=os.getenv("GMAIL_CLIENT_ID"),
    GMAIL_CLIENT_SECRET=os.getenv("GMAIL_CLIENT_SECRET"),
)

# Ensure SQLite is used if DATABASE_URL starts with postgresql or is relative
if not settings.DATABASE_URL.startswith("sqlite") or settings.DATABASE_URL.startswith("sqlite:///."):
    settings.DATABASE_URL = DEFAULT_DB_URL

settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
