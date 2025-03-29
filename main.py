
import os
import json
import requests

FRESHRSS_URL = os.getenv("FRESHRSS_URL")
FRESHRSS_USER = os.getenv("FRESHRSS_USER")
FRESHRSS_PASSWORD = os.getenv("FRESHRSS_PASSWORD")
RAINDROP_TOKEN = os.getenv("RAINDROP_TOKEN")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "FreshRSS to Raindrop Sync"})

def login_to_freshrss():
    print("🔐 Login a FreshRSS...")
    data = {
        "email": FRESHRSS_USER,
        "password": FRESHRSS_PASSWORD
    }
    resp = SESSION.post(f"{FRESHRSS_URL}/i", data=data, allow_redirects=False)
    if resp.status_code != 302:
        raise Exception("Login fallito")
    print("✅ Login OK")

def get_starred_articles():
    print("🔎 Cerco articoli con stella...")
    resp = SESSION.get(f"{FRESHRSS_URL}/api/greader.php/reader/api/0/starred?output=json")
    resp.raise_for_status()
    data = resp.json()
    articles = []
    for item in data.get("items", []):
        if "alternate" in item and len(item["alternate"]) > 0:
            articles.append({
                "url": item["alternate"][0]["href"],
                "title": item["title"]
            })
    print(f"📦 Trovati {len(articles)} articoli con stella")
    return articles

def add_to_raindrop(url, title):
    print(f"📤 Provo ad aggiungere a Raindrop: {url}")
    resp = requests.post(
        "https://api.raindrop.io/rest/v1/raindrop",
        headers={"Authorization": f"Bearer {RAINDROP_TOKEN}"},
        json={"link": url, "title": title, "collection": {"$title": "RSS starred"}}
    )
    print(f"🔁 Status code: {resp.status_code}")
    print(f"📬 Response body: {resp.text}")
    if resp.status_code >= 300:
        raise Exception(f"Errore da Raindrop: {resp.status_code} {resp.text}")

def main():
    login_to_freshrss()
    articles = get_starred_articles()
    synced = []

    if os.path.exists("synced.json"):
        with open("synced.json", "r") as f:
            synced = json.load(f)

    for article in articles:
        print(f"📰 Articolo: {article['title']} - {article['url']}")

        if article["url"] in synced:
            print("⏩ Già sincronizzato, salto.")
            continue

        try:
            add_to_raindrop(article["url"], article["title"])
            synced.append(article["url"])
            print("✅ Aggiunto a Raindrop!")
        except Exception as e:
            print(f"❌ Errore durante sync: {e}")

    with open("synced.json", "w") as f:
        json.dump(synced, f, indent=2)

    print("✅ Fine main.py")
    print("Contenuto synced.json:")
    print(json.dumps(synced, indent=2))

if __name__ == "__main__":
    main()
