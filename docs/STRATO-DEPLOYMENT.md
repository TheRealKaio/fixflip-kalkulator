# STRATO: vollständige Releases und geprüfter Rückweg

Der Workflow `STRATO automatisch veroeffentlichen` verwendet
`scripts/strato_release_publish.py`. Layout und Inhalte werden vollständig unter
`.nic-releases/<commit>-<run>-<attempt>/` hochgeladen und per SHA256 geprüft.
Bestehende öffentliche HTML-, JS-, CSS- und JSON-Dateien werden nicht ersetzt.
API, Datenbank, private Konfiguration und DNS werden nicht geändert.

## Vorprüfung und Aktivierung

- Öffentliche Startseite und alle fünf Rechner müssen bereits funktionieren.
- Das bisherige Release sowie seine Auslieferungsregeln werden geprüft.
- Ein unveränderlicher PHP-Router je Release liefert ausschließlich Dateien
  aus dessen Manifest aus. HTML durchläuft immer die serverseitige Filterung.
- Ein zufälliger Vorschau-Schlüssel schützt den noch nicht aktivierten Router.
  Die Vorschau ist ohne diesen Schlüssel nicht erreichbar und nicht indexierbar.
- Vor dem Wechsel werden alle HTML-Seiten sowie JS, CSS und JSON über die
  geschützte Vorschau abgerufen. Währenddessen bleibt der bisherige Stand aktiv.
- Ein einzelner atomarer Austausch der Root-`.htaccess` aktiviert das vollständige
  Release. Die Regeln, einschließlich Sicherungsverweis, bestimmen den aktiven Stand.
- Danach werden öffentliche Seiten, Filterung, Quelldatei-Identität, Assets,
  HTTPS, API, Weiterleitungen und Zugriffsschutz geprüft.

Die serverseitige Filterung darf HTML verändern. Darum wird ihr Ergebnis nicht
bytegenau mit dem ungefilterten HTML verglichen: `X-NIC-Release` und
`X-NIC-Source-SHA256` bestätigen die tatsächlich ausgewählte und serverseitig
geprüfte Quelldatei; `X-NIC-Filtered: 1` bestätigt die erfolgreiche Filterung.
Statische Dateien werden zusätzlich anhand der ausgelieferten Bytes geprüft.
Überlebende Inline-JavaScript- und CSS-Blöcke werden in Vorschau und Live-Antwort
exakt mit dem getesteten Build verglichen. Der HTML-Serializer darf darin weder
Unicode in HTML-Zeichencodes umwandeln noch absichtlich geschriebene Zeichencodes
dekodieren. Deaktivierte Blöcke dürfen vollständig entfallen.
Deaktivierte Inhalte dürfen dabei nicht als ungeschütztes Quell-HTML abrufbar sein.

## Rücknahme

Bei einer fehlgeschlagenen Vorschau oder Live-Prüfung stellt der Publisher die
exakt gesicherten vorherigen Root-Regeln atomar wieder her. Danach prüft er
erneut die öffentlichen Seiten und die API. Ohne diese erfolgreiche Prüfung
darf keine erfolgreiche Wiederherstellung gemeldet werden.

Für eine spätere manuelle Rücknahme den Workflow auf `main` mit `action=rollback`
starten. Alternativ ist ein ausdrücklich autorisierter Commit mit dem Präfix
`Rollback STRATO atomic release` möglich. Der Rückweg liegt unter
`.nic-releases/.backups/<run>-<attempt>.htaccess`. Releases und Sicherungen nicht
automatisch löschen. Die ursprünglichen öffentlichen Dateien bleiben auch beim
ersten Wechsel erhalten, damit der Rückweg zum vorherigen Betrieb funktioniert.

Alte Dateien mit Inhalts-Hash bleiben für bereits geöffnete Seiten verfügbar.
Frühere Router dürfen dafür nur ihre referenzierten JS-/CSS-Dateien ausliefern;
frühere HTML-Seiten werden dadurch nicht öffentlich freigegeben.

## Nachweise und offene Überwachung

Erfolg erst nach bestandenen öffentlichen Prüfungen melden. Workflow-Protokoll,
Commit und Release-ID nennen. Die lokale Testsuite prüft Fehler während Vorschau
und Aktivierung sowie die Rücknahme ohne Überschreiben öffentlicher Seiten.
CI prüft Apache-Regeln einschließlich STRATO-Unterverzeichniszuordnung und führt
echtes PHP mit DOM-Filterung gegen feste Testeinstellungen aus.

Eine unabhängige externe Überwachung im Minutenintervall ist noch nicht
eingerichtet. Die Prüfungen während einer Veröffentlichung ersetzen sie nicht.
