# ImmoCheck – verbindliche Produkt- und Entwicklungsanforderungen

Stand: 22.11.2026  
Status: **Konzept / getroffene Absprachen**, keine Aussage über bereits implementierte Funktionen.  
Geltungsbereich: Miet-/Betriebskostenabrechnung als Modul der ImmoCheck-Web-App sowie perspektivisch iOS- und Android-App.

> **Leitprinzip:** Für private Kleinvermieter möglichst einfacher Ablauf, maximal fünf sichtbare Hauptschritte (bevorzugt vier), vorhandene Daten wiederverwenden, neue Felder nur bei Bedarf einblenden. Rechtliche Konformität und nachvollziehbare Berechnung gehen vor scheinbarer Automatisierung.

## 1. Produktumfang und Zielgruppe

- Private Einzel- und Kleinvermieter; keine Ausrichtung auf große Hausverwaltungskonzerne.
- Auch kleine Mehrfamilienhäuser mit z. B. 2, 3, 4, 6 oder mehr Wohnungen sind grundsätzlich Zielgruppe. **Nicht jeder Heizkostenfall wird in V1 unterstützt.**
- Zwei Erfassungswege:
  1. **WEG-Jahresabrechnung importieren** (priorisierter Standardweg).
  2. **Manuelle Erfassung** mit festen Kostenfeldern: Vermieter sortiert/summiert selbst; optionale Belegerkennung pro Einzelbeleg innerhalb der Erfassungsmaske.
- Beide Wege nutzen dasselbe normalisierte Datenmodell, denselben Betriebskostenkatalog, dieselbe Prüf-/Abrechnungslogik und dieselbe PDF-Ausgabe.
- Website und mobile Apps greifen auf gemeinsame Daten und serverseitige Berechnungen zu. Eine einmal begonnene Abrechnung soll geräteübergreifend fortsetzbar sein.
- Fertige externe Heizkostenabrechnungen (z. B. Techem, Brunata, Minol) können als PDF zur endgültigen Abrechnung hinzugefügt werden.

## 2. Bedienung und Layout (UX)

- Höchstens **5 Hauptschritte**, Ziel: **4 Schritte beim WEG-Import**:
  1. WEG-Abrechnung hochladen und automatisch auslesen (oder manuellen Erfassungsweg auswählen).
  2. Erkannte Objekt-/Wohnungs-/Vermieterdaten kontrollieren und fehlende Mieterdaten ergänzen.
  3. Kostenpositionen, Kostenarten, Verteilung und offene Fragen prüfen/ergänzen.
  4. Endkontrolle, Freigabe, optional Anlagen hinzufügen und PDF herunterladen/Versand vorbereiten.
- Bei manueller Erfassung dieselbe klare Prozessführung; Kosten werden in einer Maske direkt in vorgegebene Positionen eingetragen. Die OCR-Erkennung einzelner Belege ist **optional**, nicht verpflichtend.
- Erkannte Werte vorausfüllen statt erneut erfragen. Unklare/fehlende Werte sichtbar markieren; keine stillschweigenden Fantasiewerte.
- Zusätzliche Eingaben per bedarfsgesteuerten Ausklappbereichen/Checkboxen; keine neuen Hauptschritte.
- Heizkosten-Entscheidungshilfe mit drei Wegen: (a) externe fertige Heizkostenabrechnung, (b) einfache Flächenverteilung **nur wenn rechtlich/mietvertraglich zulässig**, (c) eigene verbrauchsabhängige Erfassung (erweiterte Funktion, später). Nicht unterstützte Fälle klar abweisen, nicht falsch berechnen.
- UI zeigt im Regelfall die **standardisierten ImmoCheck-Bezeichnungen**, Originalbezeichnungen bleiben zur Nachvollziehbarkeit aufrufbar.

## 3. Stammdaten und Relationen

