# Verbindliche UI-Standards für Neustart ImmoCheck

Stand: 12. November 2026. Diese Regeln halten die abgestimmte Darstellung fest,
damit spätere Änderungen dieselben Entscheidungen wiederverwenden. Sie gelten
für die öffentliche Website und deren gemeinsame Einbindung von Admin- und
Nutzeransichten. PDFs behalten ihre getrennte Druckgestaltung.

Neue ausdrückliche Produktvorgaben haben Vorrang. Bei einer solchen Änderung
auch diese Standards aktualisieren. Ältere Beschreibungen des historischen
Builds sind keine Begründung, erneut eine abweichende Seitenvariante einzuführen.

## 1. Gemeinsame Anwendung und Container

- Startseite, fünf Rechner sowie Mieterabrechnung, Preise, Warum ImmoCheck?
  und Immobilien ABC verwenden dieselbe Anwendung, dieselbe Header-Instanz und `.app > main.section`.
- Interne Wechsel zwischen diesen Ansichten erfolgen über den gemeinsamen
  Routencontroller ohne vollständigen Dokumentneustart. URL und Browserhistorie
  werden korrekt aktualisiert; Zurück und Vorwärts müssen funktionieren.
- Beim vollständigen Laden wird die gemeinsame App-Fläche erst sichtbar, wenn
  die zentralen Layouteinstellungen, Footer-Inhalte und die Header-Höhenberechnung
  angewendet wurden. `assets/initial-layout.js` läuft dafür bereits im HTML-Kopf;
  unsichtbare Elemente bleiben messbar (`visibility`, kein `display: none`).
  Nachgeladene Standard-/Admin-Typografie darf beim ersten Anzeigen keine
  Zwischenansicht erzeugen. Bei Verbindungsfehlern bleibt die gebündelte
  Konfiguration nutzbar; ein Sicherheits-Timeout verhindert dauerhaftes Ausblenden.
- Direkte URLs bleiben aufrufbar und enthalten bereits passende Überschrift,
  Beschreibung, Inhaltsmarkup und SEO-Metadaten. Sie starten die gemeinsame Anwendung.
- Der Aufruf `/` zeigt die Startseite, auch wenn zuvor ein Rechner verwendet wurde.
- Der Footer steht einmal als eigenes Element in `.app`, außerhalb von `main`.
- Die Anwendung füllt mindestens die Viewporthöhe. Kurze Inhalte wachsen zum
  Footer; lange Inhalte scrollen natürlich. Kein zusätzlicher innerer Seiten-Scrollbereich.
- Admin- und Nutzeransichten verwenden den nativen Dokumentfluss und die
  gemeinsame Markenleiste. Keine zweite Kopfzeile oder separate iframe-Seite.

## Desktop-Dichte: 75 %

- Ab 1024 px Browserbreite wird die gesamte Bildschirmdarstellung in Vorschau
  und Liveversion einheitlich auf 75 % skaliert (`assets/desktop-density.css`).
  Der Browser bleibt für die Abnahme auf 100 %; ein zusätzlicher Browserzoom
  multipliziert sich mit der Seitenskalierung.
- Unter 1024 px bleiben Tablet-/Mobilansichten unverändert. Druck/PDF und
  eingebettete Rechner erhalten ebenfalls keine zusätzliche Skalierung.
- Logo, Abstände, Farben, Buttons und Admin-Schriften bleiben an dieselben
  zentralen Regeln gebunden. Nachfolgende Pixelangaben sind Layoutwerte vor der
  Desktop-Skalierung, beispielsweise 250 px Logo → 187,5 px sichtbare Breite.
- Dynamische Header-Messungen müssen Bildschirmrechtecke in unskalierte
  Layoutwerte zurückrechnen. Keine zweite Skalierung der reservierten Höhe.
- Bei 100 % Browserzoom Desktopbreiten 1024/1440/1920 sowie den Wechsel zurück
  zu Mobil prüfen: kein horizontaler Überlauf, kein abgeschnittener Header,
  erreichbare Dialoge und gleichbleibende Höhe bei internen Seitenwechseln.

## 2. Header und Navigation

- Das Logo bleibt linksbündig in der weißen Markenleiste. Es wird ausschließlich
  **vertikal in der gesamten weißen Fläche zentriert**, einschließlich der
  Navigationszeile; keine horizontale Zentrierung der Logo-/Textgruppe.
  Desktop-Logo: 250 px breit und proportional skaliert. Der zweizeilige
  Beschreibungstext steht daneben, Anmelde-/Portalzugang und Navigation rechts.
  Auf breiten Ansichten sind Logo und Beschreibung über beide Rasterzeilen
  vertikal zentriert. Mobil bleibt das Logo links mit 176 px gemäß gemeinsamem Breakpoint.
- Beschreibung: „Immobilienrechner für“ / „Kauf, Sanierung und Investment“.
- Hauptnavigation: „Preise“, „Warum ImmoCheck?“, „Immobilien ABC“ in dieser Reihenfolge.
  Die Mieterabrechnung bleibt über `/nebenkostenabrechnung/` und ihre Startseiten-Kachel erreichbar.
  Immobilien ABC unter `/immobilien-abc/` öffnet im gemeinsamen Contentfenster mit Suche,
  Themenfiltern sowie 120 alphabetisch sortierten, aufklappbaren Begriffen mit Erklärung
  und Beispiel; keine zweite Header-, Footer- oder Navigationsinstanz.
- Die Admin-Bereichsauswahl verwendet auf Desktop und Mobil dasselbe
  aufklappbare „Admin-Menü“ mit aktivem Bereich im Auslöser und senkrechter Liste.
  Die Liste startet geschlossen und schließt nach Auswahl, Escape oder Außenklick.
  Keine dauerhafte horizontale Tab-Leiste nur auf Desktop.
- Mobile Hauptnavigation über das gemeinsame Burger-Menü; keine zusätzliche
  seiteneigene Navigation. Das aufgeklappte Menü sitzt unter der Markenleiste.
