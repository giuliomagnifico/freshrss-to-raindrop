
import os
import json
import requests

FRESHRSS_URL = os.environ["FRESHRSS_URL"]
FRESHRSS_USER = os.environ["FRESHRSS_USER"]
FRESHRSS_PASSWORD = os.environ["FRESHRSS_PASSWORD"]
RAINDROP_TOKEN = os.environ["RAINDROP_TOKEN"]

def login_freshrss():
    print("🔐 Login a FreshRSS...")
    r = requests.post(f"{FRESHRSS_URL}/api/greader.php/accounts/ClientLogin", data={
        "Email": FRESHRSS_USER,
        "Passwd": FRESHRSS_PASSWORD,
    })
    if r.status_code != 200:
        raise Exception("Errore login FreshRSS")
    print("✅ Login OK")
    return r.text.strip()

def get_starred_articles(auth_token):
    print("🔎 Cerco articoli con stella...")
    headers = {
        "Authorization": f"GoogleLogin auth={auth_token}",
    }
    r = requests.get(f"{FRESHRSS_URL}/api/greader.php/reader/api/0/stream/contents/user/-/state/com.google/starred", headers=headers)
    items = r.json().get("items", [])
    print(f"📦 Trovati {len(items)} articoli con stella")
    return items

def save_to_raindrop(article):
    url = article.get("canonical", [{}])[0].get("href") or article.get("alternate", [{}])[0].get("href")
    title = article.get("title", "Senza titolo")
    if not url:
        print("⚠️ Nessun URL trovato per:", title)
        return

    headers = {
        "Authorization": f"Bearer {RAINDROP_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "link": url,
        "title": title,
        "tags": ["FreshRSS"],
    }

    print(f"💾 Salvo su Raindrop: {url}")
    r = requests.post("https://api.raindrop.io/rest/v1/raindrop", headers=headers, json=data)
    print(f'🔍 Raindrop response: {r.status_code} {r.text}')
    print("📡 Risposta Raindrop:", r.status_code, r.text)

def main():
    auth_token = login_freshrss()
    articles = get_starred_articles(auth_token)

    if Path("synced.json").exists():
        with open("synced.json") as f:
            synced_urls = json.load(f)
    else:
        synced_urls = []

    for article in articles:
        url = article.get("canonical", [{}])[0].get("href") or article.get("alternate", [{}])[0].get("href")
        if not url:
            continue
        if url not in synced_urls:
            print(f"✨ Nuovo articolo trovato: {url}")
            save_to_raindrop(article)
            synced_urls.append(url)

    with open("synced.json", "w") as f:
        json.dump(synced_urls, f, indent=2, ensure_ascii=False)

    print("✅ Fine main.py")
    print("Contenuto synced.json:")
    print(json.dumps(synced_urls, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
