# Nutzerverwaltung – V8.350

Die Oberfläche und das Installationspaket für STRATO sind implementiert. **Der produktive Backend-Schalter bleibt ausgeschaltet**, bis das Paket installiert, die privaten Zugangsdaten eingetragen und Datenbank sowie SMTP geprüft wurden.

## Umfang

- `assets/user-access.js`: Anmeldung/Registrierung mit E-Mail-Code, Benutzerkonto, Zugangskontrolle der App, Benutzerverwaltung für Admins.
- `assets/backend-config.json`: standardmäßig `enabled: false`; Aktivierung ist ein eigener Schritt nach der Servereinrichtung.
- `server/webspace/immocheck-api/`: öffentlicher PHP-Einstieg und einmaliges Installationsformular.
- `server/webspace/immocheck-private/`: geschützter Programmcode, Datenbankschema, SMTP-Client und Konfigurationsvorlage ohne Zugangsdaten.
- Admin-Reiter Nutzereinstellungen vor Statistik mit drei unabhängigen öffentlichen Zugangsregeln: `calculators`, `pdfDownload`, `pdfShare`. Alle starten mit `true`.
- Bestehender lokaler Modus bleibt erhalten. Im aktivierten zentralen Modus lädt die App Datenbank-Einstellungen statt lokaler Entwürfe; Admin-Speichern veröffentlicht Änderungen über die authentifizierte API mit Versionsprüfung.
- Globale Daten werden auf öffentlichen Seiten bei sichtbarer Seite alle 30 Sekunden nachgeladen. PDF-Aktionen prüfen die aktuellen Zugangsregeln; ein Teilen-Fallback benötigt Download-Berechtigung.
- Nur normale Benutzer können sich öffentlich registrieren. Der erste Admin wird einmalig mit einem geheimen Einrichtungsschlüssel aus der privaten Serverkonfiguration angelegt und muss seine E-Mail bestätigen.
- Admins können Konten sperren, freigeben und löschen. Sperren entfernen Sitzungen und offene Codes, Zugriffsprüfungen lesen den aktuellen Kontostatus. Das eigene Konto und der letzte aktive Admin sind geschützt.
- Anmeldecodes: acht Stellen, zehn Minuten Gültigkeit, maximal fünf Fehlversuche, einmalige Verwendung, HMAC-gehasht gespeichert und begrenzte Anforderungs-/Verifikationsraten.
- Sitzungen: sichere HttpOnly-Cookies, SameSite=Lax, 14 Tage maximale Laufzeit; CSRF-Schutz und genaue CORS-Freigaben.

## Grenzen und offener Betriebsschritt

Ohne Installation auf STRATO wurden weder Tabellen noch echte Konten angelegt und keine E-Mail versendet. Die Datenbank-11.8-Kompatibilität und der SMTP-Versand müssen mit der tatsächlichen Serverkonfiguration geprüft werden. Die lokale PHP-Prüfung der Sitzungsregeln nutzt eine SQLite-Testdatenbank und ersetzt keinen MariaDB-Integrationstest.

Die App bleibt eine Browser-Anwendung. Die Registrierungspflicht schützt ihre Bedienoberfläche und serverseitige Einstellungen/Kontodaten; öffentlich ausgelieferter Rechnercode lässt sich nicht vor eigenständiger Ausführung schützen. Für eine streng geschützte PDF- oder Berechnungsleistung müsste die Erzeugung auf den Server verlagert werden.

PDF-Versenden bezeichnet die bestehende Geräte-Teilen-Funktion, keinen automatischen Versand von PDF-Anhängen. Persönliche Kalkulationen werden weiterhin nicht zentral gespeichert. Statistik bleibt im bestehenden, zustimmungsabhängigen Modell; es wird keine zentrale Statistikdatenbank behauptet.

Die vollständige Anleitung und die noch durchzuführende Abnahme stehen in `server/INSTALLATION.md`. Serverpasswörter und persönliche Admin-Stammdaten gehören nur in `config.php` auf STRATO und werden nicht mitgeliefert oder auf GitHub veröffentlicht.
