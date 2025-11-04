import re
import os
from dotenv import load_dotenv

load_dotenv()

allowed_users_str = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = [int(uid) for uid in allowed_users_str.split(",") if uid.strip()] if allowed_users_str else []

URL_PATTERN = re.compile(
    r'(?:http[s]?://)?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.[a-z]{2,}'
)
QUALITY = "best[height<=240]/best[height<=360]/best[height<=480]/best"
# User-Agent y headers realistas para reducir retos anti-bot en IPs de cloud
USER_AGENT = (
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
  "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"
)
HTTP_HEADERS = {
  'User-Agent': USER_AGENT,
  'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
  'Referer': 'https://www.youtube.com/'
}

# Ruta de cookies: intenta `cookies.txt`; si no existe, usa `cookies.txt.bak` si está presente
_base_dir = os.path.dirname(os.path.abspath(__file__))
_cookies_candidates = [
  os.path.join(_base_dir, 'cookies.txt'),
  os.path.join(_base_dir, 'cookies.txt.bak'),
]
COOKIES_FILE = next((p for p in _cookies_candidates if os.path.exists(p)), None)

YT_DLP_OPTIONS = {
  'format': QUALITY,
  'outtmpl': '%(title)s.%(ext)s',
  'quiet': True,
  'no_warnings': True,
  'noprogress': True,
  'nocheckcertificate': True,
  # Headers y red
  'user_agent': USER_AGENT,
  'http_headers': HTTP_HEADERS,
  'force_ipv4': True,  # ayuda en algunos proveedores donde IPv6 tiene más retos
  'geo_bypass': True,
  # Cookies si existen
  'cookiefile': COOKIES_FILE,
  'extractor_args': {
    'youtube': {
      'player_client': ['ios', 'android', 'mweb'],
      'skip': ['webpage'],
    }
  }
}