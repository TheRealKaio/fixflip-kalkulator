# Gemeinsame Layoutarchitektur – V8.364

Die komprimierten Originale unter `source/`, `assets/financing.html`,
`assets/pdf-reports.js` und `assets/user-access.js` bleiben unverändert. Der
bestehende Originalvergleich im Build erzwingt dies weiterhin.

## Website

`finalize_shared_layout.py` läuft nach allen Branding- und Layoutschritten,
vor dem Asset-Fingerprinting. Es übernimmt die tatsächliche CSS-Reihenfolge
der Hauptseite in `calculator-shell.css` und entfernt die entsprechenden
Selektoren aus den anderen generierten Stylesheets und Inline-Blöcken.
Alle fünf Rechnerrouten laden dieselbe Datei. Der Footer steht überall im
selben App-Container. Seine Breite benötigt keine JavaScript-Messung mehr.

Alle fünf Navigationskacheln verwenden dieselbe Raster-, Größen- und
Zustandsdarstellung: fünf gleich breite Spalten auf Desktop/Tablet und eine
Spalte auf Smartphones. Die bisherige Icon-Anordnung bleibt erhalten.
Die Kacheln dürfen mit der Schriftgröße wachsen; es wird kein Text auf eine
feste Höhe abgeschnitten.

`NICSettings.apply` steuert die Schriftfamilie aller Website-Texte und die
Grundschriftgröße von Fließtext, Formularen, Footer und Rechtstexten.
H1–H4 behalten ihre eigenen Einstellungen. Bestehende Speicher- und
Konfigurationsschlüssel wurden nicht geändert.

## PDF

`build_pdf_typography.py` erweitert ausschließlich das generierte
`pdf-reports.js`. Alle fünf bestehenden Berichts-Builder verwenden weiter
`NICPDF.create`, die originalen Berechnungen und Inhalte.
Die PDF-Schriftgrößen bleiben auf der bisherigen Druckskala und ändern sich
proportional zur Admin-Grundschriftgröße (Referenz 16) beziehungsweise H2
(Referenz 18) für fett gesetzte Rubriken. Die Rechtstext-Paginierung misst
die tatsächlich verwendete Schriftgröße und setzt bei Bedarf neue Seiten ein.
Die bestehende jsPDF-Basisschrift-Zuordnung bleibt bestehen: Georgia wird
als Times, die Sans-Serif-Auswahl als Helvetica ausgegeben. Exakte proprietäre
Web-Schriftdateien sind nicht Bestandteil des Repositorys.

## Prüfungen

Der Pages-Workflow baut aus einem leeren Ausgabeordner und führt vor der
Veröffentlichung die vorhandenen Rechen-/Integrationsprüfungen sowie die
Chromium-Prüfung aller fünf Rechner auf Desktop und Smartphone aus.
`verify_all_reports.cjs` erzeugt die vollständigen fünf Berichte jeweils mit
Standardtypografie und Georgia/20/H2=24. Dabei werden die tatsächlichen
Bestands-Builder aufgerufen; keine nachgebauten Berichtsmodelle.

Lokale Browserprüfungen bedienen Assets direkt aus `_site`, damit getrennte
Netzwerk-Namensräume keine falschen HTTP-Verbindungsfehler erzeugen.
