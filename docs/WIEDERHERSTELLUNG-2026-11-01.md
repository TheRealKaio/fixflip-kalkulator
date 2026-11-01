# Wiederherstellung der Originaloberfläche

Auf Wunsch des Nutzers wird das Original aus `backup/live-before-immocheck-redesign-2026-11-01` (`0ef48e3faf53704bcdd52b8440da0777d81cbcbd`) wiederhergestellt.

Beibehalten werden ausschließlich die aktuellen Markenbilder und Farben: Headerlogo, Favicon, Apple Touch Icon, Social-Bild, Immobilienfoto und die dunkelgrün/creme/weiße Farbgebung. Das Marken-Stylesheet verändert keine Breiten, Abstände, Raster oder Navigation.

Die ursprüngliche Rechneranordnung, Navigation, Eingaben, Ergebnisse, Anmeldung und sonstige Bedienung stammen wieder aus dem Backup. Die nachträgliche Schrittnavigation und das Layout-Redesign werden entfernt. Die Berechnungsquellen, Finanzierungsseite, PDF-Rechenfunktionen und der Zugangscode werden im Build byteweise gegen das Backup geprüft.

Prüfung: vollständiger Original-Build einschließlich Budget-, Vermietungs-, Finanzierungs-, PDF-, Einstellungs-, Statistik- und Kontonavigationsprüfungen. Zusätzliche Chromium-Prüfung für alle fünf Rechner auf Desktop und Smartphone, ohne Redesign-Schrittnavigation, mit geladenem aktuellem Logo und Foto sowie unabhängiger Restschuldprüfung. Der Entwicklungsworkflow führt denselben Build ohne Deployment und die PHP-API-Prüfungen aus.

Die Wiederherstellung erfolgt als neuer Commit, ohne die Git-Historie oder den Backup-Branch umzuschreiben. Die aktuellen Bilddateien bleiben erhalten. Aktuelle Ergebnisse sind in GitHub Actions am Wiederherstellungs-Commit nachvollziehbar.
