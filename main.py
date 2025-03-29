import os
import json
import requests
from urllib.parse import urljoin

FRESHRSS_URL = os.environ['FRESHRSS_URL']
FRESHRSS_USER = os.environ['FRESHRSS_USER']
FRESHRSS_PASSWORD = os.environ['FRESHRSS_PASSWORD']
RAINDROP_TOKEN = os.environ['RAINDROP_TOKEN']

SESSION = requests.Session()

SYNCED_FILE = "synced.json"


def login_to_freshrss():
    print("\U0001F510 Login a FreshRSS...")
    resp = SESSION.post(
        urljoin(FRESHRSS_URL, "/api/greader.php/accounts/ClientLogin"),
        data={"Email": FRESHRSS_USER, "Passwd": FRESHRSS_PASSWORD},
    )
    if resp.status_code == 200:
        print("✅ Login OK")
        return True
    else:
        print(f"❌ Login fallito: {resp.status_code} - {resp.text}")
        return False


def get_starred_articles():
    print("\U0001F50E Cerco articoli con stella...")
    api_url = urljoin(FRESHRSS_URL, f"/api/greader.php/reader/api/0/stream/contents/user/-/state/com.google/starred?n=1000")
    headers = {"Authorization": f"GoogleLogin auth={FRESHRSS_PASSWORD}"}
    response = SESSION.get(api_url, headers=headers)
    response.raise_for_status()
    items = response.json().get("items", [])
    return [(item["title"], item["alternate"][0]["href"]) for item in items]


def load_synced():
    if os.path.exists(SYNCED_FILE):
        with open(SYNCED_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_synced(synced):
    with open(SYNCED_FILE, "w") as f:
        json.dump(list(synced), f, indent=2)


def add_to_raindrop(title, url):
    headers = {
        'Authorization': f'Bearer {RAINDROP_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {
        'link': url,
        'title': title,
        'collection': {'$title': 'RSS starred'},
        'tags': ['FreshRSS']
    }
    response = requests.post('https://api.raindrop.io/rest/v1/raindrop', headers=headers, json=data)
    if response.status_code == 200:
        print(f"✅ Aggiunto su Raindrop: {title}")
    else:
        print(f"❌ Errore su Raindrop per '{title}' ({url}): {response.status_code} - {response.text}")


def main():
    if not login_to_freshrss():
        return

    articles = get_starred_articles()
    print(f"\U0001F4E6 Trovati {len(articles)} articoli con stella")

    synced = load_synced()
    new_synced = set()

    for title, url in articles:
        if url in synced:
            continue
        add_to_raindrop(title, url)
        new_synced.add(url)

    save_synced(synced.union(new_synced))
    print("✅ Fine main.py")
    print("Contenuto synced.json:")
    print(json.dumps(list(synced.union(new_synced)), indent=2))


if __name__ == "__main__":
    main()
