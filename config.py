# Config

from pathlib import Path

SERVER_ADDR = ('', 8000)
PATH_WEB=Path("web/").resolve()
PATH_LOG="boop.log"

SERVER_KEY=Path("applicationServerKey").read_text().strip()
SERVER_URL="boop.narm.me"

REGISTRATION_FILE="clients.pickle"
MAX_CLIENTS=20