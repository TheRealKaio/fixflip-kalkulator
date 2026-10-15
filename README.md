# Neustart ImmoCheck

Web-App **Version V8.168**.

## Rechner

- Budget
- Eigennutzung
- Fix & Flip

## Branding in V8.168

- Neues **Neustart ImmoCheck**-Logo oben links im Kalkulator
- Einheitliche dunkelblaue Kopfzeile in allen drei PDF-Berichten
- Jeweiliger Berichtstitel bleibt in der PDF-Kopfzeile erhalten
- Domain **neustart-immocheck.de** dezent in der PDF-Fußzeile
- Versionsnummer auf **V8.168** aktualisiert
- Die bisherigen Budget-Standardwerte und Safari-Anpassungen bleiben erhalten

## Veröffentlichung

Live-Adresse:
https://therealkaio.github.io/fixflip-kalkulator/

- V8.168: Logo wird als Base64 direkt in die HTML-Datei eingebettet, damit es auf GitHub Pages und Safari zuverlässig angezeigt wird.

- V8.168: Service Worker erneuert; alte Web-App-Caches werden beim Aktivieren gelöscht und neue Inhalte bevorzugt aus dem Netz geladen.

- V8.168: Das sichtbare Neustart ImmoCheck Logo wird als Inline-SVG direkt in die Seite geschrieben. Die JPEG-Datei wurde zusätzlich als kompatibles Baseline-JPEG neu erzeugt und wird nur für die PDF-Ausgabe verwendet.

- V8.168: Der Begriff **Deal Check** wurde aus dem App-Header entfernt.
- V8.168: Alle PDF-Berichte verwenden das vorhandene SVG-Logo als Quelle; das alte JPG-Logo wird nicht mehr für die PDF-Kopfzeile benutzt.

- V8.168: Logo auf jeder PDF-Seite. Auch die Abschluss-Checkliste nutzt jetzt dieselbe Marken-Kopfzeile mit Neustart ImmoCheck Logo.

- V8.168: Fix & Flip und Eigennutzung zeichnen das Markenlogo in einem abschließenden Seiten-Pass nochmals auf jede PDF-Seite; dadurch ist es auch auf Seite 1 zuverlässig vorhanden.

- V8.168: JavaScript-Syntaxfehler aus V8.162 behoben. Buttons, Rechnerwechsel und Eingabefunktionen sind wieder aktiv.

- V8.168: Fix & Flip und Eigennutzung ersetzen auf Seite 1 jetzt den ursprünglichen Header explizit durch die gemeinsame Marken-Kopfzeile; zusätzlich wird das Logo im Abschluss-Pass auf jeder Seite erneut gezeichnet.

- V8.168: Der Bereich **Weitere Annahmen** im Budget-Rechner ist standardmäßig geschlossen und lässt sich rechts über Plus/Minus öffnen und schließen.
- V8.168: Bei der maximal tragbaren Kreditrate wird zusätzlich der Anteil am Haushaltsnettoeinkommen in Prozent inklusive kurzer Einordnung angezeigt.

- V8.168: Fix & Flip und Eigennutzung starten standardmäßig mit **Hamburg** als Bundesland und **20095 Hamburg** als PLZ/Ort.

- V8.168: **Max. Darlehen** wird im Budget-Rechner gelb hervorgehoben.
- V8.168: Reiter 3 heißt **Annahme zur möglichen Immobilie**.
- V8.168: Eingabezeilen mit Plus-Button nutzen mobil die volle verfügbare Breite; insbesondere Haushaltsnettoeinkommen und Sanierung inkl. Puffer.

- V8.168: **Max. Darlehen** wird fest gelb hervorgehoben.
- V8.168: Die komplette Zeile **Maximal tragbare Kreditrate** wechselt dynamisch: grün bis 30 %, gelb über 30 bis 35 %, rot über 35 % des Haushaltsnettos.
