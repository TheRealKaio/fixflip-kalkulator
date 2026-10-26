# Neustart ImmoCheck – Projektdokumentation

**Repository:** `TheRealKaio/fixflip-kalkulator`  
**Stand:** 26.10.2026 · Zielrelease V8.348  
**Produktivadresse:** <https://www.neustart-immocheck.de/>  
**GitHub-Pages-Adresse:** <https://therealkaio.github.io/fixflip-kalkulator/>

Diese Dokumentation beschreibt den Repository-Stand und die vereinbarten Produktregeln. Die veröffentlichte App wird im GitHub-Actions-Workflow aus der aufgeteilten gzip/Base64-Quelle unter `source/` gebaut und mit ergänzenden Dateien aus `assets/` sowie Verarbeitungsskripten aus `scripts/` vervollständigt. Änderungen an einer Quellkomponente müssen daher in ihrem vorgesehenen Build-Schritt vorgenommen werden.

## 1. Aktueller Stand

- Statische, responsive Web-App auf GitHub Pages; STRATO-Domain und Pages-Veröffentlichung sind eingerichtet.
- Rechner: Budget, Eigennutzung, Vermietung, Fix & Flip und Finanzierungsrechner. Die Rechner teilen Navigation, Kopfbereich, Admin-Konfiguration und PDF-Branding.
- Quellmodell: `source/index.html.gz.b64.part*` enthält die komprimierte Hauptseite. `assets/financing.html` ist die eigenständige Finanzierungsseite. `assets/admin.html`, `assets/admin.js`, `assets/admin.css` und `assets/pdf-reports.js` liefern Admin- und PDF-Bausteine. Der Workflow `.github/workflows/pages.yml` baut, prüft und veröffentlicht die Seiten.
- Für Änderungen an Seiteninhalten und Layout sind die Quellassets und Build-Skripte maßgeblich; generierte `_site`-Dateien werden beim Build neu erstellt.
- Admin-Einstellungen liegen derzeit lokal im Browser. Die Einstellungsseite weist darauf hin, dass der Bereich nicht angemeldet und nicht geräteübergreifend ist. Eine serverseitige Benutzerverwaltung und Datenbank sind noch nicht eingerichtet.
- Die Admin-Seite bearbeitet Schriftfamilie, Schriftgrößen, Grund-/Text-/Buttonfarben, Unternehmens- und Metadaten, Profile, rechtliche Inhalte und Statistiken. Die Layoutfarben sind sechstellige HEX-Werte.
- `assets/site-settings.json` enthält noch Platzhalterangaben für Anbieter- und Impressumsdaten. Vor einer Bestätigung im öffentlichen Impressum müssen die Angaben durch freigegebene Unternehmensdaten ersetzt werden.
- PDF-Berichte verwenden `assets/pdf-reports.js`: A4, dunkelblauer Kopfbereich, weißes Logo in einer abgerundeten Box, Berichtstitel und Untertitel sowie Fußzeile mit Domain, Versionsnummer und Seitenzahl. Die Einstellungen können Logo, Farben und Unternehmensangaben beeinflussen.

## 2. Navigation und Layoutregeln

Die gemeinsame Rechnernavigation enthält die fünf Produktbereiche Budget, Eigennutzung, Vermietung, Fix & Flip und Finanzierung. Der Finanzierungsrechner ist unter `/finanzierungsrechner/` erreichbar. Die Navigation merkt sich den zuletzt verwendeten Rechner und unterstützt direkte Rechner-URLs.

Verbindliche Gestaltungsregeln:

