# Neustart ImmoCheck: verbindliche UI-Regeln

Vor Änderungen an Header, Navigation, Inhaltsseiten, Textdarstellung, Buttons
oder Footer immer [docs/UI-STANDARDS.md](docs/UI-STANDARDS.md) lesen und beachten.
Diese Datei enthält die vereinbarten, aktuellen Darstellungs- und Verhaltensregeln.
Ausdrückliche neue Vorgaben des Nutzers haben Vorrang; die betroffenen Standards
anschließend im selben Änderungssatz aktualisieren.

- Gemeinsame Komponenten und Admin-Einstellungen wiederverwenden; keine eigene
  Header-, Typografie-, Button- oder Footer-Variante je Route einführen.
- Änderungen in den gepflegten Quellen unter `assets/` und `scripts/` vornehmen.
  `_site/` ist generierte Ausgabe und keine dauerhafte Implementierung.
- Den vollständigen aktiven Build berücksichtigen: spätere Build-Schritte dürfen
  die Änderung nicht wieder überschreiben. Historische Patches nur nach Prüfung entfernen.
- Gemeinsame UI-Änderungen auf Startseite, allen fünf Rechnern und den drei
  Informationsseiten vergleichen, einschließlich Mobilansicht und Seitenwechsel.
- Umfang der Prüfung an der Änderung ausrichten. Vor Veröffentlichung müssen
  die bestehenden erforderlichen Build- und CI-Prüfungen bestehen.
