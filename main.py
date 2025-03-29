
import os
import json
import requests
from urllib.parse import urljoin

FRESHRSS_URL = os.getenv("FRESHRSS_URL")
FRESHRSS_USER = os.getenv("FRESHRSS_USER")
FRESHRSS_PASSWORD = os.getenv("FRESHRSS_PASSWORD")
RAINDROP_TOKEN = os.getenv("RAINDROP_TOKEN")
COLLECTION_ID = "rss-starred"

LOGIN_ENDPOINT = "/api/greader.php"
STREAM_ITEMS_ENDPOINT = "/api/greader.php/reader/api/0/stream/items/ids"
GET_ITEM_ENDPOINT = "/api/greader.php/reader/api/0/stream/contents/user/-/state/com.google/starred"

session = requests.Session()
synced_file = "synced.json"

def login():
    print("🔐 Login a FreshRSS...")
    r = session.post(urljoin(FRESHRSS_URL, LOGIN_ENDPOINT), data={
        "email": FRESHRSS_USER,
        "passwd": FRESHRSS_PASSWORD,
        "client": "Client_FreshRSS",
        "accountType": "HOSTED",
        "service": "reader"
    })
    if r.status_code != 200:
        raise Exception("Login fallito!")
    print("✅ Login OK")

def get_starred_items():
    print("🔎 Cerco articoli con stella...")
    r = session.get(urljoin(FRESHRSS_URL, GET_ITEM_ENDPOINT), params={
        "output": "json",
        "n": 1000
    })
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])
    print(f"📦 Trovati {len(items)} articoli con stella")
    return items

def load_synced():
    if not Path(synced_file).exists():
        return set()
    with open(synced_file, "r") as f:
        return set(json.load(f))

def save_synced(urls):
    with open(synced_file, "w") as f:
        json.dump(list(urls), f, indent=2)

def save_to_raindrop(url, title):
    headers = {
        "Authorization": f"Bearer {RAINDROP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "link": url,
        "title": title,
        "collection": { "title": COLLECTION_ID }
    }
    r = requests.post("https://api.raindrop.io/rest/v1/raindrop", headers=headers, json=data)
    if r.status_code not in [200, 201]:
        print(f"❌ Errore nel salvataggio su Raindrop: {url}")
    else:
        print(f"✅ Salvato su Raindrop: {url}")

def main():
    login()
    items = get_starred_items()
    synced = load_synced()
    new_synced = set(synced)

    for item in items:
        url = item.get("alternate", [{}])[0].get("href")
        title = item.get("title", "(senza titolo)")
        if not url:
            continue
        if url in synced:
            print(f"🔁 Già sincronizzato: {url}")
            continue
        save_to_raindrop(url, title)
        new_synced.add(url)

    save_synced(new_synced)
    print("✅ Fine main.py")
    print("Contenuto synced.json:")
    print(json.dumps(list(new_synced), indent=2))

if __name__ == "__main__":
    main()
