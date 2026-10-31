# ImmoCheck – Installation auf STRATO

Dieses Paket enthält die PHP-Schnittstelle für MariaDB und den passenden Anmelde-Client. Die vorhandenen Kalkulatoren bleiben öffentlich nutzbar. Erst die gesonderte Aktivierung in `backend-config.json` verbindet die Oberfläche mit dem Server.

## 1. Vorbereiten

- PHP 8.2 mit PDO/MySQL, OpenSSL, JSON und ausgehenden TLS-Verbindungen.
- MariaDB 11.8, eine eigene Datenbank mit Berechtigung zum Erstellen von Tabellen.
- HTTPS für die API-Subdomain und die eigentliche Kalkulator-Domain.
- SFTP mit Zugriff auf das gemeinsame Stammverzeichnis.
- SMTP-Postfach mit dem vom Anbieter vorgegebenen Server, Benutzer und Passwort.
- Eine Sicherung vorhandener Admin-Einstellungen: Im alten Admin-Bereich „Konfiguration exportieren“. **Diese Datei vor Einrichtung als `initial-settings.json` verwenden**, um eigene Browser-Entwürfe zu übernehmen. Das mitgelieferte Exemplar enthält den veröffentlichten Stand, nicht unbekannte lokale Entwürfe.

Es werden nur Tabellen mit Präfix `nic_` erzeugt. Existieren solche Tabellen bereits aus einer anderen Installation, Einrichtung anhalten und erst Herkunft/Backup klären. Einrichtung nicht zum Zurücksetzen einer vorhandenen Datenbank verwenden.

## 2. Die beiden Ordner hochladen

Im Paket unter `webspace/`:

- `immocheck-api/`: in den bereits angelegten, der API-Subdomain zugeordneten Ordner hochladen.
- `immocheck-private/`: **daneben**, nicht innerhalb des API-Ordners, hochladen.

Beide Ordner müssen auf gleicher Ebene liegen. Der private Ordner enthält eine `.htaccess` mit `Require all denied`. Sie muss mit hochgeladen werden (versteckte Dateien im SFTP-Programm anzeigen). Noch besser: Falls der Hoster es ermöglicht, privaten Code ganz außerhalb aller zugeordneten Domain-Verzeichnisse ablegen und den Require-Pfad in `index.php` entsprechend anpassen.

Die API-Domain darf nur auf `immocheck-api/` zeigen. Andere Domains dürfen nicht auf `immocheck-private/` zeigen. Über eine Domain, die den gemeinsamen Stammordner ausliefert, muss ein Aufruf von `/immocheck-private/initial-settings.json` 403/404 liefern. Falls nicht: Installation stoppen, Ordnerzuordnung/Apache-Zugriffsschutz korrigieren. Nicht pauschal das gesamte Stammverzeichnis hochladen.

## 3. Geschützte Konfiguration ausfüllen

Nur auf STRATO `immocheck-private/config.example.php` nach `config.php` kopieren. Folgende Felder ausfüllen:

- `db.host`, `db.name`, `db.user`, `db.password`: bereits ermittelte Datenbankzugangsdaten.
- `smtp.user`, `smtp.password`, `smtp.from`: vollständige Absenderadresse, Postfachpasswort und dieselbe Absenderadresse.
- `smtp.port=465`, `smtp.encryption='tls'` für implizites TLS; alternativ `587` und `'starttls'`. Das Paket erlaubt keinen unverschlüsselten SMTP-Fallback und prüft Serverzertifikate.
- `admin.first_name`, `admin.last_name`, `admin.email`: Daten des vorgesehenen ersten Administrators.
- `pepper` und `setup_key`: zwei **unabhängige**, zufällige Geheimnisse mit mindestens 64 Zeichen. Zum Beispiel zweimal im lokalen Terminal `openssl rand -hex 32` ausführen. Werte nicht hier posten und nicht in URLs einfügen.
- `api_origin` und `allowed_origins`: exakt die produktiven HTTPS-Ursprünge, ohne abschließenden Schrägstrich. Die API-Adresse selbst für das Installationsformular aufnehmen. Nur vertraute Origins verwenden, niemals `*` oder beliebige GitHub-Benutzerseiten.