- Die drei Beschriftungen „Jetzt anmelden“, „Zum Nutzerportal“ und „Zum Adminportal“
  verwenden ausdrücklich dieselbe Schriftgröße (`--nic-body-font-size`, aktuell
  20 px in der veröffentlichten Konfiguration), Schriftstärke 700 und Zeilenhöhe 1,2.
  Diese Regel gilt für den Link und seinen Text-Span, unabhängig vom Anmeldestatus.
- Anmeldung, Nutzerportal und Adminportal verwenden dieselbe Buttonbreite und
  -höhe. Bereits vor der Authentifizierungsantwort wird die breiteste mögliche
  Beschriftung reserviert; ein Labelwechsel darf keine Größenänderung auslösen.
  Auf Desktop sind ab dem ersten Rendern mindestens 224 × 46 px reserviert,
  damit auch der Wechsel von der gebündelten zur gespeicherten Schriftgröße
  (aktuell 16 → 20 px) die Buttonfläche nicht verändert. Größere benutzerdefinierte
  Schriften dürfen bei Bedarf mehr Platz erhalten; mobil bleiben die Iconflächen 44 × 44 px.
- Anmelde-/Portalzugang verwendet den tatsächlichen Anmeldestatus. Auf schmalen
  Ansichten bleiben zugängliche Icon-Schaltflächen mit 44 × 44 px Bedienfläche.
- Startseite, Rechner und die drei Informationsseiten verwenden denselben
  Bildheader, dieselbe Typografie und dieselbe Höhenberechnung.
- Nur die aktive Ansicht bestimmt `heroTitle` und `heroText`. Die alte
  Rechnerinitialisierung darf weder Startseiten- noch Informationstitel überschreiben.
- Die Headerhöhe wird anhand aller Titel-/Beschreibungskombinationen für die
  aktuelle Breite und Typografie reserviert. Beim internen Wechsel bleibt sie stabil.
  Keine zweite Rücksetzlogik, die erst einen falschen Titel sichtbar schreibt.
- Kein seitenspezifisches Nachbauen von Logo, Grafik, Schriftgrößen oder Abständen.
- Startseite, alle fünf Kalkulatoren und alle Contentseiten (einschließlich Über uns,
  Kontakt und Anmeldung) verwenden denselben Bildheader und denselben Footer.
  Nur die aktiven Content-Felder `headerTitle` (max. 70 Zeichen) und
  `headerDescription` (max. 90 Zeichen) variieren je Seite. Leere Felder
  bleiben ohne Ersatztext und ohne Leerraum. Schriftgrößen, Logo, Layout,
  Header-Höhenmessung und Footer werden nicht je Route dupliziert.
- Admin- und Nutzeransichten sowie Rechtsansichten behalten ihre bestehenden
  Zugangs- und Inhaltslogiken; kein zusätzlicher Header oder Footer wird erzeugt.

- In den rechtlichen Ansichten zeigt die Zurück-Schaltfläche den Text „ZURÜCK“ mit linkem Pfeil und führt stets zur Startseite `/`, unabhängig von der zuvor geöffneten Rechnerseite.

## 3. Inhaltsseiten und Abstände

- Mieterabrechnung, Preise und Warum ImmoCheck? zeigen ihre H1 im Bildheader;
  die weiße Inhaltskarte wiederholt keine zweite H1.
- Weiße Inhaltskarte: zentriert, volle verfügbare Breite ohne zusätzliche schmale Textspalte,
  `border-box`, Rahmen 1 px `#e2e9e5`, Radius aus `--nic-brand-radius`.
- Karten-Innenabstand: 18 px auf Desktop und Mobil. Die gemeinsame Erklärbox ist der Standard für neue Contentkarten.
- Zwischen Unterkante der weißen Textkarte und Oberkante des Footers liegen
  **16 px**, wie auf den anderen Inhaltsseiten. Gemeinsamer Token:
  `--nic-content-footer-gap: 16px`. Bei den integrierten Informationsseiten setzt
  `main.section` diesen Abstand als unteren Innenabstand.
- Die zusammengeführte Mieterabrechnungsbox wächst bei kurzen Inhalten im verfügbaren Hauptbereich bis zum normalen Footer-Abstand mit. Sie übernimmt die Höhenregel der bisherigen Inhaltskarte; die gemeinsame Mindesthöhe der Rechner-Erklärboxen begrenzt sie nicht.
- Karte und Footer dürfen sich weder berühren noch überlagern. Den Abstand
  auch bei kurzen, langen und mobil umgebrochenen Inhalten erhalten.
- Keine leeren Buttons oder Platzhalter verwenden, um Desktop-Lücken zu kaschieren.
- Direkte Inhaltsseiten liefern nur ihren passenden Haupttext im HTML aus. Die
  für interne Rechnerwechsel benötigten inaktiven Formularfelder werden aus einem
  gemeinsamen externen Skript vor der Rechnerinitialisierung eingebunden. Auf
  Über uns und Kontakt enthält der ausgeblendete Bildheader keine Rechnertexte.

## 4. Texte, Typografie und Buttons

- Die serverseitige HTML-Filterung muss eingebettetes JavaScript und CSS
  unverändert erhalten. Umlaute, Trennstriche, Mittelpunkte und Symbole dürfen
  in dynamischen Rechnertexten nicht als HTML-Zeichencodes erscheinen. Ganze
  deaktivierte Blöcke einschließlich ihrer Skripte werden weiterhin entfernt.

- Markenleiste, Bildheader und Hauptinhalt verwenden `text-size-adjust: 100%`
  (einschließlich `-webkit-`), damit mobile Browser Texte beim Drehen nicht
  eigenständig vergrößern. Admin-Schriftgrößen und Browserzoom bleiben erhalten.

