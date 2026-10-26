# Neustart ImmoCheck – Projektdokumentation

**Repository:** `TheRealKaio/fixflip-kalkulator`  
**Stand:** 26.10.2026 · Release V8.349  
**Produktivadresse:** <https://www.neustart-immocheck.de/>  
**GitHub-Pages-Adresse:** <https://therealkaio.github.io/fixflip-kalkulator/>

Diese Dokumentation beschreibt den Repository-Stand, die Menüpunkte und die tatsächlich verwendeten Rechenregeln. Sie orientiert sich an der Feldreferenz der README-Beispielversion und wurde für die fünf aktuellen Rechner aktualisiert. Eingaben ohne direkten Recheneffekt sind als Informations- oder Vorbereitungseingaben gekennzeichnet.

Die veröffentlichte App wird im GitHub-Actions-Workflow aus der aufgeteilten gzip/Base64-Quelle unter `source/` gebaut und mit Dateien aus `assets/` sowie Verarbeitungsskripten aus `scripts/` ergänzt. Änderungen gehören in die jeweilige Quellkomponente; generierte `_site/`-Dateien werden beim Build neu erstellt.

## 1. Aktueller Stand

- Responsive Web-App auf GitHub Pages; die Produktivdomain `www.neustart-immocheck.de` wird mitveröffentlicht.
- Rechner: Budget, Eigennutzung, Vermietung, Fix und Flip sowie Finanzierungsrechner.
- Die fünf Rechner haben eigene Routen und teilen die Navigation, den stabilisierten Header, Admin-Einstellungen und PDF-Branding.
- `source/index.html.gz.b64.part*` enthält die komprimierte Hauptseite. Der Finanzierungsrechner liegt in `assets/financing.html`. Admin- und PDF-Bausteine liegen in `assets/`; der Build und die Versionsverarbeitung liegen in `.github/workflows/pages.yml` und `scripts/`.
- In der Anschlussfinanzierung heißen die drei Varianten „Zinssatz fällt“, „Zinssatz stabil“ und „Zinssatz steigt“. Die Beträge werden ohne Nachkommastellen angezeigt; „Zinssatz stabil“ ist gelb, „Zinssatz steigt“ rot.
- Die Projektdokumentation ist unter Admin → Layout als letzte Karte zum Herunterladen vorgesehen. Die PDF nutzt das vorhandene Berichtsbranding.
- Admin-Einstellungen werden lokal im Browser gespeichert. Eine serverseitige Anmeldung, zentrale Speicherung und Datenbank sind noch nicht eingerichtet.
- `assets/site-settings.json` enthält noch Platzhalterangaben zu Anbieter- und Impressumsdaten. Vor Bestätigung des öffentlichen Impressums müssen die freigegebenen Unternehmensdaten eingetragen werden.
- PDF-Berichte nutzen die gemeinsame Implementierung in `assets/pdf-reports.js` für Kopfbereich, Logo, Fußzeile und rechtliche Hinweise.

### Arbeitsrahmen für künftige Änderungen

- Dieses GitHub-Repository ist der maßgebliche aktuelle Quellstand. Vor Änderungen den Stand auf `main` prüfen; generierte `_site/`-Dateien nicht als Quelle bearbeiten. Rechner, Adminbereich und bestehende Funktionen bleiben erhalten, sofern eine Änderung sie nicht ausdrücklich betrifft.
- Die fünf Rechner bleiben über eigene Routen erreichbar. Neue oder geänderte Rechnerlogik muss Eingaben und gespeicherte Werte der übrigen Rechner erhalten. Finanzierungslogik und sonstige Formeln nicht stillschweigend vereinfachen oder ändern.
- Änderungen an der Hauptseite gehören in `source/` bzw. in die vorgesehenen Build-Patches; die eigenständige Finanzierungsseite liegt in `assets/financing.html`. Gemeinsame PDF-Berichte nutzen `assets/pdf-reports.js`. Release-Versionen werden durch den höchsten Patch-Dateinamen `scripts/patch*_v8*.py` festgelegt; der nächste Patch braucht deshalb eine höhere V8-Nummer.
- Admin-Vorschauen und „Lokal speichern“ ändern nur den aktuellen Browser. Globale Einstellungen werden über `assets/site-settings.json` veröffentlicht: Konfiguration exportieren, Datei im Repository ersetzen, committen und erfolgreichen Pages-Workflow abwarten.
- Header, Sticky-Verhalten und Navigation sollen auf allen fünf Rechnern derselben gemeinsamen Höhen- und Scrolllogik folgen. Gemeinsame Layoutregeln bevorzugt in den gemeinsamen Header-Dateien pflegen und Sonderregeln nur ergänzen, wenn die Produktanforderung sie begründet.
- Buttons unter „Rechtliche Pflichtangaben“ (`.legal-section-links button` in `assets/admin.css`) sollen flach ohne 3D-Schatten oder abweichende Rahmen bleiben; der Radius beträgt 9 px. Beim Social-Setup Logo, Favicon und Apple-Touch-Icon getrennt behandeln; das Website-Logo steuert den gemeinsamen Header. Richtwerte: Favicon 32 × 32 px oder ICO, Apple-Touch-Icon PNG 180 × 180 px.
- Die Domain `www.neustart-immocheck.de` wird derzeit über GitHub Pages ausgeliefert. Eine spätere Verlagerung der Live-Version zu STRATO oder eine Datenbank-/Loginlösung ist noch eine Architekturentscheidung; bestehende Domain-, Pages- und CNAME-Einstellungen bis zu einer geplanten Migration erhalten.
- Statistik bleibt zustimmungsabhängig. Finanz- und Objektdaten werden nicht an Google Analytics übermittelt. Serverseitige Anmeldung und zentrale Speicherung erst nach gesonderter Planung mit geschützter Konfiguration und passenden Geheimnissen umsetzen.

