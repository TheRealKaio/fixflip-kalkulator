# Vollständige Website von GitHub Pages auf STRATO übertragen

Planungsstand: 11. November 2026. **SFTP geprueft; Test-Upload vorbereitet, noch nicht auf STRATO aktiviert.**
Dieser Plan ersetzt für den vollständigen Website-Umzug die frühere Aufteilung
„www bei GitHub Pages / Hauptdomain für die STRATO-API“. Die vorhandene API und
Datenbank bleiben bestehen. Rechnerformeln und PDFs dürfen zunächst weiterhin
im Browser laufen; ihre PHP-Migration ist eine getrennte Aufgabe.

## Ziel und Domainzuordnung

| Name / Pfad | Ziel nach dem Umzug |
| --- | --- |
| `www.neustart-immocheck.de` | STRATO-Webspace, öffentlicher Website-Ordner `immocheck-web/` |
| `neustart-immocheck.de` | Derselbe öffentliche STRATO-Ordner; Website-Pfade werden nach HTTPS/www weitergeleitet |
| `https://neustart-immocheck.de/api/` | Bestehende API direkt auf STRATO, ohne Weiterleitung auf www |
| `immocheck-private/` | Weiterhin außerhalb des öffentlichen Website-Ordners |

Die veröffentlichte Hauptadresse bleibt `https://www.neustart-immocheck.de/`.
Bestehende Seitenpfade, Canonicals und Links müssen dadurch nicht umbenannt werden.
`assets/backend-config.json` behält zunächst die bestehende HTTPS-API-Adresse
auf der Hauptdomain. Die vorhandenen API-Cookies und erlaubten Origins bleiben
bei der Umstellung erhalten.

## DNS, Webspace und HTTPS

1. Aktuelle Domainzuordnungen, CNAME-/A-/AAAA-Werte, Weiterleitungsdatei und
   Zertifikatszuordnung dokumentieren, damit der Rückweg konkret feststeht.
2. STRATO muss sowohl die Hauptdomain als auch www auf `immocheck-web/` ausliefern
   können. Im Kundenbereich ist dafür die **interne Verzeichniszuordnung** gemeint,
   keine pauschale externe URL-Weiterleitung. Der absolute Uploadpfad hängt vom
   SFTP-/SSH-Zugang ab und ist vor der Workflow-Konfiguration zu bestätigen.
3. Bei www den bisherigen GitHub-CNAME (`therealkaio.github.io`, falls weiterhin
   gesetzt) entfernen und auf den paketbezogenen STRATO-DNS-Standard für den
   Webspace umstellen. Keine Beispiel-IP oder GitHub-IP übernehmen. Auch IPv6
   darf www anschließend nicht mehr zu GitHub führen.
4. Die Hauptdomain liegt laut bisheriger Konfiguration bereits auf STRATO.
   Ihre A-/AAAA-Ziele nur ändern, wenn die tatsächliche Prüfung dies erfordert.
   MX, SPF, DKIM, DMARC und Nameserver nicht pauschal zurücksetzen.
5. Vor dem Wechsel muss das STRATO-Zertifikat **beide Namen** gültig abdecken.
   Das bisherige GitHub-Zertifikat für www wird nicht auf STRATO übertragen.
   Ob das vorhandene STRATO-Zertifikat www einschließt, im konkreten Paket prüfen.
6. DNS erst nach vollständigem Datei-Upload und erfolgreichem Vorabtest ändern.
   Bis alle Resolver den neuen Stand verwenden, bleibt die geprüfte Pages-Version
   als bisheriges Auslieferungsziel verfügbar.

STRATO weist darauf hin, dass eigene DNS-Einstellungen die Nutzung seiner
SSL-Zertifikate einschränken können. Daher die Standardzuordnung des tatsächlichen
Pakets verwenden und kein geratenes CNAME-/IP-Schema erzwingen.

## Veröffentlichungsablauf