- Getrennte persistente Datensätze: **Vermieterprofil**, **Gebäude/WEG**, **Wohnung/Einheit**, **Mietverhältnis/Mieter**, **Abrechnungsjahr**.
- Ein Vermieter kann mehrere Wohnungen im selben Gebäude besitzen. Gebäude-Gesamtanteile und Wohnungs-Miteigentumsanteile werden **nicht** unzulässig zusammengerechnet.
- Gebäude: Adresse, Gebäude-/WEG-Stammdaten, Gesamtfläche und Nenner der Miteigentumsanteile, soweit vorhanden; Heizungsart.
- Wohnung: Nummer/Bezeichnung, Wohnfläche, individuelle Miteigentumsanteile inklusive Bezugsgröße, Bezug zu Gebäude, spätere Messgeräte.
- Mieter/Mietvertrag: Name/Anschrift, Mietbeginn/-ende, Abrechnungszeitraum, Betriebskostenvereinbarung, Umlageschlüssel, Vorauszahlungen und Mieterwechsel.
- Vermieterprofil: Vorname/Nachname oder Firma, postalische Anschrift, E-Mail, optional Telefon, optional IBAN; persönliche Steuernummer **nicht als reguläres Pflichtfeld**.
- Beim WEG-Import Eigentümer/Adressat auslesen und **als vorgeschlagenen Vermieter** übernehmen; nicht die Hausverwaltung im Briefkopf als Vermieter missverstehen. Abfrage „Ist der genannte Eigentümer auch der Vermieter?“ Bei Nein abweichende Angaben einblenden. Entscheidend ist tatsächliches Mietverhältnis.
- Wiederkehrende Stammdaten speichern, bei Folgeimporten abgleichen, Änderungen nicht unbemerkt überschreiben.

## 4. Dokumentenerkennung und Import

- Entwicklungsphase bevorzugt **lokal/selbst betriebenes Open-Source-OCR** (zunächst PaddleOCR als Testkandidat; Alternativen möglich). Keine zwingende externe kostenpflichtige API.
- OCR-Anbieter **austauschbar über definierte Schnittstelle**; OCR, Interpretation, Kostenklassifikation und Berechnung getrennte Module.
- Import soll nicht nur Kosten, sondern nach Möglichkeit auch Eigentümer-/Objektadresse, Wohnungsbezeichnung, Fläche, MEA, Abrechnungszeitraum, Verteilungsschlüssel, bereits berechnete Wohnungsanteile erkennen.
- Beim WEG-Import vorhandene **auf die Wohnung entfallende Beträge** verwenden, **nicht Hausgesamtkosten nochmals verteilen**; Erkennung und Abgrenzung beider Betragsarten erforderlich.
- PDF-/Bildquelle, Seiten-/Positionsnachweis, Originalbezeichnung, OCR-Ergebnis, zugeordnete standardisierte Felder und Korrekturen nachvollziehbar speichern.
- Gemeinsamer Import-/Validierungsprozess für ganze WEG-Abrechnungen und optionale Einzelbelege.
- Doppelte Belege/Positionen erkennen und vor doppelter Übernahme warnen.
- Privat korrigierte Zuordnungen können objekt-/nutzerspezifisch wiederverwendet werden; keine ungeprüfte Übernahme privater Beleginhalte in globalen Wissensbestand.
- Keine Aussage, dass jede WEG-Abrechnung vollständig korrekt automatisch gelesen werden kann: Qualitätsprüfung anhand echter anonymisierter Beispiele notwendig.

## 5. Einheitliches Raster: Kostenarten und Verteilungsschlüssel

- Zentraler, versionierbarer Katalog der üblichen Betriebskostenarten auf Basis BetrKV einschließlich nicht umlagefähiger und prüfpflichtiger Kosten.
- Für Kostenarten Synonyme/abweichende Bezeichnungen hinterlegen; gemischte Belege nach Positionen trennen, soweit möglich.
- Status je Position: **umlagefähig**, **nicht umlagefähig**, **prüfungsbedürftig**; tatsächliche Umlagefähigkeit ist von Rechtslage und Mietvertrag abhängig, nicht allein von OCR-Vokabeln.
- Ein **kanonischer Katalog der Verteilungsschlüssel** (z. B. Miteigentumsanteile, Wohnfläche, Wohneinheiten, Personen-/Personentage, gemessener Verbrauch, Direktzuordnung). Synonyme und Einheiten werden gematcht; „Einheiten“ darf nicht ohne Kontext blind zugeordnet werden.
- Je erkannter Kostenposition speichern: Originalschlüssel der WEG, normierter Schlüssel und zugehöriger Zähler/Nenner oder Messwerte; getrennt davon der **für das Mietverhältnis zulässige Verteilungsschlüssel**.
- Eindeutiger Match: automatisch vorschlagen/zuordnen; mehrdeutiger Match: Prüfhinweis; unbekannter Match: Auswahl durch Vermieter und optionalen Eintrag ins gepflegte Synonymverzeichnis.
- Ursprungspositionen bleiben verlinkt, während Beträge je Standardkostenart für die Ausgabe nachvollziehbar summiert werden.
- WEG-Verteilung ist **nicht automatisch** die mietrechtlich richtige Verteilung; ggf. zusätzliche Ausgangsdaten und Neuberechnung erforderlich.

