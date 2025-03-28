import json
from pathlib import Path

IDS_TMP_FILE = ".ids.tmp"
SYNCED_FILE = "synced.json"

if not Path(IDS_TMP_FILE).exists():
    print("❌ Nessun file .ids.tmp trovato")
    exit(1)

with open(IDS_TMP_FILE) as f:
    ids = json.load(f)

with open(SYNCED_FILE, "w") as f:
    json.dump({"synced": ids}, f, indent=2)

print("✅ synced.json aggiornato dopo git pull")
