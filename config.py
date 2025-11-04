import re
import os
from dotenv import load_dotenv

load_dotenv()

cookies_path = os.getenv("COOKIES_PATH", "cookies.txt")

allowed_users_str = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = [int(uid) for uid in allowed_users_str.split(",") if uid.strip()] if allowed_users_str else []

URL_PATTERN = re.compile(
    r'(?:http[s]?://)?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.[a-z]{2,}'
)

QUALITY = "best[height<=240]/best[height<=360]/best[height<=480]/best"

YT_DLP_OPTIONS = {
  'outtmpl': '%(title)s.%(ext)s',
  'format': QUALITY,
  'quiet': True,
  'cookiefile': cookies_path,
  'user_agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0',
  'http_headers': {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0',
      'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
      'Referer': 'https://www.youtube.com/'
  },
  'force_ipv4': True,
  'extractor_args': {
    'youtube': {
      'player_client': ['ios', 'android', 'mweb'],
      'skip': ['webpage'],
    }
  }
}