## 6. Heiz-, Warmwasser-, Kaltwasser- und Abwasserkosten

- Getrennte Kostenbereiche für **Heizung**, **Warmwasser**, **Kaltwasser**, **Abwasser**.
- Heizungsvarianten in Objektstammdaten: (1) gemeinsame Zentralheizung mit zentralem Warmwasser (Standardbeispiel), (2) Zentralheizung mit dezentraler Warmwasserbereitung, (3) separate Heizung je Wohnung. Andere Fälle nicht strukturell ausschließen.
- Bei kombinierten Anlagen gemeinsame Kosten **nur einmal** erfassen und nach rechtlich passender Methode auf Heizung/Warmwasser aufteilen.
- Selbst bewohntes Haus mit höchstens zwei Wohnungen kann unter Voraussetzungen und entsprechender Vereinbarung von speziellen Regeln profitieren; **keine pauschale Flächenabrechnung für beliebige Mehrfamilienhäuser**.
- V1: externe Heizkostenabrechnung übernehmen/anhängen und einfache Heizkostenlogik nur für explizit unterstützte, zulässige Fälle. Keine vollständige Verbrauchsabrechnung vortäuschen, wenn Daten/Funktion fehlen.
- Geplante spätere Erweiterung: Heizkostenverteiler/Wärmezähler/Warmwasserzähler, Geräte je Wohnung und bei Heizkostenverteilern je Heizkörper (mehrere pro Raum möglich), Seriennummer, Ablesestände/Stichtage, Bewertungsfaktoren, Verbrauchs-/Grundkostenaufteilung, weitere rechtliche Pflichten.
- Die erweiterte Verbrauchserfassung per Checkbox/aufklappbarem Bereich ist **geplant**, aber nicht als schon implementiert kennzeichnen. Gerätedaten sollen dauerhaft und Ablesewerte jahrgangsbezogen gespeichert werden.
- Falls ein Fall mit vorhandenen Zählern rechtlich eine verbrauchsabhängige Abrechnung verlangt und V1 diese noch nicht kann: **keine unzulässige Fläche-als-Ersatz-Berechnung anbieten**.

## 7. Kontrolle, Ausgabe und Schutzmaßnahmen

- Endkontrolle und Freigabe erfolgen **durch den Vermieter**, nicht durch automatische KI-Freigabe.
- Prüfen: Kostenklassifikation, gemischte Rechnungen, Doppelbuchungen, Heizkosten-Doppelerfassung, Zeitraum, Mietverhältnis, Vorauszahlungen, Abweichung WEG-/Mieterschlüssel.
- Anlage externer Heizkosten-PDFs vor Ausgabe möglich; Anlage ersetzt **nicht** die korrekte Einbeziehung der zugehörigen Kostenwerte in die Berechnung.
- PDF-Abrechnung mit nachvollziehbarer Kostenaufstellung und Anlagen, speichern und herunterladen; Versandfunktion separat spezifizieren und implementieren.
- DSGVO, Zugriffsschutz für Mieterdaten/Belege, Verschlüsselung/Backups, Berechtigungssystem und Nachvollziehbarkeit gehören zur technischen Umsetzung.

## 8. Umfang und Phasen

**Priorität V1 (MVP):** WEG-Import, Erkennung/Übernahme von Stammdaten und Kosten, einheitliche Kataloge/Schlüssel, Mieterdaten und Vermieterprofil, Prüfungen, nachvollziehbare Berechnung, PDF/Anlagen; manuelle Kostenmaske als zweiter Weg. Optionale Einzelbeleg-OCR kann stufenweise folgen.

**Später:** vollständige Messgeräte-/Verbrauchsdatenverwaltung und Heizkostenabrechnung für passende Mehrfamilienhäuser; verbesserte Erkennung/klassifizierende Modelle; App-Store-Veröffentlichung für iOS und Android aus gemeinsamer Plattform.