- Schriftfamilie und Größen für Fließtext, H1–H4, Untertexte und Hinweise kommen
  aus Admin → Layout und den gemeinsamen CSS-Variablen. Keine unabhängigen
  Schriftwerte nur für eine Informationsroute einführen.
- Die fixierte Rechner-Buttonleiste bleibt mit 5 px Abstand zum unteren Viewport-Rand.
- Farben, Button-Hintergrund, Button-Textfarbe und Button-Radius werden aus
  den zentralen Admin-Einstellungen übernommen, auch in Nutzer-/Profilansichten.
  Keine neuen fest kodierten dunklen Standardbuttons als Ersatz.
- Plus-Aufklappsymbole verwenden auf allen Rechnern dasselbe zentrale Layout.
  Admin → Layout → Style steuert Plusflächen-Hintergrund, Umrandungsfarbe,
  Zeichen-Größe (8–24 px) und Innenabstand zum Rand (0–6 px). Die Schaltfläche
  bleibt 38,4 × 38,4 px groß; die Werte sind so begrenzt, dass Pluszeichen,
  Innenabstand und Umrandung zusammen in diese Fläche passen. Änderungen gelten
  für `.plus-btn`, `.market-check-toggle` und die Plus-Pseudoelemente der
  aufklappbaren Rechnerkarten.
- Die drei Pluszeichen im dunklen Footer haben eine eigene Admin-Gruppe. Sie
  steuert Flächen-, Rand- und Zeichenfarbe sowie Zeichen-Größe (8–16 px) und
  Innenabstand (0–3 px) unabhängig von den Rechner-Pluszeichen. Das Footer-Icon
  bleibt 24 × 24 px; die Maximalwerte füllen die Fläche, ohne sie zu überragen.
- Texte nutzen die verfügbare Breite ihrer vorgesehenen Karte. Keine zusätzliche
  schmale Textspalte oder versteckte `max-width` innerhalb der Einführung.
- HTML-Sprache `de`; längere deutsche Texte mit automatischer Silbentrennung
  (`hyphens: auto`, Safari zusätzlich `-webkit-hyphens: auto`). Wörter nicht
  willkürlich mit `word-break: break-all` trennen. Keine festen Zeilenumbrüche
  zur Korrektur einer einzelnen Bildschirmbreite.
- Inhalte wachsen mit der eingestellten Schriftgröße. Überschriften, Buttons
  und Untertexte weder abschneiden noch auf feste Texthöhen begrenzen.
- Sichtbare Bezeichnungen: „Mieterabrechnung“, „Warum ImmoCheck?“ sowie am
  Startseitenbutton „Nebenkosten abrechnen“ mit Dokument-Symbol und
  Untertext „Betriebskosten erfassen und versenden“. Die Gruppenüberschrift lautet
  „Mieterabrechnung“. Das Symbol steht bereits im HTML, auch bei internem
  Wechsel zur Startseite.
- Titel, Texte und Zielverknüpfung des Mieterabrechnungsbuttons bleiben wie die
  anderen Inhalte zentral konfigurierbar. Die Startseiten-Einstellungen liegen
  unter `meta.website`; keine zweite unabhängige Text-/Linkquelle pflegen.

## Startseiten-Einführung und spezielle Hinweistexte

- Die bestehende Startseiten-Einführungsbox (`nic-home-copy`) steht innerhalb des Hauptinhalts **vor** den Gruppen mit Rechner- und Mieterabrechnungsbuttons. Zwischen Einführung, Buttongruppen und Footer gelten weiterhin die vorhandenen zentralen Abstandsregeln; die Einführungsbox erhält keine künstliche Höhenstreckung.
- Im Budget-Rechner erscheint die Ergänzung zum Eigenkapital nicht mehr rechts in der Feldüberschrift, sondern als eigener Hinweis direkt unter dem Eingabefeld mit dem Wortlaut „Frei verfügbarer Betrag“.
- Der Hinweis „geändert (bitte prüfen)“ beim Fix-und-Flip-Verkaufspreis und der Eigenkapital-Hinweis nutzen die zentrale Schriftgröße `--nic-hint-font-size` aus Admin → Layout → Hinweistexte (px); bestehende Farben und Funktionslogiken bleiben unverändert.

- Auf Mobilgeräten stehen „Notar + Grundbuch“ und „Makler beim Kauf“ in den Kaufnebenkosten-Eingaben jeweils auf einer eigenen Zeile über die volle verfügbare Breite, in dieser Reihenfolge. Desktop-Spalten und bestehende Eingaben/Berechnungen bleiben erhalten.

## Ergebnisboxen der Rechner

- Ergebnisraster werden je Rechner anhand der Zahl sichtbarer Kacheln
  ausbalanciert und bleiben bei höchstens vier Boxen pro Desktop-Zeile: Fix & Flip
  zeigt acht Standard-KPIs als 4 + 4; mit aktiver Marktdifferenz als 3 + 3 + 3.
  Eigenheim zeigt nur seine acht Kauf- und Monatskosten-KPIs als 4 + 4; die
  projektbezogenen KPIs „Dein Geld im Projekt“ und „Maximal vertretbarer Kaufpreis“
  bleiben dort ausgeblendet. Der Eigenheim-Budgetübertragungsbereich erscheint
  nicht im Fix-&-Flip-Modus. Sechs Budget-Kacheln stehen als 3 + 3;
  sieben Vermietungsergebnisse als 4 + 3. Bei neun Boxen gilt 3 + 3 + 3.
  Einzelne Restboxen werden vermieden, wenn eine gleichmäßigere Spaltenzahl passt.
- Mobilgeräte zeigen eine Kachel pro Zeile. Lange Inhalte bleiben innerhalb
  ihrer Kachel lesbar.
- Werte und direkt anschließende Texte oder Einheiten behalten sichtbar einen
  Abstand, auch wenn sie in einer Zeile umbrechen. Inline-Elemente dürfen in
  Rechnerkacheln nicht ohne Abstand aneinandergrenzen.
