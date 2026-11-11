# Vollständige Website von GitHub Pages auf STRATO übertragen

Planungsstand: 11. November 2026. **Vorbereitet, noch nicht auf STRATO aktiviert.**
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

## Noch benötigte Angaben

- STRATO-Paket beziehungsweise verfügbare SFTP-/SSH-Funktionen.
- SFTP-/SSH-Hostname und das Startverzeichnis eines Deployment-Zugangs.
- Tatsächlicher Zielpfad des öffentlichen Ordners `immocheck-web/`.
- Bestätigung, welches STRATO-Zertifikat Hauptdomain und www abdeckt.

Diese Angaben erlauben die konkrete Workflow-Vorbereitung. Zugangsdaten und
Serveränderungen sind damit noch nicht eingerichtet oder als erledigt behauptet.

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
