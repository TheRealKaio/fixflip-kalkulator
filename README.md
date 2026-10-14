# Neustart ImmoCheck

Web-App **Version V8.160**.

## Rechner

- Budget
- Eigennutzung
- Fix & Flip

## Branding in V8.160

- Neues **Neustart ImmoCheck**-Logo oben links im Kalkulator
- Einheitliche dunkelblaue Kopfzeile in allen drei PDF-Berichten
- Jeweiliger Berichtstitel bleibt in der PDF-Kopfzeile erhalten
- Domain **neustart-immocheck.de** dezent in der PDF-Fußzeile
- Versionsnummer auf **V8.160** aktualisiert
- Die bisherigen Budget-Standardwerte und Safari-Anpassungen bleiben erhalten

## Veröffentlichung

Live-Adresse:
https://therealkaio.github.io/fixflip-kalkulator/

- V8.160: Logo wird als Base64 direkt in die HTML-Datei eingebettet, damit es auf GitHub Pages und Safari zuverlässig angezeigt wird.

- V8.160: Service Worker erneuert; alte Web-App-Caches werden beim Aktivieren gelöscht und neue Inhalte bevorzugt aus dem Netz geladen.

- V8.160: Das sichtbare Neustart ImmoCheck Logo wird als Inline-SVG direkt in die Seite geschrieben. Die JPEG-Datei wurde zusätzlich als kompatibles Baseline-JPEG neu erzeugt und wird nur für die PDF-Ausgabe verwendet.

- V8.160: Der Begriff **Deal Check** wurde aus dem App-Header entfernt.
- V8.160: Alle PDF-Berichte verwenden das vorhandene SVG-Logo als Quelle; das alte JPG-Logo wird nicht mehr für die PDF-Kopfzeile benutzt.