- Rechner nutzen eine gemeinsame Kopfzeile, Navigation, Aktionsleiste und Footer-Logik. Der Header wird über `assets/stable-header.js`, `assets/stable-header.css` und `assets/header-layout.css` stabilisiert.
- Die gemeinsame Inhaltsbreite beträgt im Finanzierungsrechner maximal 640 px. Karten, Eingaben und Schaltflächen passen sich an schmale Ansichten an.
- Buttons für fünf und zehn Jahre in der Zinskurve sind gleich breit und auf Mobilgeräten vollständig lesbar.
- PDF-Berichte teilen sich den Marken-Header und die Footer-Funktion aus `assets/pdf-reports.js`. Kopfbereich: 34 mm hoch; Logo links bei x=16 mm, Titel rechts davon. Fußzeile: Domain bei x=16 mm, Version mittig bei x=105 mm, Seitenzahl rechts bei x=194 mm, jeweils nahe 289 mm.
- Ergebnisboxen vermitteln ihren Status zusätzlich zur Farbe über die Beschriftung. Gelb kennzeichnet „Bleibt“, Rot kennzeichnet „Steigt“.
- Währungsangaben im Finanzierungsrechner verwenden die deutsche Locale. Darlehensrate, Restschuld und Anschlussraten werden auf ganze Euro gerundet angezeigt; die zugrunde liegende Berechnung bleibt ungerundet.

## 3. Anschlussfinanzierung

Die Seite simuliert die Restschuld am Ende der gewählten Bindungsdauer unter dem im Rechner eingestellten Sollzins, der Anfangstilgung und einer optionalen jährlichen Sondertilgung. Die Szenarien verwenden dieselbe Restschuld und dieselbe gewählte Tilgung:

| Szenario | Szenariozins | Monatsrate |
|---|---:|---:|
| Fällt | eingestellter Sollzins − 1,5 Prozentpunkte | Restschuld × (Szenariozins + Tilgung p. a.) ÷ 12 |
| Bleibt | eingestellter Sollzins | Restschuld × (Szenariozins + Tilgung p. a.) ÷ 12 |
| Steigt | eingestellter Sollzins + 2 Prozentpunkte | Restschuld × (Szenariozins + Tilgung p. a.) ÷ 12 |

Die Anzeige wird mit `Intl.NumberFormat('de-DE', { style:'currency', currency:'EUR', maximumFractionDigits:0 })` auf ganze Euro gerundet. „Bleibt“ hat einen gelben Hintergrund; „Steigt“ einen roten Hintergrund. Das sind Sensitivitätsszenarien, keine Zinsprognosen oder Eintrittswahrscheinlichkeiten.

Berechnungsablauf im Rechner:

1. Monatsrate während der Zinsbindung: `Darlehen × (Sollzins p. a. + Tilgung p. a.) ÷ 1.200`.
2. Monatliche Zinslast: `Restschuld des Vormonats × Sollzins p. a. ÷ 1.200`.
3. Monatliche Tilgung: Monatsrate minus monatliche Zinslast; sie wird auf den offenen Darlehensbetrag begrenzt.
4. Jährliche Sondertilgung: `Darlehen × Sondertilgungssatz p. a. ÷ 100`, am Jahresende von der Restschuld abgezogen.
5. Anschlussrate: `Restschuld nach der Bindungsdauer × (Szenariozins p. a. + gewählte Tilgung p. a.) ÷ 1.200`.

Im erklärenden Hinweis steht, dass während der Zinsbindung Sollzins und Monatsrate konstant angesetzt werden und Sondertilgungen, Gebühren und Zinsänderungen der Anschlussperiode nicht einbezogen sind.

## 4. Formeln und Berechnungsregeln

### 4.1 Gemeinsame Finanzierungsformeln

Zinssätze und Tilgungssätze werden in der Oberfläche in Prozent eingegeben. Für Monatsberechnungen gilt:

- Annuität: `K × (i + t) ÷ 12`, wenn `i` und `t` als Dezimalwerte vorliegen.
- Monatszins auf Restschuld `B`: `B × i ÷ 12`.
- Monatliche Tilgung: `Monatsrate − Monatszins`.
- Restschuld nach Monatszahlung: `max(0, alte Restschuld − monatliche Tilgung)`.
- Restschuld wird nicht negativ; letzte Zahlung darf höchstens die offene Restschuld tilgen.
- Rundung findet bei der Anzeige statt, nicht in den Zwischenberechnungen.

### 4.2 Budget

Der Budgetrechner leitet aus Haushaltsnettoeinkommen, Ausgaben, Eigenkapital, Kaufnebenkosten und Finanzierungsparametern ein freies Monatsbudget und eine daraus tragbare Darlehensgröße ab. Die monatliche Belastungsquote lautet `Kreditrate ÷ Haushaltsnettoeinkommen × 100`. Die Einordnung ist eine Orientierung und ersetzt keine Finanzierungszusage.

