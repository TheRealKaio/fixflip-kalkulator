# Nutzerverwaltung – V8.352

Die produktive Anbindung ist aktiviert. Die Servereinrichtung wurde abgeschlossen, das Installationsformular gelöscht und `health` mit `ok: true, ready: true` bestätigt. Der erste echte E-Mail-Code und die Admin-Anmeldung sind noch zu prüfen.

## Kostenlose Zertifikatsvariante

Die Zieladresse lautet `https://neustart-immocheck.de/api/index.php`; die Hauptdomain ohne www wird dafür auf STRATO ausgeliefert. Die www-Seite bleibt bei GitHub Pages. Der neue öffentliche Ordner `immocheck-web` leitet alle Nicht-API-Pfade auf www weiter. Privater Code liegt außerhalb dieses Verzeichnisses. DNS, Zertifikat und Dateiinstallation wurden umgestellt; der Betreiber hat die erfolgreiche Einrichtung bestätigt. Die vorhandene `config.php` mit Zugangsdaten bleibt erhalten; lediglich öffentliche Adresswerte werden angepasst. Details und Rückweg: `server/MIGRATION_OHNE_WILDCARD.md`.

## Umfang

- `assets/user-access.js`: Anmeldung/Registrierung mit E-Mail-Code, Benutzerkonto, Zugangskontrolle der App, Benutzerverwaltung für Admins.
- `assets/backend-config.json`: produktiv `enabled: true` nach bestätigter Servereinrichtung.
- `server/webspace/immocheck-web/api/`: öffentlicher PHP-Einstieg und einmaliges Installationsformular.
- `server/webspace/immocheck-private/`: geschützter Programmcode, Datenbankschema, SMTP-Client und Konfigurationsvorlage ohne Zugangsdaten.
- Admin-Reiter Nutzereinstellungen vor Statistik mit drei unabhängigen öffentlichen Zugangsregeln: `calculators`, `pdfDownload`, `pdfShare`. Alle starten mit `true`.
- Bestehender lokaler Modus bleibt erhalten. Im aktivierten zentralen Modus lädt die App Datenbank-Einstellungen statt lokaler Entwürfe; Admin-Speichern veröffentlicht Änderungen über die authentifizierte API mit Versionsprüfung.
- Globale Daten werden auf öffentlichen Seiten bei sichtbarer Seite alle 30 Sekunden nachgeladen. PDF-Aktionen prüfen die aktuellen Zugangsregeln; ein Teilen-Fallback benötigt Download-Berechtigung.
- Nur normale Benutzer können sich öffentlich registrieren. Der erste Admin wird einmalig mit einem geheimen Einrichtungsschlüssel aus der privaten Serverkonfiguration angelegt und muss seine E-Mail bestätigen.
- Admins können Konten sperren, freigeben und löschen. Sperren entfernen Sitzungen und offene Codes, Zugriffsprüfungen lesen den aktuellen Kontostatus. Das eigene Konto und der letzte aktive Admin sind geschützt.
- Admins können alle Nutzerkonten getrennt von der Website-Konfiguration als CSV sichern. Der Export enthält Vorname, Nachname und E-Mail, schließt auch unbestätigte/gesperrte Konten ein und wird über die authentifizierte, paginierte Nutzer-API geladen.
- Anmeldecodes: acht Stellen, zehn Minuten Gültigkeit, maximal fünf Fehlversuche, einmalige Verwendung, HMAC-gehasht gespeichert und begrenzte Anforderungs-/Verifikationsraten.
- Sitzungen: sichere HttpOnly-Cookies, SameSite=Lax, 14 Tage maximale Laufzeit; CSRF-Schutz und genaue CORS-Freigaben.

## Grenzen und offener Betriebsschritt

Die Einrichtung auf STRATO einschließlich Tabellen und erstem Admin-Konto ist laut Betreiber abgeschlossen. Der SMTP-Versand und die vollständige Anmeldung müssen mit der tatsächlichen Serverkonfiguration noch geprüft werden. Die lokale PHP-Prüfung der Sitzungsregeln nutzt eine SQLite-Testdatenbank und ersetzt keinen MariaDB-Integrationstest.

Die App bleibt eine Browser-Anwendung. Die Registrierungspflicht schützt ihre Bedienoberfläche und serverseitige Einstellungen/Kontodaten; öffentlich ausgelieferter Rechnercode lässt sich nicht vor eigenständiger Ausführung schützen. Für eine streng geschützte PDF- oder Berechnungsleistung müsste die Erzeugung auf den Server verlagert werden.

PDF-Versenden bezeichnet die bestehende Geräte-Teilen-Funktion, keinen automatischen Versand von PDF-Anhängen. Persönliche Kalkulationen werden weiterhin nicht zentral gespeichert. Statistik bleibt im bestehenden, zustimmungsabhängigen Modell; es wird keine zentrale Statistikdatenbank behauptet.

Die vollständige Anleitung und die noch durchzuführende Abnahme stehen in `server/INSTALLATION.md`. Serverpasswörter und persönliche Admin-Stammdaten gehören nur in `config.php` auf STRATO und werden nicht mitgeliefert oder auf GitHub veröffentlicht.