PHP-Strings mit Apostrophen/Backslashes müssen korrekt maskiert werden. Kein BOM und kein Text vor `<?php`. Für `config.php` möglichst Dateirechte 600, sofern PHP damit lesen kann. Diese Datei niemals nach GitHub oder in öffentliche Uploads kopieren. Der ZIP-Download enthält absichtlich keine echten Zugangsdaten.

## 4. Einmalig einrichten

1. `https://api.neustart-immocheck.de/index.php?r=health` öffnen. Vor Einrichtung sollte `ok: true, ready: false` erscheinen. Bei 503 Serverkonfiguration prüfen; Datenbankdetails werden bewusst nicht öffentlich angezeigt.
2. `https://api.neustart-immocheck.de/install.html` öffnen.
3. Den selbst erzeugten `setup_key` in das Formular eingeben und „Einmalig einrichten“ wählen. Dadurch entstehen Tabellen, Startkonfiguration und das noch nicht E-Mail-bestätigte Admin-Konto. Dabei wird **keine E-Mail versendet**.
4. `install.html` anschließend vom Server löschen. Der Setup-Endpunkt verweigert eine zweite Einrichtung, solange die zentrale Konfiguration existiert.
5. `health` muss nun `ready: true` melden.

## 5. Frontend gezielt aktivieren

Die GitHub-Version enthält bereits `user-access.js`, lädt aber standardmäßig `assets/backend-config.json` mit `enabled: false`. Erst nach erfolgreicher Servereinrichtung `enabled` auf `true` setzen und die API-URL prüfen. Anschließend die Änderung über den bestehenden GitHub-Pages-Build veröffentlichen. Eine vorbereitete JSON-Datei liegt im Paket unter `frontend/backend-config.enabled.json`.

Die App muss auf der eigentlichen Kalkulator-Domain geöffnet werden. Authentifizierung verwendet ein sicheres HttpOnly-Cookie der API-Subdomain mit SameSite=Lax. Das funktioniert bei HTTPS auf API und Webseite derselben Hauptdomain. Eine fremde `github.io`-Adresse ist nicht für den produktiven Login vorgesehen und wird nicht in die CORS-Freigabe aufgenommen. Keine Cookies über URL-Parameter übertragen.

**Noch nicht aktivieren**, solange Datenbank- und SMTP-Passwörter fehlen oder der geschützte Ordner öffentlich erreichbar ist. Bei Problemen `enabled` wieder auf `false` setzen und neu veröffentlichen: Der bisherige lokale Modus bleibt verfügbar. Dadurch werden jedoch Registrierungspflichten deaktiviert; diese Rückkehr zum öffentlichen Modus ist eine bewusste Betreiberentscheidung.

## 6. Ersten Admin anmelden

Auf der eigentlichen Webseite das Kontosymbol öffnen und die konfigurierte Admin-E-Mail eingeben. „Code anfordern“ wählen. Der Versand ist der erste echte SMTP-Test. Den achtstelligen Code aus der E-Mail eingeben; er ist zehn Minuten gültig und nur einmal nutzbar. Nicht „Neues Benutzerkonto“ wählen, das Admin-Konto wurde bei Einrichtung bereits angelegt.

Im Konto „Admin-Bereich öffnen“ wählen. Im Reiter Nutzereinstellungen erscheinen Benutzerverwaltung und Abmelden. Alle bestehenden Admin-Einstellungen werden mit „Global speichern“ zentral gespeichert. Interne Servergeheimnisse gehören nicht in diese Felder. Das Programm prüft Admin-Rechte serverseitig; weder eine sichtbare Schaltfläche noch ein im Browser geänderter Rollenwert verleiht Rechte.