Im Workflow sind als aktuelle neutrale Startwerte für Haushaltsnettoeinkommen, Beschäftigungseinkommen, Kindergeld und Eigenkapital jeweils `0` sowie Familienstatus `Single`, ein Erwachsener und null Kinder festgelegt. Weitere Felder behalten ihre im Rechner definierten Werte. Diese Nullen verhindern, dass persönliche Beispielwerte als tatsächliche Angaben erscheinen.

### 4.3 Eigennutzung

Der Rechner ordnet Kaufpreis, Kaufnebenkosten, Eigenkapital, Finanzierung, Modernisierung und laufende Belastung ein. Die Kreditrate folgt den Annuitätsregeln aus Abschnitt 4.1. Tilgung ist Vermögensaufbau, aber gleichzeitig Teil des monatlichen Liquiditätsabflusses. Im Rechner lautet die Leitfrage „Lohnt sich diese Eigentumswohnung?“.

### 4.4 Vermietung

Der Rechner betrachtet Mieteinnahmen, Kaufpreis, Erwerbsnebenkosten, nicht umlagefähige Kosten, Finanzierung und Cashflow. Die grundlegenden Kennzahlen lauten:

- Bruttomietrendite: `Jahresnettokaltmiete ÷ Kaufpreis × 100`.
- Kaufpreisfaktor: `Kaufpreis ÷ Jahresnettokaltmiete`.
- Cashflow vor Steuern: `Mieteinnahmen − nicht umlagefähige Bewirtschaftungskosten − Kreditrate − weitere im Rechner erfasste laufende Kosten`.
- Tilgung und Zins werden getrennt erklärt: Zins ist Finanzierungskosten; Tilgung reduziert die Restschuld.

Die konkrete Kostenabgrenzung richtet sich nach den Eingabefeldern des Rechners. Eine Steuer- oder AfA-Berechnung ist nicht Bestandteil des aktuellen Rechenmodells und bleibt eine mögliche fachlich zu definierende Erweiterung.

### 4.5 Fix & Flip

Das Modell führt Kaufpreis, Erwerbsnebenkosten, Modernisierung, Haltekosten, Finanzierung und Verkaufserlös zusammen. Grundregel: `Projektüberschuss = Verkaufserlös − modellierte Projektkosten`. Finanzierungskosten und Rückzahlung sind nach den im Rechner verwendeten Zahlungsströmen zu unterscheiden; Tilgung darf nicht doppelt als Aufwand angesetzt werden. Die konkrete Renditebasis muss im Ergebnisbericht ausdrücklich mit Eigenkapital oder Gesamtkapital benannt sein.

### 4.6 Historische Hypothekenzinsen

Die Finanzierung zeigt die rollierende Zehnjahresreihe der Bundesbank-Zeitreihen SUD117 (1 bis 5 Jahre Zinsbindung) und SUD118 (5 bis 10 Jahre). Der Workflow bündelt Monatswerte für die Anzeige. Historische Werte beschreiben die Vergangenheit und sind keine Prognose.

## 5. Standardwerte und Eingaben

| Bereich | Repository-Stand |
|---|---|
| Finanzierungsrechner – Darlehen | 300.000 € |
| Sollzins p. a. | 4,01 % |
| Anfangstilgung p. a. | 1,5 % |
| Sondertilgung p. a. | 0 % |
| Zinsbindung | 10 Jahre |
| Budget – persönliche Beispielangaben | Nettoeinkommen, Einkommen, Kindergeld und Eigenkapital 0; Single, 1 Erwachsener, 0 Kinder |
| Eigennutzung / Fix & Flip – Ort | Hamburg, PLZ/Ort 20095 Hamburg als voreingestellte Ortsangabe |

Andere Kalkulatoren und weitere Felder behalten ihre Defaults im Quellcode. Änderungen an Startwerten sollen hier und in den Verifikationsfällen nachgeführt werden.

## 6. CSS- und PDF-Regeln

