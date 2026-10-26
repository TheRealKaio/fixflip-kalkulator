# Neustart ImmoCheck

Responsive Immobilien-Kalkulatoren für Budget, Eigennutzung, Vermietung, Fix & Flip und Finanzierung.

## Aktueller Stand

Die App wird als statische Website über GitHub Pages veröffentlicht. Die Hauptseite wird im GitHub-Actions-Workflow aus den komprimierten Dateien unter `source/` gebaut. Rechner, Adminbereich, PDF-Berichte und Build-Verarbeitung liegen ergänzend in `assets/` und `scripts/`.

- Rechnernavigation mit eigenen URLs und zuletzt gewähltem Rechner
- Finanzierungsrechner mit Restschuldverlauf, Bundesbank-Zinsreihe und den Szenarien „Zinssatz fällt“, „Zinssatz stabil“ und „Zinssatz steigt“
- Adminbereich für Layout, Unternehmensangaben, Metadaten, Profile, rechtliche Inhalte und Statistiken
- Gemeinsame PDF-Berichtsfunktionen für Logo, Kopfbereich, Fußzeile und rechtliche Hinweise
- Die Projektdokumentation kann unter Admin → Layout als letzte Karte heruntergeladen werden

Die Admin-Einstellungen werden derzeit lokal im Browser gespeichert. Eine serverseitige Anmeldung und zentrale Datenbank sind noch offen.

## Dokumentation

- [Vollständige Projektdokumentation (Markdown)](docs/PROJEKTSTATUS.md)
- [Projektdokumentation als PDF](docs/README-Projektdokumentation.pdf)

Die Dokumentation folgt dieser Gliederung:

1. Aktueller Stand
2. Navigation und Layoutregeln
3. CSS- und PDF-Regeln
4. Formeln und Berechnungsregeln, einschließlich Anschlussfinanzierung (4.6) und historischer Hypothekenzinsen (4.7)
5. Standardwerte und Eingaben
6. Build, Tests und Veröffentlichung
7. Offene Aufgaben

Sie enthält gemeinsame Formeln sowie Feldreferenz-Tabellen mit Erklärung und Formel für Budget, Eigennutzung, Vermietung, Fix & Flip und Finanzierungsrechner.

## Entwicklung und Veröffentlichung

Änderungen an der Hauptseite werden im GitHub-Actions-Workflow unter `.github/workflows/pages.yml` gebaut. Die eigenständige Finanzierungsseite wird aus `assets/financing.html` kopiert. Admin- und PDF-Quellen liegen in `assets/`; Prüfskripte und Build-Helfer in `scripts/`.

Der Pages-Workflow startet bei Pushes auf `main`, kann manuell gestartet werden und veröffentlicht nur nach erfolgreichen Build- und Verifikationsschritten.

Live: <https://www.neustart-immocheck.de/>  
Repository: <https://github.com/TheRealKaio/fixflip-kalkulator>
