# FreshRSS → Raindrop.io Sync

Questo script sincronizza automaticamente gli articoli stellati da FreshRSS su Raindrop.io, usando GitHub Actions.

## 🔧 Variabili richieste (come secret)

- `FRESHRSS_URL` → es: `https://tuo-freshrss.pikapod.net`
- `FRESHRSS_USER` → username FreshRSS
- `FRESHRSS_PASSWORD` → password FreshRSS
- `RAINDROP_TOKEN` → token API personale da [raindrop.io/settings/integrations](https://raindrop.io/settings/integrations)

## 🚀 Come usarlo

1. Crea un nuovo repository GitHub
2. Carica questi file
3. Aggiungi i segreti in Settings > Secrets > Actions
4. Esegui manualmente oppure ogni 6 ore via cron
