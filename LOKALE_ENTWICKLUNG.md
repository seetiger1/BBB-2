# 💻 Guide: Lokale Entwicklung für Einsteiger

Dieser Guide erklärt dir Schritt für Schritt, wie du das Projekt auf deinem eigenen Computer (lokal) ausführen kannst. So kannst du den Scraper manuell starten, neue Daten laden und dir die Webseite auf deinem eigenen Rechner ansehen, ohne dass du die Änderungen sofort ins Internet (auf GitHub) hochladen musst.

Diese Anleitung ist bewusst für Einsteiger geschrieben und sollte auch in Zukunft für dieses Projekt gültig sein.

---

## 🛠️ Schritt 1: Voraussetzungen (Einmalig)

Bevor du starten kannst, benötigt dein Computer die richtige Software.

1. **Python installieren:**
   - Gehe auf [python.org/downloads](https://www.python.org/downloads/) und lade dir die aktuellste Version von Python herunter.
   - **WICHTIG (für Windows-Nutzer):** Setze bei der Installation unbedingt das Häkchen bei **"Add Python to PATH"** (Python zum Pfad hinzufügen), bevor du auf "Install" klickst.
   - (Mac-Nutzer können Python oft über den Installer herunterladen oder nutzen das Terminal).

2. **Terminal (Kommandozeile) öffnen:**
   - **Windows:** Drücke die Windows-Taste, tippe `cmd` oder `PowerShell` ein und drücke Enter. Alternativ kannst du das Terminal direkt in deinem Code-Editor (z.B. VS Code) öffnen.
   - **Mac:** Öffne die Spotlight-Suche (Cmd + Leertaste), tippe `Terminal` ein und drücke Enter.

---

## 📂 Schritt 2: Zum Projektordner navigieren

Du musst dem Terminal sagen, wo sich deine Projektdateien befinden.

1. Finde den Pfad zu deinem Projektordner (z.B. `BBB-2`).
2. Tippe im Terminal den Befehl `cd` (steht für "change directory"), gefolgt von einem Leerzeichen, und ziehe dann den Ordner einfach mit der Maus in das Terminalfenster (oder tippe den Pfad manuell ein).
   ```bash
   cd pfad/zu/deinem/ordner/BBB-2
   ```
3. Drücke Enter. Du befindest dich nun im Projektordner.

---

## 📦 Schritt 3: Benötigte Pakete installieren (Einmalig)

Der Scraper nutzt kleine Helfer-Programme (Bibliotheken), um Webseiten auslesen zu können. Diese müssen wir einmalig herunterladen.

1. Stelle sicher, dass du dich im Projektordner befindest (Schritt 2).
2. Gib folgenden Befehl in dein Terminal ein und drücke Enter:
   ```bash
   pip install -r requirements.txt
   ```
   *(Tipp: Auf manchen Mac-Computern musst du stattdessen `pip3` statt `pip` schreiben).*
3. Warte, bis die Installation abgeschlossen ist.

---

## 🔄 Schritt 4: Den Scraper manuell starten (Alltag)

Wenn du aktuelle Schwimmbad-Daten herunterladen möchtest, startest du den Scraper.

1. Gib folgenden Befehl im Terminal ein:
   ```bash
   python scraper/scrape_pools.py
   ```
   *(Tipp: Auf manchen Mac-Computern musst du `python3` statt `python` schreiben).*
2. Drücke Enter. Du wirst sehen, wie der Scraper anfängt, die Berliner Bäder Webseite auszulesen.
3. Wenn er fertig ist, steht dort "Written to data/pools.json". Die Daten sind nun in der Datei `pools.json` aktualisiert worden.

---

## 🌐 Schritt 5: Die Webseite lokal ansehen (Alltag)

Jetzt wollen wir uns das Ergebnis auf einer lokalen Webseite ansehen.

1. Bleibe im gleichen Terminal-Fenster im Projektordner.
2. Starte einen lokalen Webserver mit diesem Befehl:
   ```bash
   python -m http.server 8000
   ```
   *(Wieder: Evtl. `python3` nutzen).*
3. Du siehst nun eine Meldung wie `Serving HTTP on 0.0.0.0 port 8000 ...`. Dein Server läuft!
4. Öffne nun deinen Webbrowser (Chrome, Firefox, Safari, etc.).
5. Tippe oben in die Adresszeile folgendes ein und drücke Enter:
   ```text
   http://localhost:8000
   ```
6. **Fertig!** Du siehst nun deine Webseite mit den frisch gescrapten Daten.

---

## 🛑 Schritt 6: Den Server beenden

Wenn du fertig bist und den lokalen Server wieder ausschalten möchtest:

1. Gehe zurück in dein Terminal-Fenster, in dem der Server läuft.
2. Drücke die Tastenkombination `Strg + C` (auf dem Mac `Ctrl + C`, **nicht** Cmd).
3. Der Server wird beendet und du kannst das Terminal wieder normal benutzen oder schließen.

---

## 💡 Zusammenfassung für den schnellen Start (Wenn alles eingerichtet ist)

Wenn du das nächste Mal an dem Projekt arbeitest, musst du nur noch dies tun:

1. Terminal öffnen und in den Ordner wechseln (`cd pfad/zum/projekt`).
2. Scraper starten: `python scraper/scrape_pools.py`
3. Server starten: `python -m http.server 8000`
4. Im Browser `http://localhost:8000` öffnen.
