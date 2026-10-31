# Umstellung ohne zusätzliches Wildcard-Zertifikat

Ziel: Das vorhandene STRATO-Zertifikat für die Hauptdomain verwenden. Die Hauptdomain geht für PHP zurück zum STRATO-Webspace; `www` bleibt direkt bei GitHub Pages. Die Frontend-Anbindung bleibt bis zur Serverprüfung ausgeschaltet.

## 1. Erst Dateien vorbereiten

1. Das neue Paket entpacken.
2. Per SFTP den neuen Ordner `webspace/immocheck-web` neben den vorhandenen Ordner `immocheck-private` hochladen. Der alte Ordner `immocheck-api` darf vorerst bestehen bleiben; nicht löschen.
3. Die versteckten `.htaccess`-Dateien mit übertragen. Im neuen Ordner liegt die API unter `immocheck-web/api/`.
4. **Die bereits ausgefüllte `immocheck-private/config.php` behalten. Nicht durch die leere Vorlage ersetzen.** Falls der private Ordner bereits vollständig hochgeladen wurde, muss er für diese Umstellung nicht neu hochgeladen werden.
5. In der vorhandenen `config.php` nur die folgenden öffentlichen Adresswerte ändern; Passwörter, Admin-Daten, `pepper` und `setup_key` unverändert lassen:

```php
'api_origin' => 'https://neustart-immocheck.de',
'allowed_origins' => [
    'https://neustart-immocheck.de',
    'https://www.neustart-immocheck.de',
],
```

## 2. DNS und Domainzuordnung erst nach Prüfung ändern

Vor Änderungen im STRATO-Kundenbereich Screenshots der bisherigen DNS-Werte und Domainzuordnungen sichern. Die genaue Menüführung und die Standard-IP hängen vom STRATO-Paket ab. Keine fremde STRATO-IP raten oder aus einem Beispiel übernehmen.

1. Bei der **www-Subdomain** prüfen, dass ihr CNAME direkt auf `therealkaio.github.io` zeigt. Er darf nicht auf die Hauptdomain zeigen, sonst würde `www` beim Umstellen ebenfalls bei STRATO landen. GitHub Pages muss weiterhin `www.neustart-immocheck.de` als Custom Domain verwenden.
2. Bei der **Hauptdomain ohne www** die IPv4-A-Einträge auf die von STRATO für dieses Paket angebotene Standard-IP zurückstellen. Vorhandene IPv6-AAAA-Einträge ebenfalls kontrollieren: Sie dürfen nicht weiter zu GitHub zeigen. Entweder STRATO-Standard-IPv6 verwenden oder nach Prüfung nur die GitHub-AAAA-Einträge der Hauptdomain entfernen.
3. Die Hauptdomain unter Webserver intern dem **neuen Ordner `immocheck-web`** zuweisen, nicht `immocheck-web/api` und nicht dem privaten Ordner. Kein allgemeines externes Weiterleitungsziel im STRATO-Panel aktivieren: Die mitgelieferte `.htaccess` nimmt ausschließlich Nicht-API-Pfade von der Weiterleitung aus.
4. Das vorhandene Zertifikat der Hauptdomain zugewiesen lassen und HTTPS für die Hauptdomain prüfen. Kein Wildcard-Zertifikat bestellen. Das vorhandene `www`-Zertifikat wird weiterhin von GitHub Pages ausgeliefert.
5. MX-, SPF-, DKIM-, DMARC- und sonstige Mail-Einträge unverändert lassen. Nicht die ganze DNS-Zone zurücksetzen und keine Nameserver umstellen. Falls ein vorhandener SPF-Eintrag den Mechanismus `a` verwendet, die Auswirkung der geänderten Hauptdomain-IP vorab prüfen.
6. Die neue DNS-Auflösung und beide Serverzuordnungen prüfen. Ein Screenshot allein beweist weder DNS-Ausbreitung noch ein funktionierendes Zertifikat.

## 3. Testen, bevor Anmeldung aktiviert wird

- `https://www.neustart-immocheck.de/` öffnet weiterhin den Kalkulator auf GitHub Pages.
- `https://neustart-immocheck.de/` leitet nach `www` weiter; vorhandene Seitenpfade und Query-Parameter bleiben erhalten. Während der Einrichtung ist dies absichtlich HTTP 302, um falsche dauerhafte Weiterleitungen nicht im Browser festzusetzen. Nach erfolgreicher Abnahme kann 302 in der Root-`.htaccess` auf 301 geändert werden.
- `https://neustart-immocheck.de/api/index.php?r=health` bleibt auf der Hauptdomain und liefert ohne Zertifikatswarnung JSON. Es darf keine Weiterleitung nach `www` erfolgen.
- `https://neustart-immocheck.de/api/install.html` zeigt das Installationsformular. **Es wurde bisher noch keine Datenbankeinrichtung bestätigt.** Nur einmal und erst mit bestätigtem privatem Zugriffsschutz ausführen.
- Eine Anfrage auf `https://neustart-immocheck.de/immocheck-private/config.php` darf niemals Quelltext oder Inhalte liefern. Sie wird mit dieser Ordnerstruktur nicht auf den privaten Ordner abgebildet.
- Die alte API-Subdomain ist für diesen Weg nicht erforderlich. Vor Abschluss der Migration nicht löschen; anschließend kann sie ungenutzt bleiben oder nach gesonderter Entscheidung entfernt werden.

Danach gelten die Schritte für Datenbankeinrichtung, Admin-Anmeldung, E-Mail-Test und Aktivierung aus `INSTALLATION.md`, mit der neuen API-Adresse.

## Rückkehr zum vorherigen Zustand

Solange `assets/backend-config.json` auf `enabled: false` steht, nutzt der veröffentlichte Kalkulator weiterhin den bisherigen lokalen Modus. Scheitert die Domainumstellung, die zuvor notierten A-/AAAA-Werte und die vorherige Domainzuordnung wiederherstellen. Den www-CNAME auf GitHub belassen. Keine Datenbank oder Benutzerkonten löschen.

Die kostenlose Variante nutzt vorhandenes Hosting und vorhandene Zertifikate. Sie ist erst bestätigt, wenn STRATO die Hauptdomain über das vorhandene Zertifikat korrekt ausliefert; die PHP-, MariaDB- und SMTP-Konfiguration wird dadurch nicht automatisch getestet.
