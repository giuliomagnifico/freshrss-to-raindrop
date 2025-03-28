import requests
import os
import json
import subprocess
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from pathlib import Path

# 🔁 Assicurati di avere la versione più recente del repo
subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=True)

FRESHRSS_URL = os.getenv("FRESHRSS_URL")
FRESHRSS_USER = os.getenv("FRESHRSS_USER")
FRESHRSS_PASSWORD = os.getenv("FRESHRSS_PASSWORD")
RAINDROP_TOKEN = os.getenv("RAINDROP_TOKEN")
COLLECTION_TITLE = "RSS starred"

SYNCED_FILE = "synced.json"
IDS_TMP_FILE = ".ids.tmp"

def normalize_url(raw_url):
    parsed = urlparse(raw_url)
    query = parse_qsl(parsed.query)
    filtered = [(k, v) for k, v in query if not k.lower().startswith("utm_")]
    normalized_query = urlencode(sorted(filtered))
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', normalized_query, ''))

def login_to_freshrss():
    r = requests.post(f"{FRESHRSS_URL}/api/greader.php/accounts/ClientLogin", data={
        "Email": FRESHRSS_USER,
        "Passwd": FRESHRSS_PASSWORD
    })
    r.raise_for_status()
    return [line.split('=')[1] for line in r.text.strip().splitlines() if line.startswith('Auth=')][0]

def get_starred_articles(token):
    headers = {"Authorization": f"GoogleLogin auth={token}"}
    r = requests.get(f"{FRESHRSS_URL}/api/greader.php/reader/api/0/stream/contents/user/-/state/com.google/starred", headers=headers)
    r.raise_for_status()
    return r.json().get("items", [])

def get_raindrop_collection_id():
    r = requests

import os
print("✅ Fine main.py")
print("Contenuto .ids.tmp:")
os.system("cat .ids.tmp || echo 'File mancante'")