Ziel: Entwicklung in GitHub → Übernahme nach main → vollständiger bestehender
Build inklusive PHP-, Rechner-, Browser- und PDF-Prüfungen → Auslieferung des
geprüften Release auf STRATO. Fehlerhafte Prüfungen dürfen keine Produktion ersetzen.

- Das hochgeladene Frontend kommt aus der fertigen Build-Ausgabe `_site/`, nicht
  aus einem direkten Upload des Quellrepositories.
- Übertragung verschlüsselt per SFTP/SSH. Bevorzugt einen eigenen Deployment-Zugang
  verwenden; dessen erreichbares Verzeichnis muss zum bestätigten Zielpfad passen.
- Host, Port, Benutzer, bestätigter Server-Hostkey und Zielpfad werden für den
  Workflow benötigt. Private Schlüssel/Passwörter ausschließlich als GitHub Actions
  Secrets hinterlegen, nie im Repository oder im Chat.
- In einen vorbereiteten Release-Bereich übertragen und erst nach vollständig
  erfolgreicher Übertragung aktivieren. Das konkrete Aktivierungsverfahren ist
  nach Prüfung der verfügbaren SSH-Funktionen und des Zielpfads festzulegen.
- Vorherigen Frontend-Release für Rückkehr aufbewahren; keine automatische Löschung
  unbekannter Dateien im Webspace. `api/`, `immocheck-private/`, `config.php`,
  Datenbank, Uploads und sonstige persistente Daten nicht durch Frontend-Deployment ersetzen.
- Die bestehende `.github/workflows/pages.yml` wird erst nach dem erfolgreichen
  STRATO-Test auf das neue Produktionsziel umgeschaltet. Bis dahin bleibt die
  aktuelle Pages-Veröffentlichung betriebsfähig. GitHub darf danach weiterhin
  Quellcode, Tests und Build-Artefakte verwalten, ohne die Website produktiv zu hosten.

## Weiterleitungen

Die aktuelle Datei `server/webspace/immocheck-web/.htaccess` gehört zum bisherigen
Split-Betrieb: Sie leitet sämtliche Nicht-API-Pfade nach www weiter. Nach dem
www-Umzug würde diese bedingungslose Regel auf demselben Server eine Schleife erzeugen.

Für den vollständigen Umzug liegt eine **noch nicht aktivierte Vorlage** unter
`server/deployment/frontend.htaccess`. Sie:

- lässt `/api/` unverändert auf der bestehenden Hauptdomain;
- leitet nur Website-Anfragen mit abweichendem Host nach www;
- erzwingt HTTPS für Website-Anfragen;
- bewahrt Seitenpfade und vorhandene Query-Parameter;
- verwendet zunächst 302; erst nach Abnahme die Website-Weiterleitungen auf 301 ändern.

Die Vorlage ersetzt die Root-`.htaccess` nur im Rahmen des getesteten Umzugs.
Nicht zusätzlich eine externe Domainweiterleitung im STRATO-Panel aktivieren,
die auch API-Anfragen umleitet. Das vorhandene Installationsformular nicht erneut
hochladen oder ausführen. Die private Serverkonfiguration bleibt unverändert erhalten.

## Abnahme und Rückweg

Vor der DNS-Umschaltung die neue Auslieferung über eine geeignete Vorschau oder
einen kontrollierten Host-Test prüfen. Ein öffentlich erreichbarer Testhost darf
keine privaten Dateien offenlegen; Anmeldung nur mit dafür vorgesehenen Origins testen.

Nach der Umschaltung:

- HTTPS mit und ohne www und Canonical-Weiterleitung ohne Schleife prüfen.
- Startseite, fünf Rechner, Mieterabrechnung, Preise, Warum ImmoCheck?, direkte
  Seitenaufrufe, interne Navigation, Browserhistorie und unbekannte Pfade prüfen.
- Anmeldung, Nutzer-/Adminportal, zentrale Einstellungen, PDF-Download/-Teilen
  und `https://neustart-immocheck.de/api/index.php?r=health` prüfen.