- Schieberegler und Eingabe-/Übernahmebereiche behalten ihre eigene Zeile und
  werden nicht in Ergebnisraster einsortiert.
- Im Zinsszenario der Anschlussfinanzierung stehen die Markierungen „0 %“, der aktuelle Sollzins und „10 %“ linksbündig in einer Zeile beziehungsweise bei schmalem Platz linksbündig umbrochen.
- Das Zinsdiagramm trägt die Überschrift „Hypothekenzinsen – 10 Jahre“; die historische Datenreihe bleibt vollständig erhalten.
- Im Eingabebereich zur Immobilie lautet die Feldbezeichnung „Grundstück“.
- Zwischen gemeinsamer Buttonleiste und Footer bleiben mindestens 16 px
  Layoutabstand, auch am Ende des Scrollbereichs. Dies gilt für Desktop, Mobil,
  Querformat und Tablet sowie alle fünf Rechner. Die Desktop-Skalierung bleibt
  gemäß Abschnitt Desktop-Dichte erhalten. Der davon unabhängige Sticky-Abstand
  zum unteren Fensterrand bleibt 5 px.
- Finanzierung und Restschuld stehen als normaler DOM-Abschnitt im gemeinsamen
  `main.section`-Rahmen. Das Ergebnisraster verwendet dieselben Layoutregeln wie
  die anderen Rechner; Finanzierungselemente erhalten eindeutige IDs und lokal
  begrenzte Sonderregeln, damit keine Eingabefelder oder Styles anderer Rechner
  überschrieben werden.

## Erklärboxen der sechs Werkzeuge

- Budget, Eigenheim, Vermietung, Fix & Flip, Finanzierung und Mieterabrechnung
  erhalten genau eine gemeinsame Erklärbox direkt unter dem Grafikheader.
  Andere Ansichten erhalten keine fremden Erklärtexte. Auf der Mieterabrechnung werden Produkt-Einleitung und Erklärung in genau einer Box zusammengeführt; keine zusätzliche untere Textbox. Rechnerfunktionen bleiben erhalten.
- Quelle: `assets/site-settings.json` → `content` und Admin → Content; je Box etwa 1.000 Zeichen mit
  H2, einleitendem Absatz und zwei ergänzenden H3-/Textabschnitten. Keine Kopie
  der Überschrift oder Beschreibung aus dem Grafikheader. Deutschlandbezug und
  passende interne Links verwenden, keine unbelegten Leistungsversprechen.
- Alle sechs Boxen sind unter Admin → Content bearbeitbar. `description` enthält den vollständigen Text als HTML; der erste Absatz bildet die mobile Einleitung. Bei Mieterabrechnung bleibt der Bildheader-Titel getrennt von `boxTitle`. Neue/angepasste Inhalte ersetzen die Anzeige und werden bei der Höhenmessung berücksichtigt.
- Die bestehende Server-Schnittstelle speichert die normalisierten Contentdaten kompatibel unter `meta.content`; `content` und `meta.content` referenzieren im Frontend dieselben Daten. Beim Laden werden beide Formate unterstützt. Keine zweite redaktionelle Quelle und keine Änderung an Datenbank, Zugangsdaten oder Serverinstallation.
- Schriftfamilie sowie Fließtext-, H2- und H3-Größen kommen unverändert aus
  Admin → Layout. Farben und Radius bleiben an die gemeinsamen Variablen gebunden.
- Bei gleicher Fensterbreite und Typografie haben alle Boxen dieselbe minimale
  Höhe: vollständiger Text auf Desktop, eingeklappte Fassung mobil. Die größte
  benötigte Höhe wird ohne Abschneiden aus allen sechs Texten ermittelt; die
  Desktop-Skalierung wird dabei berücksichtigt.
- Mobil (bis 760 px bzw. gemeinsame schmale Querformatansicht) zunächst nur
  Titel und erster Absatz; rechts unten steht `weiterlesen`. Ein natives
  `details`/`summary` öffnet die beiden restlichen Abschnitte. Danach kann über
  `weniger anzeigen` geschlossen werden. Beim neuen Seitenaufruf bzw. Wechsel
  zu einem anderen Werkzeug beginnt die mobile Box wieder eingeklappt.
- Der vollständige Text steht bereits im HTML der direkten Route, auch mobil.
  Öffnen erfordert keinen Netzwerkabruf; Tastaturbedienung bleibt möglich.

## 5. Startseite

- Desktop: Mieterabrechnung links; daneben Kaufplanung mit Budget und
  Finanzierung. Darunter Objektprüfung mit Eigennutzung, Vermietung und Fix & Flip.
- Mobil: Gruppen und sämtliche Buttons untereinander, innerhalb der verfügbaren Breite.
- Unter den Button-Gruppen steht die Contentbox „Startseite · Einführung“ mit
  dem konfigurierten Einführungstext. Sie nutzt die volle verfügbare Kartenbreite.
- Rechnerbuttons verwenden die bestehenden gemeinsamen Controls, Symbole und
  Zustandsregeln. Keine zweite visuell abweichende Button-Familie.

## 6. Footer

- Ein gemeinsamer Footer auf allen Ansichten; Breite am App-Container ausrichten,
  keine JavaScript-Nachmessung oder seitenspezifische Verschiebung.
- Bereiche „Folge uns“, „Über uns“, „Kontakt“ sowie die gemeinsamen rechtlichen
  Links und Cookie-Einstellungen wiederverwenden. Keine doppelten Footer-Blöcke.
- Wenn keine Social-Media-Einträge gepflegt sind, steht auf Desktop „Über uns“
  links oben und „Kontakt“ rechts oben. Die rechtlichen Links bleiben darunter
  über beide Spalten. Die vorhandene Social-Sichtbarkeit steuert dies per CSS;
  keine zusätzlichen Serverabfragen oder nachträgliches Verschieben von DOM-Knoten.
  Mit Social-Einträgen gilt das bisherige Raster.