## 2. Navigation und Layoutregeln

Die Navigation führt zu den fünf Rechnern Budget, Eigennutzung, Vermietung, Fix und Flip und Finanzierung. Die Rechner sind über eigene Pfade erreichbar. Beim nächsten Aufruf wird der zuletzt verwendete Rechner geöffnet; direkte Rechnerlinks bleiben möglich.

- Rechner nutzen eine gemeinsame Kopfzeile, Navigation, Aktionsleiste und Footer-Logik. `assets/stable-header.js`, `assets/stable-header.css` und `assets/header-layout.css` stabilisieren den Header.
- Die Inhaltsbreite des Finanzierungsrechners beträgt höchstens 640 px. Karten, Eingaben und Schaltflächen passen sich schmalen Ansichten an.
- Die Schaltflächen für fünf und zehn Jahre in der Zinskurve haben gleiche Breite und bleiben auch auf Mobilgeräten lesbar.
- PDF-Berichte verwenden A4-Hochformat. Der Kopfbereich ist 34 mm hoch. Das Logo sitzt links bei x=16 mm; der Titel steht rechts daneben. Die Fußzeile führt Domain links bei x=16 mm, Version mittig bei x=105 mm und Seitenzahl rechts bei x=194 mm nahe y=289 mm.
- Ergebniszustände sind zusätzlich zur Farbe beschriftet.
- Währungswerte im Finanzierungsrechner verwenden die deutsche Locale. Die Oberfläche rundet auf ganze Euro; Zwischenwerte werden ungerundet weiterverarbeitet.

## 3. CSS- und PDF-Regeln