- API-Antworten dürfen nicht durch Website-HTML ersetzt werden.
- Fingerprint-Assets, Service-Worker-Aktualisierung, Mobilansichten und Footer prüfen.
- Erst nach Abnahme die dauerhaften Weiterleitungen und das Abschalten der
  bisherigen Pages-Produktion durchführen.

Bei fehlerhaftem neuen Frontend den vorherigen STRATO-Release wieder aktivieren.
Scheitert die grundsätzliche Hostingumstellung, die notierten DNS-/www-Zuordnungen
zur zuvor geprüften Pages-Auslieferung zurücksetzen und die alte Root-Weiterleitung
wiederherstellen. API, Benutzerkonten und Datenbank dafür nicht löschen oder neu einrichten.
DNS-Rückkehr wirkt wegen zwischengespeicherter Einträge nicht zwingend sofort.

## Bestaetigter Stand und noch offene Schritte

- STRATO-Zugang verwendet SFTP auf Port 22, Startverzeichnis `/`; kein SSH-Shellzugriff vorausgesetzt.
- Host, Benutzer, Passwort und Server-Fingerabdruck sind als Repository-Secrets hinterlegt.
- `ssh-ed25519`-Fingerabdruck wurde mit der bestehenden FileZilla-Verbindung abgeglichen.
- Manueller Modus `check` erfolgreich: `/immocheck-web`, `api/` und `api/index.php` vorhanden.
- Lokale Sicherung des bestehenden Webspace wurde vom Nutzer als erledigt bestaetigt.
- www zeigt weiterhin per CNAME auf `therealkaio.github.io.`; Hauptdomain intern auf `/immocheck-web`.
- Offen: Test-Upload ausfuehren, atomaren Dateitausch bestaetigen, www-SSL pruefen,
  Aktivierung und Rollback implementieren/testen, danach DNS umstellen und erst
  nach Abnahme die automatische STRATO-Produktion einschalten und Pages abschalten.

## Offizielle Anleitungen

- STRATO DNS: https://www.strato.de/faq/domains/wie-kann-ich-bei-strato-meine-dns-eintraege-verwalten/
- STRATO Verzeichniszuordnung: https://www.strato.de/faq/domains/alles-zur-domainumleitung/
- STRATO SSL: https://www.strato.de/faq/domains/so-nutzen-sie-strato-ssl/
- STRATO SFTP/SSH: https://www.strato.de/faq/hosting/so-nutzen-sie-ihren-ssh-sftp-zugang/
- GitHub Deployment-Umgebungen: https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments


## Manueller Verbindungstest (vor jedem Upload)

Der Workflow **STRATO SFTP pruefen** (`.github/workflows/strato-sftp-check.yml`)
ist ausschliesslich manuell startbar und laeuft nur auf `main`.

1. Unter GitHub → Settings → Secrets and variables → Actions sind
   `STRATO_SFTP_HOST`, `STRATO_SFTP_USER` und `STRATO_SFTP_PASSWORD` hinterlegt.
   Die bereits gemeldeten Werte werden nicht in Quelltext oder Protokolle kopiert.
2. Unter Actions den Workflow starten, Branch `main`, Modus `fingerprint`.
   Dieser Modus ermittelt nur den SSH-Server-Fingerabdruck auf Port 22. Er
   erhaelt keinen Benutzernamen und kein Passwort und meldet sich nicht an.
3. Den SHA256-Fingerabdruck mit einem vorhandenen vertrauenswuerdigen
   SFTP-Client-Eintrag oder STRATO abgleichen. Der Scan allein belegt noch keine
   Serveridentitaet. Keinen HiDrive-Fingerabdruck fuer diesen Hosting-Server verwenden.
4. Den bestaetigten Wert als `STRATO_SFTP_FINGERPRINT` speichern und erst dann
   Modus `check` ausfuehren. Bei fehlendem oder abweichendem Fingerabdruck wird
   vor der Passwortanmeldung abgebrochen.