- Mobil im Hochformat bis 700 px behalten die drei Bereiche ihre vorhandenen Aufklappfunktionen und Abstände. Vor den Überschriften stehen die Symbole Nutzergruppe, Blatt und Brief; die rechtlichen Links bleiben direkt sichtbar und zentriert.
- Alle anderen Ansichten verwenden nebeneinanderliegende sichtbare Bereiche mit senkrechten Trennlinien. Ohne Social-Einträge stehen „Über uns“ links und „Kontakt“ rechts. Darunter steht ein eigener, zunächst geschlossener Bereich „Rechtliches“ mit Schildsymbol; er enthält dieselben rechtlichen Links und den vorhandenen Cookie-Hinweis. Beim Wechsel zurück zum mobilen Hochformat sind diese Links direkt sichtbar.
- Sichtbarkeitsregeln, zentrale Farben/Schrift-/Plus-Einstellungen, der äußere Footer-Abstand und alle Linkziele bleiben erhalten.
- Farben und Typografie kommen aus den gemeinsamen Einstellungen. Deutsche
  Silbentrennung und normale Umbrüche auch im Footer erhalten.
- Der gemeinsame Abstand zum Inhalt bleibt 16 px; keine lokale Nullsetzung.

## 7. Zuständigkeiten im Code

| Bereich | Gepflegte Quellen / Build-Schritte |
| --- | --- |
| Gemeinsame Routen und aktive Ansicht | `assets/unified-calculator-navigation.js`, `scripts/build_unified_navigation.py` |
| Erklärboxen / mobiles Weiterlesen | `assets/site-settings.json`, `assets/calculator-explanations.js`, `.css`, `scripts/build_calculator_explanations.py` |
| Gemeinsame Desktop-Skalierung | `assets/desktop-density.css`, Einbindung über `scripts/build_unified_navigation.py` |
| Erste stabile Darstellung | `assets/initial-layout.js`, Einbindung über `scripts/build_unified_navigation.py` |
| Bildheader und Höhenreservierung | `assets/stable-header.js`, `assets/stable-header.css` |
| Markenleiste, Logo, responsiver Footer | `assets/immocheck-brand-theme.css`, `assets/header-layout.css` |
| Einstellungen, Meta, Ansichtsanbindung | `assets/site-settings.js`, `assets/site-integration.js` |
| Startseite und integrierte Informationskarten | `assets/homepage.html`, `assets/homepage.css` |
| Direkte Inhaltsrouten und gemeinsame Shell | `scripts/build_settings_pages.py`, `scripts/finalize_shared_layout.py` |
| Gemeinsame Typografie | `scripts/centralize_layout_typography.py` |
| Verbindlicher Build und vollständige Prüfungen | `.github/actions/build-site/action.yml` |
| GitHub-Entwicklungsvorschau (`develop`) | `.github/workflows/pages.yml`, `scripts/prepare_github_preview.py` |
| Aktive STRATO-Veröffentlichung / isolierter Test | `.github/workflows/strato-production.yml`, `.github/workflows/strato-stage.yml` |

Die komprimierte Ausgangsseite und aktive historische Build-Patches werden
weiter verarbeitet. Deshalb die endgültige generierte Ausgabe prüfen; eine
Änderung in einem frühen Build-Schritt allein genügt nicht. `_site/` nicht als
Quellcode bearbeiten oder veröffentlichungsrelevante Änderungen nur dort ablegen.

## 8. Abnahme gemeinsamer UI-Änderungen

1. Startseite, alle fünf Rechner und alle drei Informationsseiten vergleichen.
2. Desktop und Smartphone prüfen; bei Header-/Footer-Änderungen auch Querformat.
3. Direkte URLs, interne Wechsel und Browser-Zurück/Vorwärts prüfen: richtige
   Titel/Metadaten, gemeinsame Headerhöhe, kein sichtbarer fremder Rechnertitel.
4. Schrift-/Farb-/Radius-Einstellungen aus dem Adminbereich berücksichtigen.
5. Weiße Inhaltskarte bis Footer prüfen: 16 px Abstand, keine Überlagerung,
   keine abgeschnittenen Texte oder horizontalen Überläufe.
6. Die erforderlichen Prüfungen des STRATO-Produktionsworkflows bestehen lassen. Die
   vorhandenen Browserprüfungen in `scripts/verify_unified_navigation.cjs` und
   `scripts/verify_calculator_styles.cjs` decken gemeinsame Navigation und Styles ab.

Weiterführende Architektur- und PDF-Beschreibung: [SHARED_LAYOUT.md](SHARED_LAYOUT.md).

## Eigenheim und Eigennutzung

- Die Route `/eigennutzung/` heißt in den Rechnerbuttons „Eigenheim & Eigennutzung“,
  mit Untertext „Immobilie kaufen und selbst nutzen“.
- Die H1 lautet „Kannst Du Dir Dein Eigenheim leisten?“. Die Seite erläutert
  Hauskauf und Eigentumswohnung sowie die manuelle Erfassung laufender Kosten.
- Der Budgetrechner prüft den allgemeinen Spielraum, der Eigenheim-Rechner eine
  konkrete Immobilie. Der Einführungstext ist auf der direkten Route im HTML
  vorhanden und bei internen Wechseln nur im Modus Eigennutzung sichtbar.

## Eingabefelder: Beispieltexte

- Keine grauen Platzhalter in Rechnereingaben; Ausnahme ist die Karte
  „Budget übernehmen“ (`#ownBudgetTransferCard`). Einheiten bleiben erhalten.
- Die Bereinigung gilt auch bei Einstieg über die Startseite/Inhaltsseiten und
  internen Rechnerwechseln. Finanzierung verwendet dieselbe Dokument-Typografie
  und keine separate Shadow-DOM-Ansicht.


## Nutzerdaten sichern und importieren