- Admin → Layout bearbeitet Schriftfamilie, Grundschriftgröße, H1 bis H4 sowie Hintergrund-, Text-, Button-Hintergrund- und Button-Textfarben. Farben müssen sechsstellige HEX-Werte haben. Ein Kontrastwert wird angezeigt; unter 4,5:1 erscheint ein Hinweis.
- Rechnerbereiche haben flexible Grid-Layouts. Bei schmalen Ansichten wechseln Ergebnisboxen und Buttons in eine einspaltige Darstellung.
- Die Finanzierungs-KPI verwenden `.kpi` als Basis. Die zweite Anschlussfinanzierungsbox („Zinssatz stabil“) erhält einen gelben Hintergrund, die dritte („Zinssatz steigt“) einen roten. Beschriftungen bleiben lesbar; Zahlen verwenden tabellarische Ziffern.
- `assets/pdf-reports.js` stellt gemeinsame Funktionen für Dokumenterstellung, Header, Footer, Logo und Disclaimer bereit. Kopfbereich dunkelblau (#0F172A), Logo auf weißem Feld, Footer mit Domain, Version und Seitenzahl. Neue PDF-Ausgaben sollen diese gemeinsame Implementierung verwenden.
- Die README-PDF wird im Admin-Tab „Layout“ als letzte Karte mit direktem Downloadlink angeboten. Der Build kopiert sie in den veröffentlichten Dokumentationspfad.

## 4. Formeln und Berechnungsregeln

### 4.1 Gemeinsame Formeln

In den folgenden Formeln bedeutet \(P\) Kaufpreis, \(K\) Darlehen, \(S\) Verkaufspreis bzw. angenommener Marktwert, \(A\) Wohnfläche und \(M\) Monatszahl. Prozentwerte werden als Dezimalzahl eingesetzt, sofern eine Formel nicht ausdrücklich mit „Prozent ÷ 100“ arbeitet. Geldwerte werden nur für die Anzeige gerundet.

| Feld / Kennzahl | Erklärung | Formel / Rechenlogik |
|---|---|---|
| Preis je m² | Vergleich von Kaufpreis und Fläche | \(P / A\), sofern \(A > 0\). |
| Grunderwerbsteuer | Abhängig vom gewählten Bundesland | \(P \times Grunderwerbsteuersatz\). |
| Notar und Grundbuch | Prozentwert auf den Kaufpreis | \(P \times Notar-/Grundbuchsatz\). |
| Makler beim Kauf | Prozentwert auf den Kaufpreis | \(P \times Käuferprovision\). |
| Kaufnebenkosten | Summe der Erwerbskosten | Grunderwerbsteuer + Notar/Grundbuch + Makler beim Kauf. |
| Sanierung inkl. Puffer | Summe der Gewerke mit Reserve | \(Sanierungsbasis \times (1 + Puffer\% / 100)\). |
| Finanzierungsbasis | Kauf und Sanierung; Nebenkosten abhängig von der Checkbox | \(P + Sanierung\ inkl.\ Puffer + (Kaufnebenkosten,\ falls\ mitfinanziert)\). |
| Bruttodarlehen | Anteil der Finanzierungsbasis | \(Finanzierungsbasis \times Finanzierungsquote\% / 100\). |
| Darlehen nach Eigenkapital | Kreditbetrag nach Eigenmitteleinsatz | \(\max(0,\ Bruttodarlehen - eingesetztes\ Eigenkapital)\). |
| Monatlicher Zins zu Beginn | Prozentualer Monatszins auf den Kreditbetrag | \(K \times Zins\% / 1.200\). |
| Monatliche Tilgung zu Beginn | Prozentualer Monatsbetrag | \(K \times Tilgung\% / 1.200\). |
| Vereinfachte Monatsrate | Summe aus anfänglichem Zins und anfänglicher Tilgung | \(K \times (Zins\% + Tilgung\%) / 1.200\). |
| Laufende Kosten gesamt | Monatliche Kosten über die eingetragene Dauer | Monatskosten \(\times M\). |
| Laufende Modellzinsen | Fix-und-Flip- und Eigennutzungsmodell | \(K \times Zins\% / 100 \times M / 12\). Die Zinsbasis sinkt im Projektmodell nicht mit der Tilgung. |
| Tilgung im Projektmodell | Kumulierte Tilgung, begrenzt auf das Darlehen | \(\min(K,\ K \times Tilgung\% / 100 \times M / 12)\). Tilgung reduziert die Restschuld, wird aber nicht als Zins- oder Projektkosten doppelt gezählt. |

Die Bundesländersteuersätze sind im Programm hinterlegt und bestimmen die Grunderwerbsteuer. Prozentwerte, Finanzierungsquoten und Laufzeiten werden auf nichtnegative Werte begrenzt, wo die Rechnerlogik dies vorsieht.

### 4.2 Budget

Der Budgetrechner ermittelt aus Haushaltswerten, laufenden Ausgaben und Finanzierungsannahmen eine tragbare Monatsrate und daraus einen orientierenden Immobilienpreis.

| Feld / Kennzahl | Erklärung | Formel / Rechenlogik |
|---|---|---|
| Haushaltsnettoeinkommen | Summe aus Beschäftigung, Rente, Unterstützung, Nebeneinkommen, Mieteinnahmen und sonstigem Einkommen | Summe der sechs Einkommensfelder. Ändert sich das Gesamteinkommen, wird das Beschäftigungseinkommen als Differenz zu den übrigen Komponenten angepasst. |
| Kindergeld | Zusätzliche monatliche Einnahme | Standardmäßig Kinderzahl \(\times 259 €\); manuell geänderter Wert bleibt erhalten. |
| Gesamte Einnahmen | Einnahmen für die Haushaltsrechnung | Haushaltsnettoeinkommen + Kindergeld. |
| Lebensmittel | Haushaltsausgabenvorschlag | Erwachsene \(\times 300 €\) + Kinder \(\times 160 €\); manuelle Eingabe kann den Vorschlag ersetzen. |
| Mobilität | Haushaltsausgabenvorschlag | Erwachsene \(\times 220 €\) + Kinder \(\times 40 €\). |
| Versicherungen | Haushaltsausgabenvorschlag | Erwachsene \(\times 120 €\) + Kinder \(\times 20 €\). |
| Telefon und Internet | Haushaltsausgabenvorschlag | \(80 € + \max(0,\ Erwachsene - 1) \times 20 € + Kinder \times 10 €\). |
| Freizeit | Haushaltsausgabenvorschlag | Erwachsene \(\times 150 €\) + Kinder \(\times 100 €\). |
| Kinderkosten | Haushaltsausgabenvorschlag | Kinder \(\times 150 €\). |
| Sonstige Ausgaben | Vorschlagswert | 150 €; kann manuell angepasst werden. |
| Bestehende Kreditraten | Monatliche Belastung aus anderen Krediten | Direkte Eingabe; wird zu den Ausgaben addiert. |
| Gesamte feste Ausgaben | Summe der Haushaltsausgaben | Summe Lebensmittel, Mobilität, Versicherungen, Telefon/Internet, Freizeit, Kinderkosten, bestehende Kredite und sonstige Ausgaben. |
| Finanzierungsreserve | Automatische Reserve des Rechners | \(\max(300 €,\ 10\% \times \max(0,\ Gesamteinnahmen - feste\ Ausgaben))\). |
| Frei verfügbares Monatsbudget | Betrag nach Ausgaben und Reserve | \(\max(0,\ Gesamteinnahmen - feste\ Ausgaben - Finanzierungsreserve)\). |
| Budgetanteil für Kreditrate | Anteil des freien Budgets, der maximal für die Rate angesetzt wird | Eingabewert in Prozent, begrenzt auf 0–100 %. |
| Maximal tragbare Kreditrate | Monatliche Rate nach Budgetanteil | Frei verfügbares Monatsbudget \(\times Budgetanteil\% / 100\). Der Rest ist zusätzlicher Puffer. |
| Max. Darlehen | Aus der tragbaren Rate und den angenommenen Sätzen | \(Monatsrate \times 12 / (Zins\% + Tilgung\%)\); bei Summe 0 wird 0 ausgegeben. |
| Eigenkapital verfügbar | Zusätzliches Eigenkapital im Gesamtbudget | Direkte Eingabe. |
| Gesamtbudget | Gesamtes rechnerisches Kaufbudget einschließlich Eigenkapital | Max. Darlehen + Eigenkapital. |
| Grunderwerbsteuer / Notar / Makler | Erwerbsnebenkosten als Anteil am Kaufpreis | Bundeslandsatz + Notar-/Grundbuchsatz + Makler-Kaufsatz. Diese drei Komponenten bilden den angezeigten Gesamtprozentsatz. |
| Sonstige Kosten | Zusätzlicher Kostenanteil, z. B. Renovierung, Umzug oder Möbel | Eingegebener Prozentsatz vom Immobilienpreis. |
| Max. Immobilienpreis | Preis, der nach Prozentanteilen noch ins Gesamtbudget passt | \(Gesamtbudget / (1 + Kaufnebenkosten\% + SonstigeKosten\%)\). |
| Kaufnebenkosten / sonstige Kosten in Euro | Umrechnung der Kostenanteile auf den Immobilienpreis | Immobilienpreis \(\times jeweiliger\ Prozentsatz\). |
| Zins- und Tilgungsanteil zu Beginn | Aufteilung der maximal tragbaren Rate | Zins = Darlehen \(\times Zins\% / 1.200\); Tilgung = \(\max(0,\ Monatsrate - Zins)\). |
| Restschuld nach 10, 20 oder 30 Jahren | Modell mit gleichbleibender Monatsrate | Bei Monatszins \(r=Zins\%/1.200\) und \(n=12 \times Jahre\): \(K(1+r)^n - Monatsrate \times ((1+r)^n-1)/r\), mindestens 0. Bei \(r=0\): \(\max(0,K-Monatsrate \times n)\). |

Familienstatus und Haushaltsgrößen steuern die Vorschläge und Darstellung. Wenn Ausgaben manuell eingegeben werden, bleiben sie unabhängig von später geänderten Haushaltsvorschlägen erhalten.

### 4.3 Eigennutzung

Die Eigennutzungsrechnung verwendet gemeinsame Erwerbs-, Sanierungs- und Finanzierungsformeln aus 4.1. Sie stellt Kauf und Sanierung für die Selbstnutzung dar. Die Ampel für Projektziele, persönlichen Steuersatz und Stressszenarien des Fix-und-Flip-Rechners wird in diesem Modus nicht verwendet.

| Feld / Kennzahl | Erklärung | Formel / Rechenlogik |
|---|---|---|
| Marktwert nach Sanierung | Angenommener oder aus Vergleichen abgeleiteter Wert | Direkte Eingabe. Ist das Feld leer und gibt es keine gültigen Vergleiche, wird \(Anfangsinvestition / 0{,}90\) vorbelegt (10 % Wertpuffer). |
| Vergleich 1–3: Preis und Wohnfläche | Manuelle Vergleichsobjekte | Vergleichspreis je m² = Vergleichspreis / Vergleichsfläche; nur Paare mit Preis > 0 und Fläche > 0 zählen. |
| Geschätzter Marktwert heute | Hochrechnung aus Vergleichsobjekten | Arithmetischer Mittelwert der gültigen Vergleichspreise je m² \(\times\) Wohnfläche des Zielobjekts. |
| Orientierungsspanne | Unsicherheitsband um den geschätzten Marktwert | 1 Vergleich: ±10 %; 2 Vergleiche: ±7,5 %; 3 Vergleiche: ±5 %. |
| Abweichung Kaufpreis | Differenz zum geschätzten heutigen Marktwert | Euro = Kaufpreis − Marktwert; Prozent = Euro-Differenz / Marktwert. Unter −5 %: unter Vergleichsniveau; bis +5 %: marktüblich; bis +10 %: leicht erhöht; über +10 %: deutlich erhöht. |
| Energieeffizienzklasse | Kann den maximal vertretbaren Kaufpreis beeinflussen | Energieabschlag: Marktwert \(\times Klassenabschlag\). A+ bis D: 0 %; E: 3 %; F: 5,5 %; G: 8,5 %; H: 12,5 %. Energiebedarf in kWh/(m²·a) ist ein Informationswert und wirkt nicht direkt auf die Kostenrechnung. |
| Anrechenbare energetische Sanierung | Verhindert einen doppelten Abzug energetischer Gewerke | Summe Dach, Fassade, Wärmeerzeuger, Heizung und Fenster \(\times (1 + Puffer\% / 100)\). |
| Verbleibender Energieabschlag | Nur noch nicht durch energetische Gewerke abgedeckter Anteil | \(\max(0,\ Bruttoenergieabschlag - anrechenbare\ energetische\ Sanierung)\). |
| Maximal vertretbarer Kaufpreis | Kaufpreisgrenze nach Marktwert, Sanierung, Erwerbskosten und Energierisiko | \(\max(0,\ (Marktwert - Sanierung\ inkl.\ Puffer - verbleibender\ Energieabschlag) / (1 + Erwerbsnebenkostenquote))\). |
| Differenz zum Marktwert nach Sanierung | Rechnerischer Wertpuffer bei einem späteren Verkauf | Marktwert − Kaufpreis − Kaufnebenkosten − Sanierung inkl. Puffer − Verkaufsmakler − weitere Verkaufskosten. Zinsen und laufende Kosten sind in dieser Kennzahl nicht abgezogen. |
| Monatliche Kreditrate | Anfangszins plus Anfangstilgung | Darlehen \(\times (Zins\% + Tilgung\%) / 1.200\). |
| Monatliche Gesamtbelastung | Kreditrate plus eingegebene laufende Kosten | Monatszins + Monatstilgung + laufende Kosten pro Monat. |

Baujahr, Grundstücksfläche, PLZ/Ort, Objektart und Zustand sind Angaben zur Einordnung oder Vorbereitung einer späteren Bewertungs-API. Sie beeinflussen die manuelle Vergleichsrechnung nicht direkt. Die Vergleichsobjekte werden derzeit gemittelt; die Oberfläche nennt den angezeigten Wert „Ø Vergleichspreis“.

### 4.4 Vermietung

Die Vermietung berechnet laufende Einnahmen, nicht umlagefähige Eigentümerkosten und eine vereinfachte Finanzierung. Die gesamte Hausgeldzahlung wird angezeigt bzw. erläutert, aber nur der eingegebene nicht umlagefähige Anteil fließt in die Kosten ein.

| Feld / Kennzahl | Erklärung | Formel / Rechenlogik |
|---|---|---|
| Kaufpreis je m² / Nettokaltmiete je m² | Einheitspreise zur Einordnung | Kaufpreis bzw. Monatsnettokaltmiete / Wohnfläche, sofern Fläche > 0. |
| Grunderwerbsteuer | Bundeslandsatz auf den Kaufpreis | Kaufpreis \(\times\) Bundeslandsatz. |
| Notar und Makler | Eingegebene Prozentsätze auf den Kaufpreis | Kaufpreis \(\times (Notar\% + Makler\%)\). |
| Kaufnebenkosten | Summe der Erwerbskosten | Grunderwerbsteuer + Notar/Grundbuch + Makler beim Kauf. |
| Gesamtinvestition | Kaufpreis, Erwerbsnebenkosten und Modernisierung | Kaufpreis + Kaufnebenkosten + einmalige Modernisierung inkl. Puffer. |
| Eingesetztes Eigenkapital | Tatsächlich angesetzter Anteil des eingegebenen Eigenkapitals | \(\min(Eigenkapital,\ Gesamtinvestition)\). |
| Darlehen | Verbleibender Finanzierungsbedarf | \(\max(0,\ Gesamtinvestition - eingesetztes\ Eigenkapital)\). |
| Mietausfall / Leerstand | Sicherheitsabschlag auf die Nettokaltmiete | Eingabe in Prozent, auf höchstens 95 % begrenzt. Effektive Miete = Nettokaltmiete \(\times (1 - Abschlag)\). |
| Eigentümerkosten pro Monat | Kosten, die nicht auf den Mieter umgelegt werden | Nicht umlagefähiges Hausgeld + Verwaltung + zusätzliche Instandhaltung + sonstige Vermieterkosten. Hausgeld gesamt wird nicht zusätzlich addiert. |
| Kreditrate | Vereinfachte anfängliche Zins- und Tilgungsrate | Darlehen \(\times (Zins\% + Tilgung\%) / 1.200\). |
| Monatlicher Cashflow | Einnahmen nach Ausfall, Eigentümerkosten und Finanzierung | Effektive Miete − Eigentümerkosten − Kreditrate; vor Steuer. |
| Bruttomietrendite | Jahresnettokaltmiete bezogen auf den Kaufpreis | Nettokaltmiete pro Monat \(\times 12 / Kaufpreis\). Ohne Mietausfall-Abzug. |
| Nettomietrendite | Nettoertrag vor Finanzierung bezogen auf die Gesamtinvestition | (Effektive Jahresmiete − jährliche Eigentümerkosten) / Gesamtinvestition. |
| Rendite auf Eigenkapital | Jährlicher Cashflow bezogen auf angesetztes Eigenkapital | Monatlicher Cashflow \(\times 12 / eingesetztes\ Eigenkapital\). |
| Kaufpreisfaktor | Kaufpreis in Jahresnettokaltmieten | Kaufpreis / (monatliche Nettokaltmiete \(\times 12\)). |
| Tilgung / Vermögensaufbau | Rechnerische Tilgung im ersten Jahr | Darlehen \(\times Tilgung\% / 100\). |
| Break-even-Nettokaltmiete | Miete, bei der der modellierte Cashflow 0 € beträgt | (Eigentümerkosten + Kreditrate) / (1 − Mietausfallquote). |

Die Modernisierungsgewerke starten in der Vermietung bei 0 €. Graue Richtwerte werden erst durch „Vorschlag übernehmen“ Teil der Rechnung. Die zusätzliche Instandhaltung wird standardmäßig mit 1,50 €/m² Wohnfläche und Monat vorgeschlagen; eine manuelle Änderung bleibt bestehen. Baujahr und Grundstücksfläche dienen nur der Objektbeschreibung.

Die Ampel beschreibt ausschließlich den monatlichen Cashflow: ab 0 € positiv, von −100 € bis unter 0 € nahe am Break-even, unter −100 € negativ. Einkommensteuer, AfA, Mietsteigerungen, Wertentwicklung, Instandhaltungsbedarf über den gewählten Ansatz hinaus und Bankkonditionen sind nicht vollständig modelliert.

### 4.5 Fix und Flip

Fix und Flip verbindet Kauf, Sanierung, Projektdauer, Finanzierung, Verkaufskosten und Verkaufserlös. Das Finanzierungsmodell verwendet konstante Zinsen auf den ursprünglichen Kreditbetrag; sinkende Restschuld reduziert die angesetzten Zinskosten nicht.

| Feld / Kennzahl | Erklärung | Formel / Rechenlogik |
|---|---|---|
| Kaufpreis je m² | Kaufpreis im Verhältnis zur Wohnfläche | Kaufpreis / Wohnfläche, sofern Wohnfläche > 0. |
| Verkaufspreis nach Sanierung | Manuelles Verkaufsziel oder kalkulatorischer Wert | Wenn kein positiver manueller Wert eingegeben ist: \(Kosten\ vor\ Verkaufsmakler / (1 - Zielmarge - Verkaufsmaklerquote)\). Ist der Nenner ≤ 0, wird 0 angesetzt. |
| Zinsen gesamt | Vereinfachte Finanzierung über die Projektdauer | Kredit \(\times Zins\% / 100 \times Monate / 12\). |
| Tilgung gesamt | Rückzahlung im vereinfachten Modell | \(\min(Kredit,\ Kredit \times Tilgung\% / 100 \times Monate / 12)\). Sie reduziert den Kreditbetrag, ist aber kein zusätzlicher Projektaufwand. |
| Laufende Kosten gesamt | Monatliche Haltekosten über das Projekt | Laufende Kosten pro Monat \(\times Monate\). |
| Makler beim Verkauf | Verkaufskosten als Anteil am Verkaufspreis | Verkaufspreis \(\times Verkaufsprovision\% / 100\). |
| Projektkosten | Modellierte Erwerbs-, Umbau-, Finanzierungs- und Verkaufskosten | Kaufpreis + Kaufnebenkosten + Sanierung inkl. Puffer + Zinsen + laufende Kosten + Verkaufsmakler + weitere Verkaufskosten. |
| Projektgewinn | Ergebnis vor persönlicher Steuer | Verkaufspreis − Projektkosten. |
| Gewinn nach Steuer | Vereinfachte Steuer auf positive Gewinne | Gewinn − \(\max(0,\ Gewinn \times persönlicher\ Steuersatz\% / 100)\). Bei Verlust wird keine Steuererstattung berechnet. |
| Marge | Gewinnanteil am Verkaufspreis | Projektgewinn / Verkaufspreis. |
| Eigenes Geld im Projekt | Modellierter Kapitalbedarf nach Finanzierung | \(\max(0,\ Projektkosten - Darlehen)\). |
| Rendite auf eigenes Geld | Gewinn im Verhältnis zum benötigten Eigenkapital | Projektgewinn / eigenes Geld im Projekt; bei 0 € Eigenkapital wird 0 angezeigt. |
| Nullpunkt Verkauf | Verkaufspreis, bei dem der Gewinn 0 € erreicht | \((Projektkosten - Verkaufsmakler) / (1 - Verkaufsprovisionquote)\). |
| Sicherheitspuffer | Abstand des Verkaufspreises zum Nullpunkt | \((Verkaufspreis - Nullpunkt) / Verkaufspreis\). |
| Ziel-Gewinn | Mindestgewinn vor persönlicher Steuer | Vergleichswert für die Ampel und Abzug im maximal sinnvollen Kaufpreis. |
| Ziel-Marge | Zielwert als Anteil am Verkaufspreis | Gewinn / Verkaufspreis. Wird auch beim kalkulatorischen Verkaufspreis verwendet. |
| Max. eigenes Geld | Persönliche Obergrenze für gebundenes Eigenkapital | Ändert keine Kennzahl; markiert das Ziel als verfehlt, wenn eigenes Geld im Projekt darüber liegt. |
| Mindest-Rendite | Gewünschte Rendite auf eingesetztes Eigenkapital | Ändert keine Kennzahl; Vergleich von ROI und eingegebenem Mindestwert steuert die Zielprüfung. |
| Maximal sinnvoller Kaufpreis | Kaufpreisgrenze für den eingegebenen Verkaufspreis und Zielgewinn | Zähler = Verkaufspreis \(\times (1-Verkaufsmaklerquote) - Zielgewinn - (weitere Verkaufskosten + laufende Kosten) - Sanierung \(\times (1 + Finanzierungsquote \times Zins\%/100 \times Monate/12)\). Nenner = \(1 + Kaufnebenkostenquote + Finanzierungsquote \times Zins\%/100 \times Monate/12 \times (1 + Kaufnebenkostenquote,\ falls\ Kaufnebenkosten\ mitfinanziert)\). Ergebnis = \(\max(0,\ Zähler/Nenner)\). |
| Stress-Test Verkauf | Neu berechneter Gewinn bei niedrigerem Verkaufspreis | Verkaufspreis \(\times (1 - Stresswert\%/100)\); alle verkaufsabhängigen Kosten werden neu berechnet. |
| Stress-Test Sanierung | Neu berechneter Gewinn bei höherer Sanierungsbasis | Sanierungsbasis \(\times (1 + Stresswert\%/100)\); anschließend greift der Sanierungspuffer erneut. |

Baujahr, Grundstücksfläche, Energiebedarf und PLZ/Ort haben im Fix-und-Flip-Rechenmodell keine direkte mathematische Wirkung. Die Energieeffizienzklasse beeinflusst nur den Eigennutzungs-Kaufpreischeck.

### 4.6 Anschlussfinanzierung

Die Szenarien setzen die am Ende des Betrachtungszeitraums berechnete Restschuld und die eingestellte neue Anfangstilgung an. Sie sind Belastungsvarianten, keine Zinsprognosen.

| Szenario | Szenariozins | Angezeigte Monatsrate |
|---|---:|---:|
| Zinssatz fällt | eingestellter Sollzins − 1,5 Prozentpunkte | Restschuld \(\times (Szenariozins\% + Tilgung\%)/1.200\) |
| Zinssatz stabil | eingestellter Sollzins | Restschuld \(\times (Szenariozins\% + Tilgung\%)/1.200\) |
| Zinssatz steigt | eingestellter Sollzins + 2 Prozentpunkte | Restschuld \(\times (Szenariozins\% + Tilgung\%)/1.200\) |

Die Beträge werden als EUR ohne Nachkommastellen formatiert. Der Szenariozins wird zusätzlich ausgegeben. Während der ersten Zinsbindung sind Sondertilgungen jährlich am Jahresende berücksichtigt; für die Anschlussperiode nimmt der Hinweis konstante Rate und konstanten Zins an, ohne zusätzliche Sondertilgungen, Gebühren oder weitere Zinsänderungen.

### 4.7 Historische Hypothekenzinsen

Die Grafik zeigt bundesweite monatliche Effektivzinsen aus der Bundesbank-MFI-Zinsstatistik für Wohnungsbaukredite mit 1–5 und 5–10 Jahren anfänglicher Zinsbindung. Angezeigt werden rollierende zehn Jahre bis zum jüngsten verfügbaren Monatswert. Die Zeitreihe wird nach Möglichkeit aus dem veröffentlichten lokalen Datensatz gelesen und bei Bedarf direkt von der Bundesbank abgerufen. Fehlende Datenblöcke werden ausgelassen.

Der Finanzierungsrechner verwendet den eingestellten Sollzins. Die historischen Reihen zeigen Effektivzinsen und dienen nur zur Orientierung. Die Schaltflächen übernehmen den jüngsten Monatswert der passenden Zinsbindungsreihe in das Sollzinsfeld; sie erzeugen keine Zinsprognose.

## 5. Standardwerte und Eingaben

| Bereich | Repository-Stand |
|---|---|
| Finanzierungsrechner – Darlehen | 300.000 € |
| Sollzins p. a. | 4,01 % |
| Anfangstilgung p. a. | 1,5 % |
| Sondertilgung p. a. | 0 % |
| Betrachtungszeitraum | 10 Jahre |
| Budget – persönliche Beispielangaben | Nettoeinkommen, Einkommenskomponenten, Kindergeld und Eigenkapital starten neutral bei 0; Single, 1 Erwachsener, 0 Kinder. Haushaltsausgaben werden aus Vorschlägen vorbelegt. |
| Budget – Finanzierung | Ort standardmäßig Hamburg; Notar/Grundbuch 2 %, Makler beim Kauf 0 %, sonstige Kosten 5 %, Budgetanteil der Monatsrate 75 %. |
| Eigennutzung / Fix und Flip – Ort | Hamburg, PLZ/Ort 20095 Hamburg als voreingestellte Ortsangabe. |
| Vermietung | Bundesland Hamburg; Zinssatz 4 %, Tilgung 1,5 %, Notar 2 %, Makler 0 %, Mietausfall 2 %, Modernisierung und laufende Kosten starten bei 0 €. |
| Fix und Flip – Zielwerte | Zielgewinn 40.000 €, Zielmarge 10 %, max. eigenes Geld 100.000 €, Mindest-Rendite 25 %, persönlicher Steuersatz 42 %. |

Weitere Felder verwenden die Startwerte in der jeweiligen Quellkomponente. Benutzereingaben werden lokal im Browser gespeichert und können daher nach dem ersten Aufruf von den ursprünglichen Standardwerten abweichen.

## 6. Build, Tests und Veröffentlichung

Der Workflow `.github/workflows/pages.yml` läuft bei Änderungen an `main`, manuell und als regelmäßiger Fallback. Er entpackt die Hauptseite, wendet fest definierte Inhalts- und Layoutänderungen an, erzeugt Routen und Einstellungsseiten, kopiert Rechnerassets und Dokumente und prüft HTML/JavaScript, Rechnerlogik, PDFs, Metadaten und Assets. Erst nach erfolgreichen Prüfungen wird nach GitHub Pages veröffentlicht.

Für die Anschlussfinanzierung enthält `scripts/verify_finance_updates.js` Prüffälle für Monatsrate, Restschuld, Sondertilgung, Null-Darlehen, Ergebnisfarben, Downloadkarte und PDF-Datei. Ein Prüffall nutzt 300.000 € Darlehen, 4 % Sollzins, 2 % Tilgung und 5 % Sondertilgung über zehn Jahre. Der Release-Vertrag in `scripts/release_contract.py` leitet die sichtbare Versionsnummer aus dem neuesten `scripts/patch*_v8*.py`-Dateinamen ab.

## 7. Offene Aufgaben

| Priorität | Aufgabe |
|---|---|
| Mittel | Standardwerte aller Rechnerfelder zentral mit den Quellkomponenten abgleichen. |
| Mittel | Die Ergebnisse der Vermietungs- und Fix-und-Flip-Rechnung fachlich bestätigen, besonders Renditebasis und berücksichtigte Kosten. |
| Mittel | Headerhöhe, Sticky-Verhalten und Rechnerwechsel auf Desktop und Mobilgeräten erneut visuell abnehmen. |
| Offen | Sichere Anmeldung, serverseitige Speicherung und Datenbankanbindung planen; Adminwerte liegen derzeit lokal im Browser. |
| Offen | Steuer-/AfA-Erweiterung für Vermietung fachlich definieren und rechtlich prüfen, bevor sie als Rechenfunktion ergänzt wird. |
| Offen | Aktualisierungsrhythmus und Verhalten bei Ausfall oder Lücken der Bundesbank-Reihe dokumentieren. |
| Hoch | Anbieter- und Impressumsangaben in `assets/site-settings.json` prüfen und mit freigegebenen Unternehmensdaten ersetzen. |
| Mittel | Den Text der Schaltflächen für den 5- und 10-Jahreszins mit der tatsächlichen Übernahme des jüngsten Monatswerts abstimmen. |
