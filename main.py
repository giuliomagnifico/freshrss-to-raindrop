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
    print("🔐 Login a FreshRSS...")
    r = requests.post(f"{FRESHRSS_URL}/api/greader.php/accounts/ClientLogin", data={
        "Email": FRESHRSS_USER,
        "Passwd": FRESHRSS_PASSWORD
    })
    r.raise_for_status()
    token = [line.split('=')[1] for line in r.text.strip().splitlines() if line.startswith('Auth=')][0]
    print("✅ Login OK")
    return token

def get_starred_articles(token):
    print("🔎 Cerco articoli con stella...")
    headers = {"Authorization": f"GoogleLogin auth={token}"}
    r = requests.get(f"{FRESHRSS_URL}/api/greader.php/reader/api/0/stream/contents/user/-/state/com.google/starred", headers=headers)
    r.raise_for_status()
    items = r.json().get("items", [])
    print(f"📦 Trovati {len(items)} articoli con stella")
    return items

def get_raindrop_collection_id():
    print("📁 Recupero ID collezione Raindrop...")
    headers = {"Authorization": f"Bearer {RAINDROP_TOKEN}"}
    r = requests.get("https://api.raindrop.io/rest/v1/collections", headers=headers)
    r.raise_for_status()
    for collection in r.json().get("items", []):
        if collection.get("title") == COLLECTION_TITLE:
            print(f"✅ Collezione trovata: {COLLECTION_TITLE}")
            return collection["_id"]
    raise Exception(f"Collezione '{COLLECTION_TITLE}' non trovata")

def main():
    token = login_to_freshrss()
    articles = get_starred_articles(token)

    ids = []
    Path(IDS_TMP_FILE).unlink(missing_ok=True)

    with open(IDS_TMP_FILE, "w") as f:
        for article in articles:
            url = article.get("canonical", [{}])[0].get("href")
            if not url:
                continue
            norm_url = normalize_url(url)
            ids.append(norm_url)
            f.write(norm_url + "\n")

    print("✅ Fine main.py")
    print("Contenuto .ids.tmp:")
    os.system(f"cat {IDS_TMP_FILE} || echo 'File mancante'")

if __name__ == "__main__":
    main()