- Die Admin-Funktion „Nutzerdaten sichern“ exportiert Nutzerkonten als CSV mit den Spalten Vorname, Nachname und E-Mail. Der Import-Button steht rechts daneben in derselben Zeile.
- Der Import akzeptiert die unveränderte Sicherungsdatei, bis zu 2.000 Konten und 2 MB Dateigröße. Doppelte oder ungültige E-Mail-Adressen und fehlerhafte Zeilen werden vor dem Senden abgewiesen.
- Vorhandene Konten werden anhand der E-Mail-Adresse zugeordnet; nur Vor- und Nachname werden aktualisiert. Rollen, Sperrstatus und E-Mail-Bestätigung bleiben unverändert. Fehlende Konten werden als aktive, noch nicht bestätigte Benutzer angelegt.
- Die Verarbeitung ist auf Administratoren beschränkt, erfolgt transaktional und wird protokolliert. Die Serverroute lautet `users-import`; ihre API-Änderung wird erst mit dem separaten STRATO-Backend-Update wirksam.


## Admin: Inhaltszugang

- Die Tabelle zur H2-Inhaltssteuerung verwendet die Spalten „Inhalte“, „Anzeigen“ und „Nur Nutzer“. Ein aktiviertes Feld „Nur Nutzer“ beschränkt den Inhalt auf angemeldete Nutzer.
- Die drei Spalten bleiben auch auf schmalen Mobilansichten nebeneinander. Checkboxen sind kompakt, kontrastreich und ohne browserabhängige blaue Großflächen.
- Wenn „Anzeigen“ deaktiviert ist, entfernt der STRATO-PHP-Auslieferungsfilter das markierte HTML vor der Übertragung. Bei fehlender Konfiguration oder Datenbankverbindung liefert der Filter keine ungeprüfte Seite aus.

## Diagrammbeschriftungen

- SVG-Beschriftungen in Tilgungs- und Zinsdiagramm entsprechen sichtbar der Admin-Einstellung „Untertexte (px)“. Die Skalierung der SVG-viewBox wird ausgeglichen; die gemeinsame Desktop-Dichte von 75 % gilt wie für HTML-Untertexte.
- Bei Größenänderungen, Drehen des Geräts, Schriftwechsel und internem Rechnerwechsel neu messen. Jahresbeschriftungen auf schmalen Ansichten ausdünnen, ohne die Datenreihe zu kürzen; erstes und letztes Jahr erhalten.
- Nicht nur computed font-size prüfen: die tatsächlich gerenderte Schrift mit gleich eingestelltem HTML-Text vergleichen, einschließlich Mobil, Querformat, Tablet und breiten Desktopansichten.

## Immobilien ABC (15. November 2026)

- Begriffstitel: Grundschrift fett, Erklärung und Beispiel: Grundschrift, Themen- und Statusangaben: Untertext aus den Admin-Layout-Variablen.
- Suchfeld nimmt die gesamte verfügbare Contentbreite ein, mit Beispiel-Platzhalter „Begriff suchen, z. B. Grundschuld …“; diese Ausnahme betrifft nicht die platzhalterfreien Rechnereingaben.
- Über der Liste steht links „Begriffe von A bis Z“, rechts die Trefferzahl als „X Begriffe von 120 Begriffen“; die Anzahl reagiert auf Filter und Suche.
- Unter jedem fett gesetzten Begriffstitel steht die hellgraue Kategorie linksbündig, nicht am rechten Kartenrand.
- Auf Mobil sind Themenfilter horizontal scrollbar; Texte haben keine feste Höhe und bleiben barrierearm über native Details/Summary aufklappbar.
- Rechner-Infohilfen verlinken auf den zugehörigen Begriff und erhalten den gemeinsamen Routencontroller. Die bisherigen Rechnereingaben werden beim Wechsel nicht zurückgesetzt.
- Glossareinträge werden separat in `assets/immobilien-abc.json` gepflegt; Skript und Styles liegen unter `assets/`, der Build-Einbau unter `scripts/add_immobilien_abc.py`.
- Die neue Route wird nach dem vereinheitlichten Rechner-Build und vor der Fingerprint-Erzeugung ergänzt; STRATO-Live wird durch diesen Dev-Schritt nicht aktualisiert.

## Immobilien ABC: redaktionelle Verwaltung (15. November 2026)

- Neuer Admin-Menüpunkt „Immobilien ABC“ unmittelbar nach „Content“, in derselben nativen Admin-Navigation auf Desktop und Mobil.
- 120 Ausgangsbegriffe aus `assets/immobilien-abc.json` werden erstmals geladen. Jeder Datensatz besitzt Titel, Themengebiet, Erklärung und optionales Praxisbeispiel.
- Die Liste im Editor und die öffentliche Ausgabe werden alphabetisch nach Titel sortiert; neue Begriffe werden nach dem Bearbeiten einsortiert.
- „Hinzufügen“ erzeugt einen bearbeitbaren Datensatz; jedes Element hat rechts ein rotes X zum Löschen mit Bestätigungsdialog. Speichern und Zurücksetzen verwenden die bestehenden Admin-Aktionen.
- Der veröffentlichte Datenstand wird als JSON-Zeichenfolge unter `meta.immobilienABC` in den zentralen Website-Einstellungen gespeichert. Damit bleibt die bestehende Server-Schnittstelle kompatibel (sie akzeptiert die Metadaten ohne neue Tabellen und ohne neue Freigaberoute).
- Der öffentliche Router zeigt gespeicherte Begriffe statt Ausgangsdatei, wenn solche Einstellungen verfügbar sind; andernfalls dient die Datei als Fallback.
- Die Suchzeile nutzt unabhängig von vererbten Form-CSS-Regeln die gesamte verfügbare Breite der Inhaltskarte. Platzhalter: „Begriff suchen, z. B. Grundschuld …“.

## Kontextbezogenes Immobilien ABC in den Rechnern (16. November 2026)