- Admin → Layout: Schriftfamilie, Grundschriftgröße, H1 bis H4 und Hintergrund-, Text-, Button-Hintergrund- und Button-Textfarbe. Die Farben werden als sechsstellige HEX-Werte validiert. Ein Kontrastwert wird angezeigt; unter 4,5:1 erscheint ein Hinweis.
- Rechnerbreite: maximal 640 px; Karten, Ranges, Ergebnisboxen und Navigationsflächen verwenden flexible Grid-Layouts. Bei schmalen Ansichten wechseln Ergebnisboxen und Buttons in einspaltige Darstellung.
- Finanzierungs-Ergebnisboxen haben eine gemeinsame Basisgestaltung (`.kpi`). Die Anschlussfinanzierung überschreibt nur die Hintergründe von „Bleibt“ und „Steigt“; Beschriftungen bleiben sichtbar und der Zahlenwert verwendet Tabellenschriftziffern.
- PDFs: `assets/pdf-reports.js` stellt `create`, `header`, `footer`, `logo` und Disclaimer-Funktionen bereit. Dokumente sind A4-Hochformat. Kopfzeile dunkelblau (#0F172A), Logo auf weißem Feld, Footer mit Domain, Version und Seitennummer. Neue Dokumente sollen diese gemeinsame Implementierung nutzen.
- Die README-PDF wird im Admin-Tab „Layout“ als letzte Karte mit einem direkten Downloadlink angeboten. Der Build kopiert die versionierte PDF-Datei in den veröffentlichten Pfad.

## 7. Build, Tests und Veröffentlichung

Der Workflow `.github/workflows/pages.yml` läuft bei Änderungen an `main`, manuell und als regelmäßiger Fallback. Er entpackt `source/index.html.gz.b64.part*`, wendet die dokumentierten Layout- und Inhaltsänderungen an, erzeugt Routen und Einstellungen, kopiert den Finanzierungsrechner und prüft HTML/JavaScript, Rechnerlogik, PDFs, Metadaten und Assets. Bei Erfolg wird das Ergebnis nach GitHub Pages veröffentlicht.

Für die Anschlussfinanzierung gilt der Prüffall: Restschuld 200.000 €, Sollzins 3,5 %, Tilgung 2 %. Erwartete Monatsraten vor Anzeigeformatierung: 666,67 €, 916,67 € und 1.250,00 €; erwartete Anzeige: 667 €, 917 € und 1.250 €. Zusätzlich sind die Null-Darlehen- und Zinsbindungsfälle zu prüfen. Der Versionsvertrag in `scripts/release_contract.py` leitet die Versionsnummer aus dem neuesten `scripts/patch*_v8*.py`-Dateinamen ab.

## 8. Offene Aufgaben

| Priorität | Aufgabe |
|---|---|
| Hoch | Build und Live-Deployment nach dieser Änderung erfolgreich abschließen; veröffentlichte README-PDF-URL und Admin-Download prüfen. |
| Hoch | Kopf-/Fußzeile der README-PDF nach dem Rendern visuell mit einem aktuellen Kalkulatorbericht vergleichen. |
| Mittel | Weitere Standardwerte aus allen Rechnerfeldern zentral erfassen und mit Quellcode/Tests abgleichen. |
| Mittel | Berechnungsdetails der Vermietungs- und Fix-&-Flip-Kennzahlen je Eingabefeld eindeutig dokumentieren; Renditebasis und berücksichtigte Kosten bestätigen. |
| Mittel | Headerhöhe, Sticky-Verhalten und alle Rechnerwechsel auf Desktop und Mobilgeräten erneut visuell abnehmen. |
| Offen | Sichere Anmeldung, serverseitige Speicherung und Datenbankanbindung planen; Adminwerte liegen derzeit lokal im Browser. |
| Offen | Steuer-/AfA-Erweiterung für Vermietung fachlich definieren und rechtlich prüfen, bevor sie als Rechenfunktion ergänzt wird. |
| Offen | Aktualisierungsrhythmus und Verhalten bei Ausfall/Lücken der Bundesbank-Reihe dokumentieren. |
| Hoch | Anbieter- und Impressumsangaben in `assets/site-settings.json` prüfen und durch freigegebene Unternehmensdaten ersetzen. |

