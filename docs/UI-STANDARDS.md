# Verbindliche UI-Standards für Neustart ImmoCheck

Stand: 10. November 2026. Diese Regeln halten die abgestimmte Darstellung fest,
damit spätere Änderungen dieselben Entscheidungen wiederverwenden. Sie gelten
für die öffentliche Website und deren gemeinsame Einbindung von Admin- und
Nutzeransichten. PDFs behalten ihre getrennte Druckgestaltung.

Neue ausdrückliche Produktvorgaben haben Vorrang. Bei einer solchen Änderung
auch diese Standards aktualisieren. Ältere Beschreibungen des historischen
Builds sind keine Begründung, erneut eine abweichende Seitenvariante einzuführen.

## 1. Gemeinsame Anwendung und Container

- Startseite, fünf Rechner sowie Mieterabrechnung, Preise und Warum ImmoCheck?
  verwenden dieselbe Anwendung, dieselbe Header-Instanz und `.app > main.section`.
- Interne Wechsel zwischen diesen Ansichten erfolgen über den gemeinsamen
  Routencontroller ohne vollständigen Dokumentneustart. URL und Browserhistorie
  werden korrekt aktualisiert; Zurück und Vorwärts müssen funktionieren.
- Direkte URLs bleiben aufrufbar und enthalten bereits passende Überschrift,
  Beschreibung, Inhaltsmarkup und SEO-Metadaten. Sie starten die gemeinsame Anwendung.
- Der Aufruf `/` zeigt die Startseite, auch wenn zuvor ein Rechner verwendet wurde.
- Der Footer steht einmal als eigenes Element in `.app`, außerhalb von `main`.
- Die Anwendung füllt mindestens die Viewporthöhe. Kurze Inhalte wachsen zum
  Footer; lange Inhalte scrollen natürlich. Kein zusätzlicher innerer Seiten-Scrollbereich.
- Admin- und Nutzeransichten verwenden den nativen Dokumentfluss und die
  gemeinsame Markenleiste. Keine zweite Kopfzeile oder separate iframe-Seite.

## 2. Header und Navigation

- Auf Desktop steht die gesamte Logo-/Textgruppe horizontal in der Mitte der
  weißen Markenleiste, unabhängig von der Breite des Anmelde-/Portalzugangs rechts.
  Die beiden äußeren Rasterspalten sind dafür gleich breit. Desktop-Logo: 250 px
  breit, proportional skaliert und vertikal über beide Beschreibungszeilen zentriert.
  Auf schmaleren Desktop-/Tabletansichten erhält der Portalzugang bei Platzmangel
  eine eigene Zeile. Mobil: Logo links mit 176 px gemäß gemeinsamem Breakpoint.
- Beschreibung: „Immobilienrechner für“ / „Kauf, Sanierung und Investment“.
- Hauptnavigation: „Mieterabrechnung“, „Preise“, „Warum ImmoCheck?“.
  Die bestehende Route `/nebenkostenabrechnung/` wird trotz Umbenennung beibehalten.
- Mobile Hauptnavigation über das gemeinsame Burger-Menü; keine zusätzliche
  seiteneigene Navigation. Das aufgeklappte Menü sitzt unter der Markenleiste.
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
- Bestehende Sonderansichten (z. B. Über uns/Kontakt ohne Bildheader sowie die
  gemeinsamen Rechtsansichten) nicht unbeabsichtigt durch eine neue Variante ersetzen.

## 3. Inhaltsseiten und Abstände

- Mieterabrechnung, Preise und Warum ImmoCheck? zeigen ihre H1 im Bildheader;
  die weiße Inhaltskarte wiederholt keine zweite H1.
- Weiße Inhaltskarte: zentriert, volle verfügbare Breite bis maximal 980 px,
  `border-box`, Rahmen 1 px `#e2e9e5`, Radius 16 px.
- Karten-Innenabstand: Desktop 32 px; bis 760 px Breite 24 px vertikal und 18 px horizontal.
- Zwischen Unterkante der weißen Textkarte und Oberkante des Footers liegen
  **16 px**, wie auf den anderen Inhaltsseiten. Gemeinsamer Token:
  `--nic-content-footer-gap: 16px`. Bei den integrierten Informationsseiten setzt
  `main.section` diesen Abstand als unteren Innenabstand.
