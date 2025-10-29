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

YT_DLP_OPTIONS = {
  'format': QUALITY,
  'outtmpl': '%(title)s.%(ext)s',
  'quiet': True,
  'no_warnings': True,
  'nocheckcertificate': True,
  'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
  'http_headers': {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Sec-Fetch-Mode': 'navigate'
  },
  'extractor_args': {
    'youtube': {
      'player_client': ['android', 'web'],
      'skip': ['hls', 'dash']
    }
  }
}