- Fachbegriffe erhalten eine zarte, gepunktete Unterstreichung und öffnen eine Infobox im aktuellen Rechner, ohne Seitenwechsel und ohne Rücksetzen der Eingaben.
- Die allgemeine Begriffsdefinition bleibt im Immobilien ABC zentral bearbeitbar. Erklärungen aus bisherigen Rechner-Infoboxen werden zusätzlich im selben Dialog ausgegeben; in Vermietung bleiben insbesondere die vollständigen Abschnitte „Einfach gesagt“ und „Gut zu wissen“ erhalten.
- Als Sicherung wird beim Build vor der Integration eine maschinenlesbare Inventur der bisherigen Info-Schaltflächen erzeugt: `immobilien-abc-legacy-audit.json`. Die vollständigen mehrteiligen Vermietungserklärungen werden separat unter `immobilien-abc-context.json` konserviert.
- Fehlende Begriffe aus den geprüften vollständigen Miet-Erklärungen werden ohne Überschreiben bestehender Einträge zur generierten ABC-Datenbasis ergänzt; die 120 Ausgangsbegriffe bleiben vollständig erhalten.
- Bestehende Infoknöpfe werden nur dann ausgeblendet, wenn die erforderlichen Inhalte in der neuen Darstellung verfügbar sind. Noch nicht sicher migrierte Hinweise dürfen nicht verloren gehen.
- Der Browser-Regressionstest überprüft die Erklärung, die zusätzlichen Abschnitte sowie unveränderte URL, Dokumentinstanz und Rechnerwerte nach dem Schließen.

### Vollständiger Abgleich der historischen Info-Logik

- Der Dev-Build extrahiert die 20 vollständigen Hilfetexte aus dem vorhandenen Fix-&-Flip-`info`-Objekt sowie die neun strukturierten Vermietungs-Hinweise, jeweils mit Haupttext, „Einfach gesagt“ und „Gut zu wissen“.
- Historische Feldschlüssel und KPI-Titel werden aus dem tatsächlich generierten HTML zugeordnet; unbekannte Schlüssel verhindern ein stilles Entfernen der alten Information.
- Die Kontextansicht ersetzt die Symbole auch bei Fix-&-Flip-Kennzahlen und bei den beiden Vermietungskennzahlen „Monatlicher Cashflow“ und „Kaufpreisfaktor“. Der Link ist der dezent punktiert unterstrichene Feld- bzw. Kennzahlentitel.
- Automatische Tests stellen für ausgewählte Feld- und KPI-Typen sicher, dass kein Seitenwechsel erfolgt und die Originalabschnitte weiterhin abrufbar sind. Die initialen 120 ABC-Einträge bleiben erhalten, die ergänzten Begriffe werden alphabetisch eingeordnet.

### Finanzierungsrechner: Anschlussfinanzierung (16.11.2026)

- Nach der weißen Karte „2. Finanzierungsergebnis“ beginnt eine eigenständige weiße Contentkarte mit der H2 „3. Anschlussfinanzierung“.
- Die Karte verwendet die bestehenden gemeinsamen Klassen und Abstände (`card`), ohne gesonderte Farben, Abmessungen oder mobile Layoutvarianten.
- Zinsszenarien, Schieberegler, historische Zinsgrafik, Beschriftungen, Datenquelle und Berechnungslogik verbleiben unverändert in der neuen Karte.


### Rechnerauswahl ausschließlich Mobil Portrait (16.11.2026)

- Die Auswahlbox erscheint **auf allen öffentlichen Unterseiten**, aber **niemals auf der Startseite**, ausschließlich im Hochformat bis 700 px. Das gilt für alle fünf Rechner, Mieter-Abrechnung, Preise, Warum ImmoCheck?, Immobilien-ABC, Über uns, Kontakt und Anmelden.
- Freigegebene Variante: **eine durchgehend dunkelgrüne, außen abgerundete Auswahlleiste** mit „Rechner auswählen →“ links und dem aktiven Rechner rechts in einem leicht helleren grünen Bereich samt Pfeil nach unten. Das weiße Trägerfeld hat ringsum gleichmäßige Innenabstände, alle vier äußeren Ecken folgen dem Admin-Menü-Radius (`--nic-menu-radius`). Das geöffnete Menü ist eine weiße Dropdown-Karte mit Rechner-Icons, Trennlinien und einem hellgrün hervorgehobenen aktiven Eintrag samt Haken. **Alle Texte der Auswahlleiste und Optionsliste** verwenden die Admin-Einstellung „Untertexte (px)“ (`--nic-subtext-font-size`).
- Das Dropdown zeigt die fünf Rechner und als letzten auswählbaren Eintrag „Mieter-Abrechnung“. Auf Inhaltsseiten ist **Budgetrechner** als Standard vorausgewählt; es wird kein Platzhalter („Rechner auswählen“ / „Bitte wählen“) im Dropdown angelegt. Die Vorauswahl verändert den Inhalt der gerade geöffneten Seite nicht, bis ein Menüwechsel erfolgt.
- Auf Rechner- und gemeinsamen Inhaltsseiten wird die vorhandene `.deal-type-card` als **einzige** Navigation wiederverwendet: im Mobil-Hochformat im Bildheader, sonst an ihrem ursprünglichen Ort im Hauptinhalt. Keine zweite Kachelleiste und keine doppelte Routing-Logik.
- Reine Inhaltsseiten ohne Rechnerformular und ohne ursprüngliche Kachelleiste erzeugen über dieselbe Initialisierungsfunktion genau eine kompakte Navigation; sie bleibt außerhalb von Mobil Portrait unsichtbar. Die Auswahl eines Rechners lädt dort die vollständige Rechnerseite, während die gemeinsame Rechner-App weiterhin ohne kompletten Seitenwechsel navigiert.
- Auf Rechnerseiten in Mobil Portrait entfällt die große Kachelleiste. Der jeweilige Bildheader zeigt die mobile Überschrift „Jetzt [Rechnername] berechnen!“ mit kurzem Subtext. Die ausführliche Erklär-/SEO-Karte steht im Dokumentfluss nach den Rechnermodulen.
- Startseite, Querformat, Tablet/Desktop und rechtliche/adminstrative Überlagerungen auf der Startseite bleiben außerhalb dieser Porträt-Navigation.
- Vor Freigabe: alle Unterseiten, 320/375/390/430 px Hochformat, 700/701 px Übergang, sämtliche sechs Ziele, Browser-Zurück/Vorwärts, direkte Routen, Wechsel zwischen Hoch-/Querformat und Live-Layout-Radius testen.

