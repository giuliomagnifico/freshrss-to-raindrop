print("🧪 Versione aggiornata di main.py in esecuzione...")

import os
import requests
import json

FRESHRSS_URL = os.environ.get("FRESHRSS_URL")
FRESHRSS_USER = os.environ.get("FRESHRSS_USER")
FRESHRSS_PASSWORD = os.environ.get("FRESHRSS_PASSWORD")
RAINDROP_TOKEN = os.environ.get("RAINDROP_TOKEN")

RAINDROP_COLLECTION = "RSS starred"
SYNCED_FILE = "synced.json"


def login_freshrss():
    print("🔐 Login a FreshRSS...")
    r = requests.post(f"{FRESHRSS_URL}/api/greader.php/accounts/ClientLogin", data={
        "Email": FRESHRSS_USER,
        "Passwd": FRESHRSS_PASSWORD
    })
    r.raise_for_status()
    sid = r.text.split("\n")[0].split("=")[1]
    print("✅ Login OK")
    return sid


def get_starred_articles(sid):
    print("🔎 Cerco articoli con stella...")
    headers = {"Authorization": f"GoogleLogin auth={sid}"}
    r = requests.get(f"{FRESHRSS_URL}/api/greader.php/reader/api/0/stream/contents/user/-/state/com.google/starred?n=1000", headers=headers)
    r.raise_for_status()
    items = r.json().get("items", [])
    print(f"📦 Trovati {len(items)} articoli con stella")
    return items


def get_already_synced():
    if not os.path.exists(SYNCED_FILE):
        return set()
    with open(SYNCED_FILE, "r") as f:
        return set(json.load(f))


def save_synced(urls):
    with open(SYNCED_FILE, "w") as f:
        json.dump(sorted(list(urls)), f, indent=2)


def save_to_raindrop(title, url):
    headers = {
        "Authorization": f"Bearer {RAINDROP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "link": url,
        "title": title,
        "collection": {"$title": RAINDROP_COLLECTION}
    }
    print(f"🔗 Salvo su Raindrop: {title} ({url})")
    r = requests.post("https://api.raindrop.io/rest/v1/raindrop", headers=headers, json=data)
    r.raise_for_status()


def main():
    sid = login_freshrss()
    items = get_starred_articles(sid)
    already_synced = get_already_synced()

    new_urls = []
    for item in items:
        url = item.get("canonical", [{}])[0].get("href")
        title = item.get("title", "Senza titolo")
        if url and url not in already_synced:
            try:
                save_to_raindrop(title, url)
                already_synced.add(url)
                new_urls.append(url)
            except Exception as e:
                print(f"❌ Errore nel salvataggio di {url}: {e}")

    save_synced(already_synced)
    print("✅ Fine main.py")
    if new_urls:
        print("📄 Nuovi articoli salvati:")
        for url in new_urls:
            print(f"- {url}")
    else:
        print("😴 Nessun nuovo articolo da salvare.")


if __name__ == "__main__":
    main()
