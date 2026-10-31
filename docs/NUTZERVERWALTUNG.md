# Nutzerverwaltung und zentrale Einstellungen – Vorbereitungsstand

## Umgesetzt
Im Admin-Bereich liegt „Nutzereinstellungen“ direkt vor „Statistik“. Die drei booleschen Einstellungen werden unter `access` gemeinsam mit der gesamten Konfiguration lokal gespeichert, exportiert und importiert:

- `calculators`: Kalkulatoren ohne Registrierung nutzen.
- `pdfDownload`: PDF-Berichte ohne Registrierung speichern/herunterladen.
- `pdfShare`: PDF-Berichte ohne Registrierung versenden/teilen.

Alle Werte sind standardmäßig `true`. Alte Konfigurationen ohne `access` behalten diese öffentlichen Standardwerte. Ungültige Typen werden abgewiesen. Mit „Speichern“ ist hier ausschließlich der PDF-Download gemeint, nicht das Speichern von Kalkulationsständen.

## Noch nicht aktiviert
Es existiert noch keine serverseitige Nutzerverwaltung. Die Checkboxen sind vorbereitete Regeln; sie erzwingen derzeit weder Anmeldung noch Zugriffsrechte. Es wird bewusst keine bloße Browser-Sperre als abgesicherte Anmeldung ausgegeben. Der Admin-Bereich ist weiterhin ohne Anmeldung erreichbar, besitzt aber keine Datenbank-Administrationsrechte. Es wurde kein Administrator in der Datenbank angelegt. Die MariaDB-Verbindung und der SMTP-Versand wurden noch nicht geprüft.

## Infrastruktur
PHP 8.2 und MariaDB 11.8 auf dem vorhandenen STRATO-Webspace. Der E-Mail-Versand ist über SMTP mit TLS vorgesehen. Hostnamen, Datenbanknamen, Benutzernamen und die persönlichen Daten des ersten Administrators werden bei der Installation ausschließlich in einer nicht öffentlichen Serverkonfiguration hinterlegt.

Passwörter gehören niemals in das Repository, einen Export oder die öffentliche Einstellungsantwort.

## Nächster Umsetzungsschritt auf STRATO
1. Vorhandene Website und API-Unterverzeichnis prüfen, ohne WordPress-Routen zu überschreiben.
2. PHP-API, versionierte MariaDB-Migrationen und geschützte Serverkonfiguration installieren.
3. Registrierung und E-Mail-Code-Anmeldung mit Ablauf, Einmalverwendung und Versuchslimits implementieren. Nur Hashes der Codes und Sitzungsschlüssel speichern; keine E-Mail-Codes protokollieren.
4. Das bestätigte Konto des vorgesehenen Administrators einmalig über einen geschützten Einrichtungsweg zum Admin machen. Keine automatische Rechtevergabe allein über eine vom Browser übermittelte E-Mail-Adresse.
5. Sämtliche Admin-Konfigurationen in MariaDB übernehmen; globale Änderungen ausschließlich durch einen authentifizierten, aktiven Admin erlauben. Öffentliche Einstellungen von internen Kontodaten trennen.
6. Benutzerverwaltung mit Sperren/Entsperren/Löschen und Schutz des letzten aktiven Admins ergänzen. Sperrstatus bei jeder geschützten Anfrage prüfen, einschließlich laufender Sitzungen.
7. Die drei Regeln an die verifizierte Sitzung anbinden. Bei `calculators=false` sind auch Berichte aus diesen Kalkulatoren erst nach Anmeldung zugänglich. PDF-Download und Teilen getrennt prüfen; ein Teilen-Fallback auf Download benötigt ebenfalls die Download-Berechtigung. Bei fehlender Berechtigung Anmeldung anzeigen und anschließend die ursprünglich angeforderte Aktion fortsetzen.
8. Globale Einstellungen bei Seitenaufruf und vor geschützten Aktionen frisch laden. Veraltete lokale Entwürfe dürfen veröffentlichte Zugangsregeln nicht überschreiben.
9. Erst nach erfolgreicher Prüfung von Registrierung, Rollen, Sperrstatus, E-Mail-Versand und globaler Speicherung die Registrierungspflicht aktivierbar machen.

GitHub Pages führt kein PHP aus. Die API muss auf STRATO eingerichtet werden; ein GitHub-Commit stellt weder Datenbanktabellen noch das SMTP-Postfach bereit. Ohne Serverzugriff können diese Schritte vorbereitet, aber nicht als installiert oder funktionsgeprüft bezeichnet werden.