## 7. Abnahme vor Registrierungspflicht

- Normales Konto registrieren, Namen und Bestätigung prüfen; Anmeldung mit falschem/abgelaufenem/wiederverwendetem Code muss scheitern.
- Fünf falsche Codeversuche müssen eine Challenge sperren. Wiederholte Code-Anforderungen und Verifikationsversuche müssen begrenzt werden.
- Normaler Nutzer darf weder Benutzerliste noch globale Schreibfunktionen aufrufen.
- Zwei Browser: Einstellung im Admin ändern; beim anderen Browser neu laden und Änderung prüfen. PDF-Aktionen prüfen aktuelle Zugangsregeln serverseitig. Bereits geöffnete Webseiten übernehmen globale Einstellungen nach spätestens 30 Sekunden, solange die Seite sichtbar ist.
- Benutzer sperren: Eine bestehende Sitzung darf danach keine geschützte Aktion mehr ausführen. Entsperren verlangt eine neue Anmeldung. Löschen entfernt Profil, Codes und Sitzungen. Das eigene Admin-Konto und der letzte aktive Admin sind geschützt.
- Admin-Änderungen aus zwei Tabs: Eine veraltete Version darf die neuere nicht überschreiben (409, neu laden).
- Die drei Checkboxen einzeln testen: öffentliches Kalkulieren, PDF-Download und PDF-Teilen. Wird Kalkulieren eingeschränkt, verlangen auch dessen Berichte eine Anmeldung. Ein Teilen-Fallback auf Download prüft zusätzlich die Download-Regel.
- Teilen bedeutet die vorhandene Geräte-/Browser-Teilen-Funktion, keinen automatischen Versand von PDF-Anhängen per SMTP. SMTP versendet hier ausschließlich Anmeldecodes.
- Die App-Berechnungen laufen weiterhin im Browser. Eine Registrierungspflicht steuert die Bedienung der App; sie kann das Herunterladen oder eigenständige Ausführen öffentlich ausgelieferten JavaScript-Codes technisch nicht verhindern. Für strikt geschützte Berechnungen oder PDF-Erzeugung müssten diese Funktionen auf den Server verlagert werden.

## 8. Betrieb

- Regelmäßiges Datenbank-Backup und Wiederherstellung testen; Zugriff auf Backups auf den Betreiber begrenzen. Gelöschte Konten können innerhalb der Backup-Aufbewahrung noch in Sicherungen enthalten sein.
- Wenn SSH/Cron zur Verfügung steht, täglich `php /ABSOLUTER/PFAD/immocheck-private/cleanup.php` ausführen. Das entfernt abgelaufene Codes/Sitzungen, alte Versuchszähler, unbestätigte normale Konten nach sieben Tagen und Änderungsmetadaten nach 180 Tagen. Der Pfad muss zum Hosting passen. Aufruf nur per PHP-CLI, nicht per öffentlicher URL.
- Datenschutzhinweise um Registrierung, E-Mail-Versand, Sitzungen und Löschfristen ergänzen; die vorhandenen Texte werden nicht automatisch rechtlich angepasst.
- Die Zugangskonfiguration und Konten werden nicht in die öffentliche Einstellungsantwort aufgenommen. Rollen werden nicht aus Nutzerangaben übernommen; öffentliche Registrierung legt ausschließlich normale Benutzer an.

## Validierung dieses Pakets

Automatisierte Prüfungen sind im Quellprojekt unter `scripts/verify_user_access.cjs`, PHP-Prüfungen unter `server/tests/` dokumentiert. Ein erfolgreicher Quellcode-/Lokaltest ersetzt nicht die oben genannten Tests mit der tatsächlichen MariaDB-11.8-Instanz und dem STRATO-SMTP-Postfach. Ohne Zugangsdaten wurde keine Verbindung zu diesen Diensten hergestellt.