## 9. Dokumentations- und Änderungsregeln

Anforderungen ausdrücklich in drei Domänen trennen:
1. **UI/UX und Layout**
2. **Datenmodell, Erkennung, Recht und Rechenlogik**
3. **Funktionsumfang, Produktregeln und Roadmap**

Jede neue verbindliche Vereinbarung versioniert in dieser Datei oder verlinkten Spezifikationen festhalten. Konflikte mit bisherigen Beschlüssen sichtbar dokumentieren und erst nach Entscheidung ändern.

**Offene technische/rechtliche Prüfungen:** konkrete WEG-Dokumentlayouts, notwendige Eingabefelder für zulässige Heizkostenfälle, mietvertragliche Schlüssel/Abweichungen, jährliche Nutzer- und Geräteprozesse, sichere OCR-Betriebsumgebung und DSGVO-Prüfung. Diese sind **nicht** stillschweigend als entschieden oder implementiert zu behandeln.

## 10. Startseite und Schrittführung (Ergänzung 22.11.2026)

**Startseite (vor Prozessbeginn):**
- Die bestehende Seite „Mieterabrechnung starten“ in ImmoCheck als Ausgangspunkt verwenden; vorhandenen oberen Einleitungstext beibehalten.
- In der Mitte **genau zwei primäre Schaltflächen**: „WEG-Abrechnung hochladen“ und „Manuelle Erfassung“. Keine weiteren primären Startaktionen.
- Unter den Schaltflächen einen zusätzlichen, über den Adminbereich pflegbaren Informationstext vorsehen.
- Einen knappen Hinweis „In vier einfachen Schritten zur Abrechnung“ auf der Startseite erlauben; konkreten Fortschrittsbalken erst **nach Auswahl** des Weges zeigen.
- Der Fortschritt sollte auf Desktop und mobil gut erkennbar sein und vier benannte Schritte zeigen.

**WEG-Import – präzisierte UX-Reihenfolge, ohne mehr als vier Schritte:**
1. WEG-Abrechnung hochladen; Erkennung von Objekt, Wohnung, Eigentümer, Kosten und WEG-Schlüsseln.
2. Erkannte **Eigentümer-/Vermieterdaten und Wohnungs-/Objektdaten** anzeigen und zur Kontrolle anbieten; Eigentümer als Vermieter vorschlagen, nach Bestätigung übernehmen; IBAN ergänzen; fehlende Mieterdaten/Mietvertrag ergänzen. Unterabschnitte innerhalb **eines** Hauptschritts, kein Aufblähen der Schrittzahl.
3. Erkannte Kostenpositionen, Zuordnungen, Verteilungsschlüssel und rechtliche Prüfhinweise kontrollieren; nötige Nachträge.
4. Endkontrolle, Anlagen (z. B. Heizkosten-PDF), Freigabe und Ausgabe.
- Ob Eigentümer-/Vermieterdaten vor Objektdetails geprüft werden, ist eine **UX-Detailfrage**; beide Prüfungen bleiben im Datenergänzungs-/Prüfschritt, sodass der Ablauf kurz bleibt.

**Platzierung von Verteilungsschlüsseln:**
- Unter Gebäude-/Wohnungs-Stammdaten: Gesamt- und Wohnungsfläche, Gesamt- und individuelle Miteigentumsanteile sowie vorhandene **Standard-/Defaultschlüssel** und erforderliche Bezugsgrößen.
- Der tatsächliche, **kostenartbezogene WEG-Schlüssel** gehört zusätzlich an die jeweilige erkannte Kostenposition; der **mietrechtlich anzuwendende Schlüssel** wird separat je Kostenart/Mietverhältnis gespeichert bzw. abgeleitet und geprüft.
- Der Import matched Begriffsvarianten auf den zentralen normierten Schlüsselkatalog; nicht automatisch ein einziger Objektschlüssel für sämtliche Kosten.
- Sichtbar einfach halten: Standardwerte vorausfüllen, nur Abweichungen und unklare Zuordnungen zur Eingabe öffnen.

Diese Ergänzung dokumentiert die Startseiten- und Ablaufabsprache als Konzept; sie behauptet keine bereits erfolgte Umsetzung im Code.
