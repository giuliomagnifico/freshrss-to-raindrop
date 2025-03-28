import json
from pathlib import Path
import subprocess

IDS_TMP_FILE = ".ids.tmp"
SYNCED_FILE = "synced.json"

# Verifica che esista il file temporaneo con gli ID
if not Path(IDS_TMP_FILE).exists():
    print("❌ Nessun file .ids.tmp trovato")
    exit(1)

# Carica gli ID e salva nel file JSON finale
with open(IDS_TMP_FILE) as f:
    ids = json.load(f)

with open(SYNCED_FILE, "w") as f:
    json.dump({"synced": ids}, f, indent=2)

print("✅ synced.json aggiornato")

# Aggiungi e committa il file in Git
try:
    subprocess.run(["git", "add", SYNCED_FILE], check=True)
    subprocess.run(["git", "commit", "-m", "update synced.json"], check=True)
    print("📁 synced.json aggiunto e commit fatto")
except subprocess.CalledProcessError:
    print("⚠️ Nessuna modifica da committare")
