# Config

from pathlib import Path

SERVER_ADDR = ('', 8888)
PATH_WEB=Path("web/").resolve()
PATH_LOG="boop.log"
PATH_PEM="private_key.pem"

SERVER_KEY=Path("applicationServerKey").read_text().strip()
SERVER_URL="https://boop.narm.me"
ADMIN_EMAIL="gaurav@gauravmanek.com"

CLIENT_MANAGER="clients.pickle"
PUSHER_MANAGER="pushers.pickle"
STYLE_MANAGER="style.pickle"
MAX_CLIENTS=20
MAX_DELAY=60

STYLE_IMAGE=["icons/bell{}.png".format(x) for x in range(7)]
STYLE_COLOR=["#C18F72", "#510068", "#FFBB53", "#FF6C51", "#00B0A0", "#2D393E", "#5B4F50"]
STYLE_CLASS=["style-color-{}".format(x) for x in range(7)]

AUTH_ENABLE=True
AUTH_USERNAME="gaurav"
AUTH_PASSWORD="booptwerp123"
