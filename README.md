# Neustart ImmoCheck

Responsive Immobilien-Kalkulatoren für Budget, Eigennutzung, Vermietung, Fix & Flip und Finanzierung.

## Aktueller Stand

Die App wird als statische Website über GitHub Pages veröffentlicht. Die Hauptseite wird im GitHub-Actions-Workflow aus den komprimierten Dateien unter `source/` gebaut. Rechner, Adminbereich, PDF-Berichte und Build-Verarbeitung liegen ergänzend in `assets/` und `scripts/`.

- Rechnernavigation mit eigenen URLs und zuletzt gewähltem Rechner
- Finanzierungsrechner mit Restschuldverlauf, Bundesbank-Zinsreihe und den Szenarien „Zinssatz fällt“, „Zinssatz stabil“ und „Zinssatz steigt“
- Adminbereich für Layout, Unternehmensangaben, Metadaten, Profile, rechtliche Inhalte und Statistiken
- Gemeinsame PDF-Berichtsfunktionen für Logo, Kopfbereich, Fußzeile und rechtliche Hinweise
- Die Projektdokumentation kann unter Admin → Layout als letzte Karte heruntergeladen werden

Für Anmeldung, zentrale Einstellungen und Statistiken liegt ein optionales PHP-/MySQL-Backend unter `server/webspace/` vor. Seine Installation und der tatsächliche Betrieb sind getrennt vom statischen Pages-Deployment. Die Rechnerformeln laufen weiterhin im Browser; Bezahlfunktionen und serverseitige Berechnungen sind noch nicht umgesetzt.

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

## Modularisierung und Rechnerkennungen (4. November 2026)

`assets/calculators.json` definiert die fünf stabilen Kennungen und Routen zentral:

| Rechner | Kennung | Route |
| --- | --- | --- |
| Budget | `budget` | `/budget/` |
| Eigennutzung | `own` | `/eigennutzung/` |
| Vermietung | `rent` | `/vermietung/` |
| Fix & Flip | `flip` | `/fix-flip/` |
| Finanzierung | `finance` | `/finanzierungsrechner/` |

Die Navigation nutzt diese Registrierung. `data-calculator` am HTML-Element und Body zeigt den aktiven Rechner auch nach einem Wechsel ohne Seitenneuladen. `window.NICCalculators.active` liefert die Kennung; `nic-calculator-changed` meldet abgeschlossene Wechsel. Eigennutzung und Fix & Flip teilen derzeit denselben Inhaltscontainer, bleiben aber unterschiedliche Rechnerkennungen.

Das Build-Skript `scripts/build_unified_navigation.py` erzeugt die gemeinsame Navigation und den darin integrierten Finanzierungsrechner. Gemeinsame Layoutregeln bleiben zentral in den bestehenden Stylesheets. Eine vollständige Aufteilung der übrigen Formeln und rechnerspezifischen Styles ist noch offen.

Alte Patch-Dateien sind teilweise aktive Build-Abhängigkeiten. Sie dürfen erst entfernt werden, nachdem ihre Wirkung in die gepflegten Quellen übernommen und der vollständige Build geprüft wurde. Veraltete Repositories werden nur nach eindeutiger Zuordnung und Prüfung von Deployment-Abhängigkeiten entfernt. Im geprüften Kaio-Konto wurde bei der Repository-Suche nur `fixflip-kalkulator` gefunden; es wurde kein Repository gelöscht.

### CSS-Auslagerung

`scripts/modularize_calculator_styles.py` läuft nach der Erzeugung der einheitlichen Navigation. Statische Inline-Styles werden an exakt derselben Stelle durch Stylesheet-Links ersetzt. Die erzeugten Dateien sind nach `shared`, `budget`, `own`, `rent` und `flip` geordnet und werden zwischen Routen wiederverwendet. Der Finanzierungsrechner behält seine isolierten Shadow-DOM-Styles im Finanzierungsmodul. `calculator-styles.json` dokumentiert die erzeugten Gruppen.

Die Aufteilung verwendet mehrere geordnete CSS-Blöcke je Gruppe: Ein Zusammenziehen in nur eine Datei je Rechner würde die bisherige Kaskade verschieben. Laufzeitabhängige Styles und Styles mit relativen Ressourcenpfaden bleiben erhalten. Eine semantische Bereinigung aller alten CSS-Überschreibungen ist damit noch nicht abgeschlossen. Die komprimierten Originalquellen und Berechnungsformeln bleiben unverändert.

### Bereinigung historischer CSS-Regeln

Vor der CSS-Auslagerung entfernt `scripts/clean_calculator_css.py` leere Regeln, vollständig wiederholte Angaben und nachweislich durch spätere Regeln desselben Selektors ersetzte feste Größenwerte. Medienbedingungen und Priorität (`!important`) werden getrennt behandelt. Komplexe Werte, Browser-Fallbacks, benannte Layer und dynamisch verwaltete Styles bleiben bestehen. Der Cleaner ist mit zwölf gezielten Tests abgesichert.

Die Browserprüfung vergleicht nun ausdrücklich die bereinigten externen Styles mit den ursprünglichen Inline-Regeln, einschließlich fingerprinteter Dateinamen. Die vorübergehende Vergleichsdatei wird vor der Veröffentlichung entfernt. `calculator-css-cleanup.json` protokolliert die entfernten Regeln/Angaben über die sechs Seitenausgaben. Dies ist eine konservative Bereinigung der statischen Inline-Regeln; historische Build-Patches bleiben weiterhin aktiv, soweit sie die Seiten erzeugen.

### Gemeinsame Einbindung der Finanzierung

Die zuvor eingeführte zusätzliche Datei `calculator-finance.js` ist wieder entfernt. Die Finanzierungsfunktion wird innerhalb von `calculator-navigation.js` zusammen mit den fünf zentral registrierten Rechnern geladen und initialisiert. Es gibt keinen zusätzlichen globalen `NICFinanceModule`-Startpunkt. Navigation, Rechnerkennung und Referenzzins bleiben gemeinsam. Die fachlichen Finanzierungsformeln und der bestehende isolierte Formularcontainer bleiben erhalten, um Feld-ID- und CSS-Kollisionen zu vermeiden. Dies vereinheitlicht die Einbindung; es behauptet keine vollständige Zusammenführung aller historisch gewachsenen Speicher- oder PDF-Implementierungen.
