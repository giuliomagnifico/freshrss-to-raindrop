
import os
import json
import requests

FRESHRSS_URL = os.environ["FRESHRSS_URL"]
FRESHRSS_USER = os.environ["FRESHRSS_USER"]
FRESHRSS_PASSWORD = os.environ["FRESHRSS_PASSWORD"]
RAINDROP_TOKEN = os.environ["RAINDROP_TOKEN"]

FRESHRSS_API = f"{FRESHRSS_URL}/api/greader.php"
SYNCED_FILE = "synced.json"
COLLECTION_NAME = "RSS starred"


def login():
    print("🔐 Login a FreshRSS...")
    res = requests.post(f"{FRESHRSS_URL}/api/v1/login", data={
        "email": FRESHRSS_USER,
        "password": FRESHRSS_PASSWORD
    })
    res.raise_for_status()
    session = res.json()["session_id"]
    print("✅ Login OK")
    return {"Cookie": f"identifier={session}"}


def load_synced():
    if not Path(SYNCED_FILE).exists():
        return set()
    with open(SYNCED_FILE) as f:
        return set(json.load(f))


def save_synced(synced):
    with open(SYNCED_FILE, "w") as f:
        json.dump(list(synced), f, indent=2)
        print("Contenuto synced.json:")
        print(json.dumps(list(synced), indent=2))


def fetch_starred(headers):
    print("🔎 Cerco articoli con stella...")
    r = requests.get(FRESHRSS_API, headers=headers, params={
        "output": "json",
        "starred": "true",
        "n": 100
    })
    r.raise_for_status()
    items = r.json().get("items", [])
    print(f"📦 Trovati {len(items)} articoli con stella")
    return items


def get_collection_id():
    r = requests.get("https://api.raindrop.io/rest/v1/collections", headers={
        "Authorization": f"Bearer {RAINDROP_TOKEN}"
    })
    r.raise_for_status()
    for c in r.json()["items"]:
        if c["title"] == COLLECTION_NAME:
            return c["_id"]
    raise Exception(f"Collection '{COLLECTION_NAME}' non trovata")


def save_to_raindrop(articles):
    collection_id = get_collection_id()
    for a in articles:
        url = a["url"]
        title = a["title"]
        print(f"➡️ Salvo su Raindrop: {title} ({url})")
        requests.post("https://api.raindrop.io/rest/v1/raindrop", json={
            "collection": {"$id": collection_id},
            "link": url,
            "title": title
        }, headers={
            "Authorization": f"Bearer {RAINDROP_TOKEN}"
        })


def main():
    headers = login()
    starred = fetch_starred(headers)
    synced = load_synced()

    new_articles = [a for a in starred if a["url"] not in synced]

    if new_articles:
        save_to_raindrop(new_articles)  # 🧩 <-- questa era la riga mancante

    synced.update(a["url"] for a in new_articles)
    save_synced(synced)
    print("✅ Fine main.py")


if __name__ == "__main__":
    main()
