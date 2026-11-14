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

## Verbindlicher Ablauf für STRATO-Veröffentlichungen

Diese Regeln gelten für alle zukünftigen Live-Veröffentlichungen. Eine
Dokumentationsänderung allein ist keine Umsetzung der technischen Absicherung.

1. Vor jedem Deployment die öffentliche Live-Domain einschließlich www,
   Weiterleitungen, Startseite und Rechner prüfen und den aktiven Release-Stand
   dokumentieren. Bei bestehendem Ausfall zuerst Ursache und Wiederherstellung
   klären; keine normale Veröffentlichung auf einen ungeklärten Fehler aufsetzen.
2. Neue Version vollständig in ein separates Release-Verzeichnis hochladen.
   Die aktive Version während Upload und Vorprüfung erreichbar lassen; keine
   schrittweise Überschreibung der laufenden Website.
3. Erforderliche Build- und CI-Prüfungen bestehen lassen. Vor Aktivierung das
   tatsächlich hochgeladene Release über eine geschützte Vorschau prüfen:
   Startseite, alle Rechner, statische Dateien und serverseitige Funktionen
   einschließlich Inhaltsfreigaben. Mobile, Querformat-, Tablet- und
   Desktop-Darstellung entsprechend dem Änderungsumfang kontrollieren.
4. Vor dem Wechsel einen bekannten funktionsfähigen Rückweg sichern und dessen
   Funktionsweise nachweisen. Den Wechsel mit einer atomaren, auf STRATO
   unterstützten Umschaltung ausführen. Ist das nicht gewährleistet, zuerst
   den Veröffentlichungsmechanismus korrigieren.
5. Unmittelbar nach Aktivierung die öffentliche Live-Domain prüfen:
   gültiges TLS, erwartete Weiterleitungen, HTTP 200 und erwarteter Seiteninhalt
   sowie wesentliche Dateien und Funktionen. Dateiprüfsummen oder ein grüner
   Workflow allein belegen keine erfolgreiche Veröffentlichung.
6. Bei fehlgeschlagener Live-Prüfung sofort automatisch auf das vorherige
   funktionsfähige Release zurückschalten. Danach dieselben öffentlichen
   Erreichbarkeits- und Inhaltsprüfungen wiederholen. Rücknahme erst als
   erfolgreich melden, wenn die Website tatsächlich wieder erreichbar ist.
   Bei fehlgeschlagener Wiederherstellung sofort klar über den Ausfall berichten,
   Diagnose und gesicherte Rückwege erhalten und keine weiteren normalen
   Deployments starten.
7. Externe Erreichbarkeitsüberwachung im Minutenintervall mit Ausfallmeldung
   vorsehen. Solange sie nicht eingerichtet und geprüft ist, diesen offenen
   Punkt ausdrücklich dokumentieren; keine aktive Überwachung behaupten.
8. DNS, Domain-/Webspace-Zuordnung und allgemeine Server-Konfiguration getrennt
   von normalen Layout- und Inhaltsänderungen ändern und prüfen.
9. Erst nach bestandener öffentlicher Live-Prüfung „live“, „aktiviert“ oder
   „erfolgreich veröffentlicht“ melden. Im Status zwischen Quellcode gespeichert,
   Vorschau geprüft, Auslieferung versucht und Live-Version bestätigt unterscheiden.
   Zu jedem Release Commit, Workflow, Prüfresultat und gegebenenfalls Rücknahme
   nachvollziehbar festhalten.

Vor der nächsten normalen Veröffentlichung müssen der bestehende 404 geklärt
und ein geprüfter Wiederherstellungsweg vorhanden sein.
