import os
import requests
import json

FRESHRSS_URL = os.getenv("FRESHRSS_URL")
FRESHRSS_USER = os.getenv("FRESHRSS_USER")
FRESHRSS_PASSWORD = os.getenv("FRESHRSS_PASSWORD")
RAINDROP_TOKEN = os.getenv("RAINDROP_TOKEN")
RAINDROP_COLLECTION = os.getenv("RAINDROP_COLLECTION")

HEADERS = {
    "Authorization": f"Bearer {RAINDROP_TOKEN}",
    "Content-Type": "application/json"
}

def login_to_freshrss():
    print("🔐 Login a FreshRSS...")
    login_url = f"{FRESHRSS_URL}/api/greader.php/accounts/ClientLogin?Email={FRESHRSS_USER}&Passwd={FRESHRSS_PASSWORD}"
    response = requests.get(login_url)

    if response.status_code in (200, 201):
        print("✅ Login riuscito a FreshRSS")
        return True
    else:
        print(f"❌ Errore login FreshRSS: {response.status_code} - {response.text}")
        return False

def get_starred_items():
    print("⭐ Recupero articoli con stella da FreshRSS...")
    url = f"{FRESHRSS_URL}/api/greader.php/reader/api/0/starred-items?output=json"
    response = requests.get(url, auth=(FRESHRSS_USER, FRESHRSS_PASSWORD))
    if response.status_code != 200:
        print(f"❌ Errore nel recupero articoli: {response.status_code}")
        return []
    data = response.json()
    items = data.get("items", [])
    print(f"➡️ Trovati {len(items)} articoli con stella")
    return items

def save_to_raindrop(item):
    url = "https://api.raindrop.io/rest/v1/raindrop"
    payload = {
        "link": item.get("alternate", [{}])[0].get("href", ""),
        "title": item.get("title", "Senza titolo"),
        "excerpt": item.get("summary", {}).get("content", ""),
        "collection": {"$id": int(RAINDROP_COLLECTION)}
    }
    response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
    if response.status_code == 200:
        print(f"✅ Salvato su Raindrop: {payload['title']}")
    elif response.status_code == 409:
        print(f"⚠️ Già salvato: {payload['title']}")
    else:
        print(f"❌ Errore salvataggio: {response.status_code} - {response.text}")

def main():
    if not login_to_freshrss():
        return

    items = get_starred_items()
    for item in items:
        save_to_raindrop(item)

if __name__ == "__main__":
    main()
