import requests
import os
import json

FRESHRSS_URL = os.getenv("FRESHRSS_URL")
FRESHRSS_USER = os.getenv("FRESHRSS_USER")
FRESHRSS_PASSWORD = os.getenv("FRESHRSS_PASSWORD")
RAINDROP_TOKEN = os.getenv("RAINDROP_TOKEN")
COLLECTION_TITLE = "RSS starred"

SYNCED_FILE = "synced.json"
IDS_TMP_FILE = ".ids.tmp"

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
    r = requests.get("https://api.raindrop.io/rest/v1/collections", headers={
        "Authorization": f"Bearer {RAINDROP_TOKEN}"
    })
    r.raise_for_status()
    for col in r.json()["items"]:
        if col["title"].lower() == COLLECTION_TITLE.lower():
            return col["_id"]
    raise ValueError("Collection not found")

def save_to_raindrop(collection_id, article):
    data = {
        "collection": {"$id": collection_id},
        "link": article["alternate"][0]["href"],
        "title": article["title"],
    }
    r = requests.post("https://api.raindrop.io/rest/v1/raindrop", headers={
        "Authorization": f"Bearer {RAINDROP_TOKEN}",
        "Content-Type": "application/json"
    }, json=data)
    r.raise_for_status()

def load_synced_ids():
    if os.path.exists(SYNCED_FILE):
        with open(SYNCED_FILE, "r") as f:
            return set(json.load(f).get("synced", []))
    return set()

def main():
    try:
        token = login_to_freshrss()
        articles = get_starred_articles(token)
        collection_id = get_raindrop_collection_id()
        synced_ids = load_synced_ids()
        new_synced = set(synced_ids)

        for a in articles:
            if a["id"] in synced_ids:
                continue
            save_to_raindrop(collection_id, a)
            new_synced.add(a["id"])

        with open(IDS_TMP_FILE, "w") as f:
            json.dump(list(new_synced), f, indent=2)

        print(f"✅ Sincronizzati {len(new_synced) - len(synced_ids)} nuovi articoli")

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
