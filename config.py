# Config

from pathlib import Path

SERVER_ADDR = ('', 8000)
PATH_WEB=Path("web/").resolve()
PATH_LOG="boop.log"
PATH_PEM="private_key.pem"

SERVER_KEY=Path("applicationServerKey").read_text().strip()
SERVER_URL="https://boop.narm.me/"
ADMIN_EMAIL="gaurav@gauravmanek.com"

CLIENT_MANAGER="clients.pickle"
PUSHER_MANAGER="pushers.pickle"
MAX_CLIENTS=20