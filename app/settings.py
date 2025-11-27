import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

DEFAULT_DB_PATH = INSTANCE_DIR / "app.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ECHO_SQL = os.getenv("ECHO_SQL", "0") == "1"
