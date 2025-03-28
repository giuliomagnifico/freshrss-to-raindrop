import json

def save_synced_ids(ids, path="synced.json"):
    with open(path, "w") as f:
        json.dump({"synced": list(ids)}, f, indent=2)

if __name__ == "__main__":
    import sys
    from pathlib import Path

    synced_path = Path("synced.json")
    if not synced_path.exists():
        print("❌ Nessun file synced.json trovato")
        sys.exit(1)

    with open(synced_path) as f:
        data = json.load(f)
        ids = set(data.get("synced", []))

    save_synced_ids(ids)
    print(f"✅ synced.json aggiornato dopo il pull")
