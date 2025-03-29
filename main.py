import os
import json
import requests

FRESHRSS_URL = os.getenv("FRESHRSS_URL")
FRESHRSS_USER = os.getenv("FRESHRSS_USER")
FRESHRSS_PASSWORD = os.getenv("FRESHRSS_PASSWORD")
RAINDROP_TOKEN = os.getenv("RAINDROP_TOKEN")

def login_freshrss():
    print("🔐 Login a FreshRSS...")
    r = requests.post(f"{FRESHRSS_URL}/api/greader.php/accounts/ClientLogin", data={
        "Email": FRESHRSS_USER,
        "Passwd": FRESHRSS_PASSWORD,
    })
    r.raise_for_status()
    sid = r.text.split("\n")[2].split("=")[1]
    print("✅ Login OK")
    return {"Authorization": f"GoogleLogin auth={sid}"}

def get_starred_articles(headers):
    print("🔎 Cerco articoli con stella...")
    r = requests.get(f"{FRESHRSS_URL}/api/greader.php/reader/api/0/stream/contents/user/-/state/com.google/starred?n=1000", headers=headers)
    r.raise_for_status()
    items = r.json().get("items", [])
    articles = [{"title": item["title"], "url": item["canonical"][0]["href"]} for item in items if "canonical" in item]
    print(f"📦 Trovati {len(articles)} articoli con stella")
    return articles

def save_to_raindrop(article):
    print(f"🔗 Provo a salvare su Raindrop: {article['url']}")
    headers = {
        "Authorization": f"Bearer {RAINDROP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "link": article["url"],
        "title": article["title"],
        "collection": {"title": "RSS starred"}
    }
    r = requests.post("https://api.raindrop.io/rest/v1/raindrop", headers=headers, data=json.dumps(data))
    if r.status_code == 200:
        print("✅ Salvato con successo")
    else:
        print(f"❌ Errore durante il salvataggio: {r.status_code} {r.text}")

def load_synced():
    if os.path.exists("synced.json"):
        with open("synced.json", "r") as f:
            return json.load(f)
    return []

def save_synced(urls):
    with open("synced.json", "w") as f:
        json.dump(urls, f, indent=2)

def main():
    headers = login_freshrss()
    articles = get_starred_articles(headers)
    synced = load_synced()

    for article in articles:
        # Forza il salvataggio per test
        print(f"🔁 Forzo salvataggio: {article['url']}")
        save_to_raindrop(article)
        if article["url"] not in synced:
            synced.append(article["url"])

    save_synced(synced)
    print("✅ Fine main.py")
    print("Contenuto synced.json:")
    print(json.dumps(synced, indent=2))

if __name__ == "__main__":
    main()
