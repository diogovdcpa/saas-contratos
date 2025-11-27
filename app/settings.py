import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def resolve_instance_dir() -> Path:
    custom = os.getenv("INSTANCE_DIR")
    candidate = Path(custom) if custom else BASE_DIR / "instance"
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate
    except OSError:
        # Em ambiente somente leitura (ex.: Vercel), usar /tmp
        fallback = Path("/tmp/saas-contratos")
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


INSTANCE_DIR = resolve_instance_dir()
DEFAULT_DB_PATH = INSTANCE_DIR / "app.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ECHO_SQL = os.getenv("ECHO_SQL", "0") == "1"
