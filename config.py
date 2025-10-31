import re
import os
from dotenv import load_dotenv

load_dotenv()

allowed_users_str = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = [int(uid) for uid in allowed_users_str.split(",") if uid.strip()] if allowed_users_str else []

URL_PATTERN = re.compile(
    r'(?:http[s]?://)?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.[a-z]{2,}'
)

# YT-DLP Options
QUALITY = "best[height<=240]/best[height<=360]/best[height<=480]/best"

# Ruta absoluta al archivo cookies.txt
COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

YT_DLP_OPTIONS = {
  'format': QUALITY,
  'outtmpl': '%(title)s.%(ext)s',
  'quiet': True,
  'no_warnings': True,
  'noprogress': True,
  'nocheckcertificate': True,
  'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
  'ignoreerrors': False,  # No ignorar errores reales
  'extractor_args': {
    'youtube': {
      'player_client': ['ios', 'android', 'mweb'],
      'skip': ['webpage'],
    }
  }
}