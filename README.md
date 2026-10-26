# Neustart ImmoCheck

Responsive Immobilien-Kalkulatoren für Budget, Eigennutzung, Vermietung, Fix & Flip und Finanzierung.

## Aktueller Stand

Die App wird als statische Website über GitHub Pages veröffentlicht. Die Hauptseite wird im GitHub-Actions-Workflow aus den komprimierten Dateien unter `source/` gebaut. Rechner, Adminbereich, PDF-Berichte und Build-Verarbeitung liegen ergänzend in `assets/` und `scripts/`.

- Rechnernavigation mit eigenen URLs und zuletzt gewähltem Rechner
- Finanzierungsrechner mit Restschuldverlauf, Bundesbank-Zinsreihe und Anschlussfinanzierungsszenarien
- Adminbereich für Layout, Unternehmensangaben, Metadaten, Profile, rechtliche Inhalte und Statistiken
- Gemeinsame PDF-Berichtsfunktionen für Logo, Kopfbereich, Fußzeile und rechtliche Hinweise

Die Admin-Einstellungen werden derzeit lokal im Browser gespeichert. Eine serverseitige Anmeldung und zentrale Datenbank sind noch offen.

## Dokumentation

- [Vollständige Projektdokumentation (Markdown)](docs/PROJEKTSTATUS.md)
- [Projektdokumentation als PDF](docs/README-Projektdokumentation.pdf)

Die vollständige Dokumentation enthält Formeln, Berechnungsregeln, bekannte Standardwerte, CSS- und PDF-Regeln, Build-Ablauf und offene Aufgaben.

## Entwicklung und Veröffentlichung

Änderungen an der Hauptseite werden im GitHub-Actions-Workflow unter `.github/workflows/pages.yml` gebaut. Die eigenständige Finanzierungsseite wird aus `assets/financing.html` kopiert. Admin- und PDF-Quellen liegen in `assets/`; Prüfskripte und Build-Helfer in `scripts/`.

Der Pages-Workflow startet bei Pushes auf `main`, kann manuell gestartet werden und veröffentlicht nur nach erfolgreichen Build- und Verifikationsschritten.

Live: <https://www.neustart-immocheck.de/>  
Repository: <https://github.com/TheRealKaio/fixflip-kalkulator>
