# Buttonleiste, Maskenaktionen und Footer

- Footertext mit 5 px Innenabstand zum oberen Rand.
- Untere Aktionsleiste folgt exakt Breite und horizontaler Position des Kalkulators, einschließlich Smartphone und Größenänderungen.
- Finanzierungstitel und Symbol sind vertikal mittig ausgerichtet.
- Die alten Schaltflächen „Auf 0 zurücksetzen“ und „Übernehmen“ sind aus der sichtbaren Sanierungsoberfläche entfernt. Ihre DOM-IDs bleiben für vorhandene Initialisierung erhalten.
- Vorschlagsbuttons heißen einheitlich „Vorschläge übernehmen“ und sind grün; „Budgetwerte übernehmen“ ist ebenfalls grün.
- Rechts neben den Vorschlagsbuttons steht ein rotes X. Es leert ausschließlich die Eingabemaske der monatlichen Ausgaben bzw. der jeweiligen Sanierung. Kaufpreis, Wohnfläche und andere Masken bleiben erhalten. Die vorhandenen Eingabeereignisse aktualisieren Modellwerte und Speicherung; Berechnungsformeln werden nicht geändert.
- Vorschlagsbutton und X teilen sich die bisherige Buttonbreite, ohne Umbruch der Aktionszeile oder zusätzliche Spalte.

Die Browserprüfung umfasst alle fünf Rechner bei Desktop- und Smartphonebreite, 5-px-Abstand, Ausrichtung/Breite der Aktionsleiste, Finanzierungstitel, grüne Buttons, Übernahme von Vorschlägen, gezieltes Leeren sowie Fortbestand der gelöschten Werte nach erneutem Laden. Bestehende Build-, PDF-, Finanzierungs- und API-Prüfungen bleiben aktiv. Die fachlichen Quellen werden unverändert gegen das Backup geprüft.