- DEV-Freigabe: Die freigegebene grüne Mobil-Portrait-Auswahl wird über den GitHub-Pages-Workflow auf `develop` gebaut und getestet; keine automatische Veröffentlichung auf `main` oder STRATO.

### Rechnerauswahl: neue Screenshot-Vorgabe (16.11.2026)
- Mobil Portrait: ein durchgehender grüner Auslöser über die volle Breite, zentriert „Bitte Rechner wählen“, Pfeilsymbol rechts. Die bisherige linke Beschriftung entfällt.
- Auf Rechnerseiten und bei Mieterabrechnung zeigt das geschlossene Dropdown den aktiven Eintrag; auf sonstigen Inhaltsseiten steht „Bitte Rechner wählen“. Interne Navigation, direkte Aufrufe und Browser-Zurück/Vorwärts synchronisieren die Anzeige. Der aktive Eintrag bleibt in der Liste hervorgehoben.
- Geöffnete weiße Liste über die volle Breite, mit allen sechs vorhandenen Einträgen und unveränderten Originalsymbolen einschließlich Vermietung.
- Auslöser und Liste verwenden wieder direkt „Untertexte (px)“ (`--nic-subtext-font-size`, Standard 14 px), ohne 2-px-Abzug.
- Weißer Innenabstand 6 px, Gesamtbreite plus 2 px; bestehende äußere Grafikabstände, Admin-Radien und Bedienfunktionen bleiben erhalten.
- Diese neue Vorgabe ersetzt die älteren zweiteiligen Darstellungsregeln oben. Nur develop/GitHub-Entwicklungsvorschau.

- Feldbeschriftungen und ihre Einheiten stehen gemeinsam linksbündig mit kleinem Abstand; Einheiten wie (€), p. a. und jährlich werden nicht zum rechten Feldrand geschoben.

### Darlehensbetrag: Euro im Eingabefeld
- Finanzierungsrechner: „Darlehensbetrag“ ohne (€) im Label; € als hellgraue `.input-wrap .unit` rechts im Eingabefeld. Einheit nutzt `--nic-hint-font-size`, Beschriftung einschließlich Glossarlink nutzt `--nic-body-font-size` wie andere Feldbeschriftungen.

## Content-Editor: längere HTML-Inhalte und FAQ
- Content-HTML unterstützt bis zu 100.000 Zeichen, mit sichtbarem Zähler. Die Normalisierung kürzt längere Inhalte nicht still, sondern meldet eine Überschreitung.
- Content-Vorschau und öffentliche Inhalte verwenden denselben Filter für section/article, Klassen, IDs, ARIA sowie native details/summary-FAQ. Unbekannte harmlose Hüllen entfernen keine Texte; ausführbare Inhalte und Ereignisattribute bleiben ausgeschlossen.
- Eingebettetes CSS wird geparst und auf die jeweilige Contentbox begrenzt. Imports und URL-Ladevorgänge werden nicht übernommen. Rechtstexte behalten ihren getrennten Filter.
- Statisches HTML erhält Texte und FAQ-Struktur; CSS-Quelltext erscheint nicht als sichtbarer Text. Content-CSS wird beim Anwenden der Einstellungen lokal ergänzt.
- Keine automatische Übernahme von Beispieltext in veröffentlichte Inhalte; nur develop.

## Fünf Rechner: kompakte Contentbox im mobilen Hochformat
- Bis 700 px im Hochformat steht die Contentbox von Budget, Eigenheim, Vermietung, Fix & Flip und Finanzierung wieder zuerst unter dem Bildheader, vor den Rechnereingaben.
- Zunächst geschlossen: nur die ersten maximal zwei Titelzeilen plus „weiterlesen“. Der Einleitungsabsatz bleibt geschlossen unsichtbar; keine vom langen Text abgeleitete Mindesthöhe.
- „weiterlesen“ zeigt den vollständigen Titel, Einleitung und restlichen Text. Erneutes Schließen sowie Tastaturbedienung bleiben erhalten; beim Rechnerwechsel beginnt die Box geschlossen.
- Mieterabrechnung, Mobil-Querformat, Tablet/Desktop behalten ihre bisherige Darstellung. Alle Texte bleiben im DOM vorhanden und über dieselben Adminfelder bearbeitbar.

## Nummerierte Rechnerüberschriften auf allen Einstiegswegen
- Die bestehenden nummerierten Ergebnisüberschriften gelten auf direkten Rechner-URLs ebenso wie beim Einstieg über die Startseite und beim internen Wechsel. Der Build muss die Korrektur auf alle fünf Rechner anwenden, nicht nur index.html.
- Neuberechnung darf die nummerierten neutralen Ergebnistitel nicht durch alte Ampel-Überschriften ersetzen. Mobil und Desktop sowie direkte Aufrufe, interne Navigation und Eingabeänderungen im finalen Build prüfen.

## Objektdaten: gemeinsame Beschriftungszeile
- Wohnfläche / Preis pro m² sowie Baujahr / Grundstück stehen je Rasterzeile mit gleicher Oberkante der Eingabe- und Ergebnisboxen. Glossar-Unterstreichungen dürfen die Feldhöhe nicht verschieben.
- Zeilen richten sich über flexible, gemeinsame Beschriftungshöhen aus; Schriftgrößen, Umbruch, Einheiten und bestehendes responsives Raster bleiben erhalten.
