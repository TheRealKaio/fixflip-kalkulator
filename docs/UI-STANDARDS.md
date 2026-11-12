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

## 2. Header und Navigation

- Das Logo bleibt linksbündig in der weißen Markenleiste. Es wird ausschließlich
  **vertikal in der gesamten weißen Fläche zentriert**, einschließlich der
  Navigationszeile; keine horizontale Zentrierung der Logo-/Textgruppe.
  Desktop-Logo: 250 px breit und proportional skaliert. Der zweizeilige
  Beschreibungstext steht daneben, Anmelde-/Portalzugang und Navigation rechts.
  Auf breiten Ansichten sind Logo und Beschreibung über beide Rasterzeilen
  vertikal zentriert. Mobil bleibt das Logo links mit 176 px gemäß gemeinsamem Breakpoint.
- Beschreibung: „Immobilienrechner für“ / „Kauf, Sanierung und Investment“.
- Hauptnavigation: „Mieterabrechnung“, „Preise“, „Warum ImmoCheck?“.
  Die bestehende Route `/nebenkostenabrechnung/` wird trotz Umbenennung beibehalten.
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
- Direkte Inhaltsseiten liefern nur ihren passenden Haupttext im HTML aus. Die
  für interne Rechnerwechsel benötigten inaktiven Formularfelder werden aus einem
  gemeinsamen externen Skript vor der Rechnerinitialisierung eingebunden. Auf
  Über uns und Kontakt enthält der ausgeblendete Bildheader keine Rechnertexte.

## 4. Texte, Typografie und Buttons

- Markenleiste, Bildheader und Hauptinhalt verwenden `text-size-adjust: 100%`
  (einschließlich `-webkit-`), damit mobile Browser Texte beim Drehen nicht
  eigenständig vergrößern. Admin-Schriftgrößen und Browserzoom bleiben erhalten.

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
  Startseitenbutton „Nebenkosten abrechnen“ mit Dokument-Symbol und
  Untertext „Betriebskosten erfassen und versenden“. Die Gruppenüberschrift lautet
  „Mieterabrechnung“. Das Symbol steht bereits im HTML, auch bei internem
  Wechsel zur Startseite.
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
- Wenn keine Social-Media-Einträge gepflegt sind, steht auf Desktop „Über uns“
  links oben und „Kontakt“ rechts oben. Die rechtlichen Links bleiben darunter
  über beide Spalten. Die vorhandene Social-Sichtbarkeit steuert dies per CSS;
  keine zusätzlichen Serverabfragen oder nachträgliches Verschieben von DOM-Knoten.
  Mit Social-Einträgen gilt das bisherige Raster.
- Desktop nutzt das gemeinsame Raster; mobil stehen die Bereiche untereinander
  und verwenden die bestehenden aufklappbaren Abschnitte.
- Farben und Typografie kommen aus den gemeinsamen Einstellungen. Deutsche
  Silbentrennung und normale Umbrüche auch im Footer erhalten.
- Der gemeinsame Abstand zum Inhalt bleibt 16 px; keine lokale Nullsetzung.

## 7. Zuständigkeiten im Code

| Bereich | Gepflegte Quellen / Build-Schritte |
| --- | --- |
| Gemeinsame Routen und aktive Ansicht | `assets/unified-calculator-navigation.js`, `scripts/build_unified_navigation.py` |
| Erste stabile Darstellung | `assets/initial-layout.js`, Einbindung über `scripts/build_unified_navigation.py` |
| Bildheader und Höhenreservierung | `assets/stable-header.js`, `assets/stable-header.css` |
| Markenleiste, Logo, responsiver Footer | `assets/immocheck-brand-theme.css`, `assets/header-layout.css` |
| Einstellungen, Meta, Ansichtsanbindung | `assets/site-settings.js`, `assets/site-integration.js` |
| Startseite und integrierte Informationskarten | `assets/homepage.html`, `assets/homepage.css` |
| Direkte Inhaltsrouten und gemeinsame Shell | `scripts/build_settings_pages.py`, `scripts/finalize_shared_layout.py` |
| Gemeinsame Typografie | `scripts/centralize_layout_typography.py` |
| Verbindlicher Build und vollständige Prüfungen | `.github/actions/build-site/action.yml` |
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
  mit Untertext „Haus oder Wohnung kaufen und selbst nutzen“.
- Die H1 lautet „Kannst Du Dir Dein Eigenheim leisten?“. Die Seite erläutert
  Hauskauf und Eigentumswohnung sowie die manuelle Erfassung laufender Kosten.
- Der Budgetrechner prüft den allgemeinen Spielraum, der Eigenheim-Rechner eine
  konkrete Immobilie. Der Einführungstext ist auf der direkten Route im HTML
  vorhanden und bei internen Wechseln nur im Modus Eigennutzung sichtbar.

## Eingabefelder: Beispieltexte

- Keine grauen Platzhalter in Rechnereingaben; Ausnahme ist die Karte
  „Budget übernehmen“ (`#ownBudgetTransferCard`). Einheiten bleiben erhalten.
- Die Bereinigung gilt auch bei Einstieg über die Startseite/Inhaltsseiten,
  internen Rechnerwechseln und im Shadow DOM des Finanzierungsrechners.
