# Neustart ImmoCheck

Web-App **Version V8.164**.

## Rechner

- Budget
- Eigennutzung
- Fix & Flip

## Branding in V8.164

- Neues **Neustart ImmoCheck**-Logo oben links im Kalkulator
- Einheitliche dunkelblaue Kopfzeile in allen drei PDF-Berichten
- Jeweiliger Berichtstitel bleibt in der PDF-Kopfzeile erhalten
- Domain **neustart-immocheck.de** dezent in der PDF-Fußzeile
- Versionsnummer auf **V8.164** aktualisiert
- Die bisherigen Budget-Standardwerte und Safari-Anpassungen bleiben erhalten

## Veröffentlichung

Live-Adresse:
https://therealkaio.github.io/fixflip-kalkulator/

- V8.164: Logo wird als Base64 direkt in die HTML-Datei eingebettet, damit es auf GitHub Pages und Safari zuverlässig angezeigt wird.

- V8.164: Service Worker erneuert; alte Web-App-Caches werden beim Aktivieren gelöscht und neue Inhalte bevorzugt aus dem Netz geladen.

- V8.164: Das sichtbare Neustart ImmoCheck Logo wird als Inline-SVG direkt in die Seite geschrieben. Die JPEG-Datei wurde zusätzlich als kompatibles Baseline-JPEG neu erzeugt und wird nur für die PDF-Ausgabe verwendet.

- V8.164: Der Begriff **Deal Check** wurde aus dem App-Header entfernt.
- V8.164: Alle PDF-Berichte verwenden das vorhandene SVG-Logo als Quelle; das alte JPG-Logo wird nicht mehr für die PDF-Kopfzeile benutzt.

- V8.164: Logo auf jeder PDF-Seite. Auch die Abschluss-Checkliste nutzt jetzt dieselbe Marken-Kopfzeile mit Neustart ImmoCheck Logo.

- V8.164: Fix & Flip und Eigennutzung zeichnen das Markenlogo in einem abschließenden Seiten-Pass nochmals auf jede PDF-Seite; dadurch ist es auch auf Seite 1 zuverlässig vorhanden.

- V8.164: JavaScript-Syntaxfehler aus V8.162 behoben. Buttons, Rechnerwechsel und Eingabefunktionen sind wieder aktiv.

- V8.164: Fix & Flip und Eigennutzung ersetzen auf Seite 1 jetzt den ursprünglichen Header explizit durch die gemeinsame Marken-Kopfzeile; zusätzlich wird das Logo im Abschluss-Pass auf jeder Seite erneut gezeichnet.
