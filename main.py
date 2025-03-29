import os
import json
import requests
from urllib.parse import urlparse, parse_qs, urlunparse

FRESHRSS_URL = os.environ["FRESHRSS_URL"]
FRESHRSS_USER = os.environ["FRESHRSS_USER"]
FRESHRSS_PASSWORD = os.environ["FRESHRSS_PASSWORD"]
RAINDROP_TOKEN = os.environ["RAINDROP_TOKEN"]

def login():
    print("🔐 Login a FreshRSS...")
    response = requests.post(f"{FRESHRSS_URL}/api/greader.php/accounts/ClientLogin", data={
        "Email": FRESHRSS_USER,
        "Passwd": FRESHRSS_PASSWORD,
    })
    response.raise_for_status()
    sid = response.text.split("Auth=")[-1].strip()
    print("✅ Login OK")
    return sid

def fetch_starred_articles(sid):
    print("🔎 Cerco articoli con stella...")
    headers = {"Authorization": f"GoogleLogin auth={sid}"}
    response = requests.get(f"{FRESHRSS_URL}/api/greader.php/reader/api/0/stream/contents/user/-/state/com.google/starred", headers=headers)
    response.raise_for_status()
    items = response.json().get("items", [])
    print(f"📦 Trovati {len(items)} articoli con stella")
    return items

def normalize_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    clean_query = {k: v for k, v in query.items() if not k.startswith("utm_")}
    new_query = "&".join([f"{k}={v[0]}" for k, v in clean_query.items()])
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

def load_synced():
    if os.path.exists("synced.json"):
        with open("synced.json", "r") as f:
            return set(json.load(f))
    return set()

def save_synced(urls):
    with open("synced.json", "w") as f:
        json.dump(sorted(urls), f, indent=2)
    print("💾 synced.json aggiornato")

def main():
    sid = login()
    items = fetch_starred_articles(sid)
    old_urls = load_synced()
    new_urls = {normalize_url(item["alternate"][0]["href"]) for item in items}
    all_urls = old_urls.union(new_urls)
    save_synced(all_urls)
    print("✅ Fine main.py")
    print("Contenuto synced.json:")
    print(json.dumps(sorted(all_urls), indent=2))

if __name__ == "__main__":
    main()