- Karte und Footer dürfen sich weder berühren noch überlagern. Den Abstand
  auch bei kurzen, langen und mobil umgebrochenen Inhalten erhalten.
- Keine leeren Buttons oder Platzhalter verwenden, um Desktop-Lücken zu kaschieren.

## 4. Texte, Typografie und Buttons

- Schriftfamilie und Größen für Fließtext, H1–H4, Untertexte und Hinweise kommen
  aus Admin → Layout und den gemeinsamen CSS-Variablen. Keine unabhängigen
  Schriftwerte nur für eine Informationsroute einführen.
- Farben, Button-Hintergrund, Button-Textfarbe und Button-Radius werden aus
  den zentralen Admin-Einstellungen übernommen, auch in Nutzer-/Profilansichten.
  Keine neuen fest kodierten dunklen Standardbuttons als Ersatz.
- Texte nutzen die verfügbare Breite ihrer vorgesehenen Karte. Keine zusätzliche
  schmale Textspalte oder versteckte `max-width` innerhalb der Einführung.
- HTML-Sprache `de`; längere deutsche Texte mit automatischer Silbentrennung
  (`hyphens: auto`, Safari zusätzlich `-webkit-hyphens: auto`). Wörter nicht
  willkürlich mit `word-break: break-all` trennen. Keine festen Zeilenumbrüche
  zur Korrektur einer einzelnen Bildschirmbreite.
- Inhalte wachsen mit der eingestellten Schriftgröße. Überschriften, Buttons
  und Untertexte weder abschneiden noch auf feste Texthöhen begrenzen.
- Sichtbare Bezeichnungen: „Mieterabrechnung“, „Warum ImmoCheck?“ sowie am
  Startseitenbutton „Mieterabrechnung erstellen“ mit Dokument-Symbol und
  Untertext „Nebenkosten erfassen und Abrechnen“.
- Titel, Texte und Zielverknüpfung des Mieterabrechnungsbuttons bleiben wie die
  anderen Inhalte zentral konfigurierbar. Die Startseiten-Einstellungen liegen
  unter `meta.website`; keine zweite unabhängige Text-/Linkquelle pflegen.

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
- Desktop nutzt das gemeinsame Raster; mobil stehen die Bereiche untereinander
  und verwenden die bestehenden aufklappbaren Abschnitte.
- Farben und Typografie kommen aus den gemeinsamen Einstellungen. Deutsche
  Silbentrennung und normale Umbrüche auch im Footer erhalten.
- Der gemeinsame Abstand zum Inhalt bleibt 16 px; keine lokale Nullsetzung.

## 7. Zuständigkeiten im Code

| Bereich | Gepflegte Quellen / Build-Schritte |
| --- | --- |
| Gemeinsame Routen und aktive Ansicht | `assets/unified-calculator-navigation.js`, `scripts/build_unified_navigation.py` |
| Bildheader und Höhenreservierung | `assets/stable-header.js`, `assets/stable-header.css` |
| Markenleiste, Logo, responsiver Footer | `assets/immocheck-brand-theme.css`, `assets/header-layout.css` |
| Einstellungen, Meta, Ansichtsanbindung | `assets/site-settings.js`, `assets/site-integration.js` |
| Startseite und integrierte Informationskarten | `assets/homepage.html`, `assets/homepage.css` |
| Direkte Inhaltsrouten und gemeinsame Shell | `scripts/build_settings_pages.py`, `scripts/finalize_shared_layout.py` |
| Gemeinsame Typografie | `scripts/centralize_layout_typography.py` |
| Verbindlicher Veröffentlichungsablauf | `.github/workflows/pages.yml` |

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
6. Die erforderlichen Prüfungen des Pages-Workflows bestehen lassen. Die
   vorhandenen Browserprüfungen in `scripts/verify_unified_navigation.cjs` und
   `scripts/verify_calculator_styles.cjs` decken gemeinsame Navigation und Styles ab.

Weiterführende Architektur- und PDF-Beschreibung: [SHARED_LAYOUT.md](SHARED_LAYOUT.md).
