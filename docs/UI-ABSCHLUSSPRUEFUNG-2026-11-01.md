# ImmoCheck – UI-Abschlussprüfung vom 1. November 2026

Branch: `design/immocheck-ui-only-2026-11`.
Ausgangsstand: `d4dcca46dedb290c51684e0e2e73acd812e3e180`.

## Umsetzung

- Bestätigtes Logo: dunkelgrünes Haus, vier Fenster, gelbe Welle und zweizeilige Wortmarke auf weißem Hintergrund. Die bestätigte Bildvorlage ist die zentrale Quelle für Header, SVG/PNG-Favicon, Apple Touch Icon (180 × 180), Social-Bild (1200 × 630) und die statischen Ersatzdateien.
- Immobilienfoto mit responsivem Zuschnitt und heller Fläche unter dem Text; kompakter weißer Logobereich, gut lesbare Titel und Anmeldung.
- Volle Desktopbreite mit seitlichem Abstand, fünf gleichwertige Rechnerkacheln, gestapelte Kacheltexte, nummerierte Schritte mit Verbindungslinien und korrigierter doppelter Nummerierung.
- Schmaler dunkelgrüner Footer mit sämtlichen bisherigen rechtlichen Links; lesbare Link- und Textkontraste.
- Fix-&-Flip-Route `/fix-flip/` erhält nun ebenfalls das Design-Stylesheet. Sie fehlte zuvor in der Liste der zu gestaltenden Routen.
- Der Laufzeit-Fallback der Website-Einstellungen verwendet das bestätigte Logo und stellt nicht erneut das alte Zeichen her.
- Auf 320 Pixel breiten Geräten stehen die Ergebniskacheln untereinander. Damit laufen Eigennutzung und Vermietung auch in den späteren Schritten nicht aus dem Bildschirm.
- PNG-Dateien werden zunächst vollständig im Speicher erzeugt und dekodiert, dann atomar ersetzt. Die Prüfung lädt alle PNGs vollständig; so werden auch abgeschnittene Bilddaten erkannt. Der Icon-Zuschnitt enthält die vollständige gelbe Welle.
- Browserzoom bleibt möglich. Bildbeschreibungen, Tastaturfokus, Feld-IDs und bestehende Bedienfunktionen bleiben erhalten.

## Schutz der Berechnungen

Die sieben komprimierten Quelldateien unter `source/`, `assets/financing.html` und `assets/pdf-reports.js` wurden byteweise mit dem Ausgangsstand verglichen: alle neun Dateien sind unverändert. Die Änderungen betreffen Bilder, Darstellung, die Schrittbeschriftung, den Logo-Fallback und Build-/Prüfintegration. Es wurden keine Berechnungsformeln, fachlichen Regeln oder Eingabewerte verändert.

Der abschließende Branding-Schritt prüft außerdem, dass sämtliche Script-Blöcke der erzeugten Seiten vor und nach der Bild-/Metadatenanpassung identisch sind.

## Ergebnisse

| Prüfung | Ergebnis |
| --- | --- |
| Vollständiger statischer Build mit vorhandenen Build-Verifikationen | Erfolgreich |
| Budget-Slider und Grenzfälle | Erfolgreich |
| Vermietung, Kennzahlen, Interpretation und Reset | Erfolgreich |
| Finanzierungsnavigation, Startwerte und monatliche Werte | Erfolgreich |
| Fünf Rechner und alle 26 Schritte | Erfolgreich |
| Desktop 1440 und 1920 Pixel, Mobil 320 und 390 Pixel, Querformat 844 Pixel | 25 erfolgreiche Browserfälle; alle Schritte ohne Seitenüberlauf |
| Restschuld: 300.000 €, 4 % Zins, 2 % Tilgung, zehn Jahre, ohne/mit 5 % Sondertilgung | Erfolgreicher Vergleich mit unabhängig berechnetem Annuitätenverlauf |
| Restschuld: Nullzins und Darlehen null | Erfolgreich |
| Finanzierung: Charts und Anschlussfinanzierung | Bestehende Elemente erhalten; Integrations- und PDF-Prüfungen erfolgreich |
| PDFs | Drei Seiten für Finanzierung, historische Zinskurven, Anschlussfinanzierung und rechtliche Abschnitte aller fünf Rechner erfolgreich geprüft |
| Header, Logo, Favicon, Apple und Social-Metadaten | Erfolgreich, einschließlich Prüfung der gelben Welle |
| Anmeldung, Kontonavigation, rechtlicher Footer, Einstellungen und Statistik | Erfolgreich |
| PHP-API, Rollen, Sitzungen und CSRF | GitHub Actions erfolgreich |
| JavaScript-Syntax und Whitespace-Prüfung | Erfolgreich |

Die horizontal scrollbar gehaltene Schrittleiste auf kleinen Geräten ist beabsichtigt; die Seite selbst bleibt innerhalb der Bildschirmbreite.

## GitHub Actions

Für Implementierungsstand `889136fd73d6916bf529c98157ba786be7b22151`:

- [UI-Entwicklungsprüfungen – erfolgreich](https://github.com/TheRealKaio/fixflip-kalkulator/actions/runs/41335660921)
- [Build, PHP, PDFs und Browserintegration ohne Deployment – erfolgreich](https://github.com/TheRealKaio/fixflip-kalkulator/actions/runs/41335660902)

Für `191a2d0ff3689885e52546e3abc9fc710d77513b` sind sowohl die [UI-Prüfung](https://github.com/TheRealKaio/fixflip-kalkulator/actions/runs/41336045466) als auch der [Integrationslauf](https://github.com/TheRealKaio/fixflip-kalkulator/actions/runs/41336045391) erfolgreich.

Die abschließende Aktualisierung der PNG-Erzeugung und statischen Ersatzlogos und kleiner Darstellungsdetails löst dieselben Entwicklungsprüfungen erneut aus. Die jeweils zum aktuellen Commit gehörenden Ergebnisse stehen unter [Actions für diesen Branch](https://github.com/TheRealKaio/fixflip-kalkulator/actions?query=branch%3Adesign%2Fimmocheck-ui-only-2026-11).

## Prüfgrenzen und Veröffentlichung

Die API-Prüfung nutzt Testdaten und SQLite-Fixtures; sie prüft keine echte MariaDB-Verbindung und keinen SMTP-Versand. Der PDF-Test deckt Dokumenterzeugung und zentrale Inhalts-/Strukturverträge ab, keinen vollständigen visuellen Einzelvergleich jeder denkbaren Eingabekombination. Die Browserprüfung erfolgte in Chromium mit verschiedenen Bildschirmgrößen, nicht auf einem physischen iPhone oder in Safari.

Lokal fehlte PHP; dessen vollständiger Test wurde deshalb im GitHub-Runner erfolgreich ausgeführt. Der lokale Chromium-Test nutzte einen alternativen Chromium-Binärpfad; im GitHub-Runner wird die reguläre Playwright-Installation verwendet.

Kein Merge nach `main`, keine Live-Veröffentlichung und kein Deployment-Job wurden ausgeführt. Der Build des Pages-Workflows wurde über den Entwicklungsworkflow ohne Veröffentlichungsberechtigungen geprüft.