5. Der lesende Test prueft nur Metadaten von `/immocheck-web`, dessen `api/`
   und `api/index.php`. Falls der SFTP-Zugang eine andere Pfadabbildung verwendet,
   den bestaetigten Pfad als Actions-Variable `STRATO_SFTP_ROOT` hinterlegen.
   Er muss weiterhin auf den oeffentlichen Ordner `immocheck-web` zeigen.

Beide Modi veraendern keine Serverdateien, keine DNS-Eintraege und keine
Veröffentlichung. Ein erfolgreicher lesender Test ist noch kein Schreibtest
und aktiviert noch kein automatisches STRATO-Deployment. SSH-Shellzugriff ist
fuer diese SFTP-Pruefung nicht erforderlich.

## Manueller Test-Upload ohne Aktivierung

Workflow **STRATO Testversion hochladen** (`.github/workflows/strato-stage.yml`),
manuell auf `main` starten. Es sind keine zusaetzlichen Secrets erforderlich.

Der komplette bestehende Build und alle bisherigen PHP-, Rechner-, Browser-,
PDF- und Navigationspruefungen liegen jetzt gemeinsam in
`.github/actions/build-site/action.yml`. Pages und der STRATO-Test verwenden
denselben Ablauf; die bisherigen Build-Befehle und ihre Reihenfolge sind erhalten.
Pages bleibt weiterhin das aktive Veroeffentlichungsziel.

Erst nach diesen Pruefungen wird eine frische Version nach
`/immocheck-web/.nic-releases/<commit>-<run>-<attempt>/` uebertragen:

- Nur statische Frontend-Dateien aus `_site/`. Keine PHP-Dateien, API, privaten
  Verzeichnisse, Konfigurationen, symbolischen Links oder Datenbanksicherungen.
  CNAME, Pages-Metadaten und `_checks/` werden nicht ausgeliefert.
- Die vorhandene HTTPS-API-Adresse auf der Hauptdomain muss unveraendert sein.
- Der gespeicherte Server-Fingerabdruck wird vor dem Senden des Passworts geprueft.
- Ein `.htaccess`-Zugriffsschutz im Release-Speicher sperrt direkte Browserzugriffe
  auf `.nic-releases/` mit `Require all denied`. Er veraendert nicht die aktive
  Root-`.htaccess`. Bei der spaeteren Aktivierung muss dieser Staging-Schutz im
  konkret getesteten Auslieferungsverfahren beruecksichtigt werden; ein blosser
  interner Rewrite in den gesperrten Ordner reicht nicht aus.
- Zwei ausschliesslich im neuen Release angelegte Testdateien pruefen die
  SFTP-Erweiterung `posix-rename` durch Ersetzen einer bereits vorhandenen Testdatei.
  Fehlt die Erweiterung, wird ohne unsicheren Loeschen/Umbenennen-Ersatz abgebrochen.
- Jede uebertragene Datei wird zurueckgelesen und ihr SHA256-Hash verglichen.
  Erst nach vollstaendiger Uebertragung wird `.ready.json` geschrieben.
- Bei Abbruch bleibt ein nicht aktivierter, gegebenenfalls unvollstaendiger
  Release-Ordner liegen. Es werden keine fremden Dateien oder aelteren Releases geloescht.
  Ein neuer Workflow-Versuch verwendet eine neue Release-ID.

Ein erfolgreicher Test-Upload ist **keine Aktivierung und noch kein HTTP-/SSL-Test**.
DNS, die bestehende Root-Weiterleitung, API, private Daten und aktive Website bleiben
unveraendert. Der Bericht nennt die Release-ID fuer die anschliessende Aktivierung.
Erst nach bestaetigtem Test-Upload wird der konkrete atomare Wechsel samt Rueckweg
vorbereitet. Der Workflow hat bewusst keinen Push- oder Zeitplan-Trigger.

Technische Referenzen:
- Paramiko SFTP / `posix_rename`: https://docs.paramiko.org/en/stable/api/sftp.html
- Apache Rewrite-Flags und interne Verarbeitung: https://httpd.apache.org/docs/2.4/rewrite/flags.html
