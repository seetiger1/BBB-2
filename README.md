# 🏊 Berliner Bäder – Öffnungszeiten

Eine schlanke Web-Anwendung zur Anzeige von aktuellen Öffnungszeiten aller Berliner Schwimm- und Hallenbäder (BBB). Die Daten werden automatisch täglich vom Portal berlinerbaeder.de gescraped.

**Live-Demo:** [https://seetiger1.github.io/BBB-2/](https://seetiger1.github.io/BBB-2/)

---

## 🎯 Features

- ✨ **Moderne UI** – Dark Mode, responsive Design, Echtzeit-Favoriten
- 🏊 **Alle Bäder im Überblick** – Sommerbäder & Hallenbäder sortiert
- ⭐ **Favoriten-System** – Speichert deine Lieblingsbäder lokal
- 📱 **Responsive** – Desktop, Tablet, Handy
- 🔄 **Automatisch aktualisiert** – Täglich via GitHub Actions
- 🏷️ **Detaillierte Labels** – „Eingeschränkte Wasserfläche", Schulbetrieb, etc.
- 🔍 **Filterbar** – Nach Typ (Sommerbad/Hallenbad) oder Favoriten

---

## 📦 Tech-Stack

| Komponente | Details |
|-----------|---------|
| **Frontend** | HTML5 + CSS3 + Vanilla JavaScript (38 KB single file) |
| **Backend** | Python 3.12 + BeautifulSoup4 + requests |
| **Hosting** | GitHub Pages (`docs/` oder `gh-pages` branch) |
| **Automation** | GitHub Actions – täglicher Scrape um 02:00 UTC |
| **Datenformat** | JSON (statisch) |

---

## 🗂️ Projektstruktur

```
BBB-2/
├── index.html              # Single-Page-App (Frontend + JS)
├── requirements.txt        # Python-Dependencies
├── data/
│   └── pools.json         # Gescrapte Schwimmbad-Daten (~50 KB)
├── scraper/
│   └── scrape_pools.py    # Python Scraper (Web-Scraping + Detail-Anreicherung)
└── .github/workflows/
    └── scrape.yml         # GitHub Actions Workflow
```

### Frontend → Backend Flow

```
index.html (lädt JSON)
    ↓
data/pools.json (statische Daten)
    ↑ (täglich aktualisiert von)
.github/workflows/scrape.yml (GitHub Actions)
    ↑
scraper/scrape_pools.py (scrapte berlinerbaeder.de)
```

---

## 🚀 Quickstart

### Option 1: Lokal entwickeln

```bash
# 1. Repository klonen
git clone https://github.com/seetiger1/BBB-2.git
cd BBB-2

# 2. Python-Dependencies installieren
pip install -r requirements.txt

# 3. Daten scrapen (aktualisiert data/pools.json)
python scraper/scrape_pools.py

# 4. Lokalen Server starten und index.html öffnen
python -m http.server 8000
# Öffne: http://localhost:8000
```

### Option 2: Live-Version nutzen

Einfach die GitHub Pages URL öffnen:  
**https://seetiger1.github.io/BBB-2/**

---

## 🔧 Kommandos

### Daten neu scrapen

```bash
# Standard: Vollständiges Scraping (inkl. Detail-Pages für Labels)
python scraper/scrape_pools.py

# Schneller: Nur Übersichtsseite (ohne Detail-Labels)
python scraper/scrape_pools.py --skip-details

# In Custom-Pfad speichern
python scraper/scrape_pools.py --output /custom/path/pools.json
```

### Workflow manuell triggern

Gehe zu: **GitHub → Actions → "Scrape Berliner Bäder"** → "Run workflow"

---

## 📅 Automatisiertes Scraping

**Zeitplan:** Täglich **02:00 UTC** (04:00 CEST / 03:00 MESZ)

| Schritt | Was | Status |
|---------|-----|--------|
| 1. Checkout | Repository runterladen | ✅ `actions/checkout@v4` |
| 2. Python Setup | Python 3.12 + deps | ✅ `actions/setup-python@v5` |
| 3. Scrape | `scraper/scrape_pools.py` ausführen | ✅ (~2 Min) |
| 4. Validieren | JSON-Format checken | ✅ |
| 5. Auto-Commit | Nur wenn Daten geändert | ✅ if-changed |

**Log-Output Beispiel:**
```
🔄 Fetching https://www.berlinerbaeder.de/oeffnungszeiten-auf-einem-blick/ ...
✅ Scraped 78 pools across 7 days from overview page
🔍 Fetching detail pages for time slot labels ...
  [1/78] Schwimm- und Sprunghalle im Europasportpark (SSE)
  [2/78] Sommerbad Kreuzberg
  ...
✅ Enriched 78 pools with detail labels
📁 Written to data/pools.json
   Sommerbad: 42
   Hallenbad: 36
```

---

## 📊 Datenstruktur (`data/pools.json`)

```json
{
  "scraped_at": "2026-07-13T20:32:33Z",
  "source_url": "https://www.berlinerbaeder.de/oeffnungszeiten-auf-einem-blick/",
  "dates": ["Mo. 13.07.26", "Di. 14.07.26", ...],
  "pools": [
    {
      "name": "Schwimm- und Sprunghalle im Europasportpark (SSE)",
      "type": "Hallenbad",
      "detail_url": "https://www.berlinerbaeder.de/baeder/...",
      "schedule": [
        {
          "date": "Mo. 13.07.26",
          "times": [
            {
              "time": "06:30 - 08:00",
              "label": "Frühschwimmen"
            },
            {
              "time": "08:00 - 09:00",
              "label": "Wassersport (eingeschränkt)"
            }
          ]
        },
        ...
      ]
    },
    ...
  ]
}
```

**Felderklärung:**
- `times` kann sein:
  - `"geschlossen"` – Bad ist zu
  - `"unbekannt"` – Daten noch nicht veröffentlicht
  - `[{time, label}, ...]` – Liste von Zeitslots mit Labels
  - `"06:30 - 08:00"` – Einfacher Time-String (Legacy)

---

## 🎨 Frontend-Features

### Dashboard

- **Header** – Aktualisierungszeit, Pool-Anzahl, Tagesanzahl
- **Filter-Toolbar** – „Alle" / „Sommerbäder" / „Hallenbäder"
- **Favoriten-Panel** – Selektieren/Abwählen aller Lieblingsbäder
- **Responsive Tabelle** – Sticky Pool-Namen, Spalten-Scroll, Heute-Highlight

### Interaktionen

| Action | Speicherung |
|--------|------------|
| Klick ⭐ neben Pool-Namen | LocalStorage (`bbb-favorites`) |
| Filter nach Kategorie | Session (nicht persistent) |
| Favoriten-Ansicht | Session (nicht persistent) |

---

## 🐛 Troubleshooting

### „Daten konnten nicht geladen werden"

1. Prüfe Browser-Konsole (F12 → Console)
2. Checke ob `data/pools.json` existiert
3. Validieres JSON: `python -c "import json; json.load(open('data/pools.json'))"`

### Scraper fehlgeschlagen

```bash
# Logs ansehen (lokal)
python scraper/scrape_pools.py 2>&1 | tee scrape.log

# GitHub Actions Logs
GitHub → Actions → "Scrape Berliner Bäder" → letzte Ausführung
```

**Häufige Fehler:**
- ❌ `berlinerbaeder.de` hat die HTML-Struktur geändert  
  → Manuell aktualisieren in `scraper/scrape_pools.py`
- ❌ Connection-Timeout  
  → Wird automatisch wiederholt oder manuell neu getriggert
- ❌ Fehlende Dependencies  
  → `pip install -r requirements.txt`

---

## 📈 Metrics & Status

| Metrik | Wert |
|--------|------|
| **Pools insgesamt** | ~78 (dynamisch) |
| **Vorausschau-Tage** | 7-14 Tage |
| **Update-Frequenz** | 1× täglich um 02:00 UTC |
| **Frontend Größe** | 38 KB (index.html) |
| **JSON Größe** | ~50 KB |
| **Scrape-Zeit** | ~2 Min (inkl. Detail-Pages) |
| **Git Commits/Woche** | ~7 (wenn Daten geändert) |

---

## 🔄 Was wird wann gescraped?

### Täglich 02:00 UTC (04:00 CEST)

1. **Übersichtsseite parsen**  
   `https://www.berlinerbaeder.de/oeffnungszeiten-auf-einem-blick/`
   - Pool-Namen extrahieren
   - Öffnungszeiten aus Tabelle auslesen
   - 7-14 Tage vorab

2. **Detail-Pages durchgehen** (optional)  
   Für jeden Pool einzeln:
   - `https://www.berlinerbaeder.de/baeder/{pool-id}/`
   - Labels auslesen: „Eingeschränkte Wasserfläche", „Schul-/Vereinsbetrieb", etc.
   - Mit 0.3 Sek Delay zwischen Requests (höflich gegenüber Website)

3. **JSON generieren**  
   `data/pools.json` mit aktuellem Timestamp

4. **Commit & Push**  
   Nur wenn sich Daten geändert haben

---

## 🚀 Deployment

### GitHub Pages aktivieren

1. **Settings** → **Pages**
2. **Source:** `Deploy from a branch`
3. **Branch:** `main` / Folder: `/ (root)` oder `/docs`
4. **Save** → Site ist live unter `https://{username}.github.io/BBB-2/`

### Custom Domain (optional)

1. DNS A-Record setzen
2. **Settings** → **Pages** → **Custom domain** eingeben
3. `CNAME`-Datei wird automatisch erstellt

---

## 🤝 Beitragen

PRs sind willkommen! Beispiele:

- 🐛 Scraper-Fehler beheben
- ✨ UI-Features hinzufügen (z.B. Benachrichtigungen)
- 📊 Daten-Export (CSV, iCal)
- 🌐 Mehrsprachigkeit

---

## 📝 Lizenz

[Lizenz hier einfügen, z.B. MIT]

---

## 📞 Support & Links

- **BBB Official:** https://www.berlinerbaeder.de/
- **Öffnungszeiten:** https://www.berlinerbaeder.de/oeffnungszeiten-auf-einem-blick/
- **Issues:** [GitHub Issues](https://github.com/seetiger1/BBB-2/issues)

---

**Zuletzt aktualisiert:** 2026-07-13  
**Nächster Scrape:** Morgen 02:00 UTC
