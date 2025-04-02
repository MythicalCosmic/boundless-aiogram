import os
import logging
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")


WEBHOOK = os.getenv("WEBHOOK", "False").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")


DEBUG = os.getenv("DEBUG", "True").lower() == "true"
DEBUG_LEVEL = os.getenv("DEBUG_LEVEL", "info").upper()


LOG_DIR = "requests"
LOG_FILE = f"{LOG_DIR}/request.log"


os.makedirs(LOG_DIR, exist_ok=True)


logging.basicConfig(
    level=getattr(logging, DEBUG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ],
)

logging.info("Configuration loaded successfully.")
