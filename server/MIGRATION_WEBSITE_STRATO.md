# Website auf STRATO: Betrieb und Rückweg

Stand: 12.11.2026. Die Website wird unter <https://www.neustart-immocheck.de/>
von STRATO ausgeliefert. GitHub bleibt Quelle für Entwicklung, Tests und die
anschließende Veröffentlichung nach STRATO.

Die abgeschlossene Erstumschaltung wurde mit
[Lauf 43176907096](https://github.com/TheRealKaio/fixflip-kalkulator/actions/runs/43176907096)
im Modus `activate` erfolgreich geprüft: öffentliche Seiten, Startseiten-Prüfsumme,
HTTPS-Zertifikate für beide Domainnamen, Canonical, Zugriffsschutz und API.

## Domains und Verzeichnisse

| Bestandteil | Verbindliches Ziel |
| --- | --- |
| `neustart-immocheck.de` | STRATO-Webspace, intern `/immocheck-web` |
| `www.neustart-immocheck.de` | STRATO-Standardzuordnung, intern ebenfalls `/immocheck-web` |
| Öffentliche Hauptadresse | `https://www.neustart-immocheck.de/` |
| Bestehende API | `https://neustart-immocheck.de/api/index.php` |
| Frontend-Dateien | Direkt unter `/immocheck-web`, einschließlich Unterverzeichnissen |
| Release- und Sicherungsspeicher | `/immocheck-web/.nic-releases/`, öffentlich gesperrt |
| Private Backend-Konfiguration | Außerhalb des öffentlichen Webroots, `immocheck-private/` |

Der frühere `www`-CNAME auf `therealkaio.github.io` ist entfernt. STRATO verwaltet
die Standard-IP-Zuordnung; keine aus einer einzelnen DNS-Abfrage übernommenen IPs
als feste Konfiguration eintragen. Mail-, TXT- und API-Subdomain-Einträge bleiben
von der Website-Veröffentlichung unberührt. Ein leerer TXT-Eintrag für `www` ist
für diesen Umzug nicht erforderlich.

Die Root-Regeln leiten HTTP und den Domainnamen ohne `www` dauerhaft mit 301 auf
HTTPS und `www` um. Pfad und Query bleiben erhalten. `/api/` und `/.well-known/`
werden vorher ausgenommen, damit API-Aufrufe und Zertifikatsprüfung funktionieren.

## Automatische Veröffentlichung

`.github/workflows/strato-production.yml` heißt **STRATO automatisch veroeffentlichen**.
Jeder Push auf `main` startet denselben vollständigen Build und dieselben
bestehenden Rechner-, PDF-, PHP-, Browser- und Layoutprüfungen wie bisher.
Danach laufen die SFTP-/Rückwegtests und echte Apache-Tests der Auslieferungsregeln.
Nur nach erfolgreichen Prüfungen darf der getestete Build auf STRATO gelangen.

Entwicklung erfolgt im Branch `develop` oder in Arbeitsbranches, die nach `develop` übernommen werden. `develop` veröffentlicht automatisch die getrennte Vorschau auf <https://therealkaio.github.io/fixflip-kalkulator/>. Das Übernehmen
nach `main` veröffentlicht automatisch. Der Workflow lässt sich auf `main` auch
manuell starten. Ein zuletzt überholter Commit wird unmittelbar vor dem
Serverzugriff erkannt und übersprungen; ein neuerer Lauf übernimmt die Auslieferung.

Alle schreibenden STRATO-Workflows teilen die Sperre `strato-production-v2` und
brechen einen laufenden Dateitausch nicht zugunsten eines neueren Pushs ab.
Die API, PHP-Dateien, private Konfiguration, Datenbank, Uploads und DNS werden
vom Frontend-Workflow nicht ersetzt oder neu installiert.

### Ablauf des Dateitauschs

1. Lokalen Build auf erlaubte statische Dateien und unveränderte API-Adresse prüfen.
2. TLS und API-Bereitschaft für Hauptdomain und `www` prüfen.
3. SFTP-Server-Schlüssel mit dem bereits bestätigten Fingerabdruck vergleichen,
   bevor ein Passwort gesendet wird.
4. Aktiven Release, Root-Regeln und öffentliche Dateien anhand ihrer SHA256 prüfen.
5. Falls nötig die bisherigen V1-Regeln einmalig auf V2 erweitern und per HTTP prüfen.
6. Bei bytegleichen Frontend-Dateien erneuten Upload überspringen. Der aktive
   Release behält dann seine bisherige ID; der geprüfte main-Commit steht im Bericht.
7. Einen geänderten Build vollständig in einen neuen isolierten Release laden
   und sämtliche übertragenen Dateien per SHA256 verifizieren.
8. Root-Regeln und jede zu ersetzende Datei sichern, bevor öffentliche Dateien
   verändert werden. Neue Assets zuerst installieren; anschließend beide
   Asset-Generationen in den Root-Regeln freigeben.
9. Weitere JavaScript-/CSS-Einstiegsdateien und danach HTML-Seiten austauschen.
   Die neue Release-Markierung kommt zuletzt.
10. Öffentliche Seiten, Startseiten-Prüfsumme, HTTPS, Canonical, API und Sperren prüfen.
    Bei einem Fehler die vorherigen Dateien und Regeln wiederherstellen und prüfen.

Jede einzelne Datei wird mit geprüftem temporärem Inhalt und atomarem
SFTP-`posix_rename` ersetzt. Der gesamte Satz aller Seiten ist kein einzelner
atomarer Vorgang. Assets mit Prüfsumme im Dateinamen bleiben bei Wechseln und
Rücknahmen erreichbar, damit bereits geöffnete Seiten weiter laden können.
Alte Assets und Sicherungen werden nicht automatisch gelöscht. Eine spätere
Bereinigung muss aktive Seiten, Cache-Nutzung und Rückweg ausdrücklich beachten.

V2-Regeln enthalten `NIC-RELEASE`, `NIC-ROLLBACK`, `NIC-DIRECT-FILES: v2` und eine
geprüfte Liste zusätzlich erlaubter statischer Assets. Unbekannte URLs liefern
404, versteckte Pfade und der Release-Speicher 403. Ein Diagnoseheader ermöglicht
gezielte Inhaltsprüfungen über die Hauptdomain ohne Änderung der normalen
Weiterleitung; solche Antworten sind `no-store` und `noindex`.

## Zugang und Einstellungen

Die vorhandenen GitHub Actions Secrets werden weiterverwendet:

- `STRATO_SFTP_HOST`
- `STRATO_SFTP_USER`
- `STRATO_SFTP_PASSWORD`
- `STRATO_SFTP_FINGERPRINT`

Optional legt die Actions-Variable `STRATO_SFTP_ROOT` den Webroot fest;
Standard ist `/immocheck-web`. Übertragung ausschließlich per SFTP auf Port 22,
kein SSH-Shellzugang erforderlich. Keine Zugangsdaten in Repository oder Log ablegen.
Der Host-Fingerabdruck wurde vor dem ersten authentifizierten Zugriff mit der
bereits vertrauten FileZilla-Verbindung abgeglichen.

## Prüfung und Rückweg

Der manuelle Workflow **STRATO Website umschalten** (`strato-activate.yml`)
verwendet standardmäßig die Release-Eingabe `current`:

| Modus | Zweck |
| --- | --- |
| `check` | Dateien, Prüfsummen und verwaltete Regeln ausschließlich lesen |
| `activate` | Bereits aktiven Release einschließlich öffentlicher HTTP-Auslieferung prüfen |
| `rollback` | Vorherige gesicherte Version auf STRATO wiederherstellen |
| `prepare` | Historischer erster Umzug vor DNS-Wechsel; nicht für neue Produktivversionen |

Neue Versionen werden über den Produktionsworkflow gebaut und ausgeliefert,
nicht durch `activate` auf einen beliebigen alten Release umgeschaltet.

Für eine Rücknahme STRATO → vorherige STRATO-Version `rollback` und `current`
auswählen. Eine DNS-Änderung ist dabei nicht nötig. Gesicherte Originaldateien
werden vor den vorherigen Root-Regeln wiederhergestellt. Dateien, die jemand
zwischenzeitlich außerhalb des Workflows verändert hat, werden nicht ungeprüft
überschrieben. Bei einer solchen Abweichung stoppen und die im Bericht genannten
Sicherungen gezielt prüfen.

Die Sicherungen liegen unter `.nic-releases/.backups/<operation>.htaccess`,
`<operation>.files.json` und gegebenenfalls `<operation>.files/`. Die aktive
`NIC-ROLLBACK`-Markierung benennt die nächste Rücknahme. Ein reines V1→V2-Upgrade
hat eine leere Dateiliste und ändert keine Frontend-Inhalte.

**GitHub Entwicklungsvorschau** (`pages.yml`) veröffentlicht automatisch bei Pushs
auf `develop` und manuell ausschließlich aus diesem Branch. Die Vorschau bleibt
unter `https://therealkaio.github.io/fixflip-kalkulator/` getrennt von STRATO.
Unter Settings → Environments → github-pages muss `develop` als Deployment-Branch zugelassen werden; vorhandene Schutzregeln nicht durch eine zweite Umgebung umgehen.
In GitHub Settings → Pages muss **Custom domain leer** bleiben; die produktive
Domain wird ausschließlich bei STRATO zugeordnet. Das verändert keine DNS-Einträge.

Der gemeinsame vollständige Build wird zuerst unverändert geprüft. Danach erzeugt
`scripts/prepare_github_preview.py` eine separate Ausgabe `_preview/`: lokale URLs
werden auf den Projekt-Unterpfad angepasst, Asset-Prüfsummen neu erzeugt, CNAME
entfernt, robots/noindex gesetzt und das produktive Backend deaktiviert. Der
Browsertest `verify_github_preview.cjs` prüft direkte Routen, interne Wechsel,
Zurück-Navigation und Assets auf Desktop/Mobil sowie fehlende Backend-Zugriffe.
`_site/` und die Live-Konfiguration bleiben unverändert. Benutzeranmeldung und
serverseitige Speicherung sind nur in der Liveversion verfügbar; Recheneingaben
und lokale Vorschau-Einstellungen bleiben im separaten GitHub-Origin.

Neue Änderungen zuerst auf `develop` ansehen, danach durch Übernahme nach `main`
für STRATO freigeben. Der normale Rückweg bleibt die Sicherung auf STRATO. Eine
vollständige Rückkehr der Produktivdomain zu GitHub würde eine erneute Domain-/DNS-
und Zertifikatsplanung benötigen; die Entwicklungsvorschau ersetzt diesen Schritt nicht.
Nur bei der ersten Rücknahme zu den ursprünglichen Regeln verlangt der Workflow
`original_dns_restored=true`. Nicht für eine normale STRATO-Rücknahme anhaken.

## Verantwortliche Quellen

- Gemeinsamer Build: `.github/actions/build-site/action.yml`
- Produktionsworkflow: `.github/workflows/strato-production.yml`
- Veröffentlichung: `scripts/strato_publish.py`
- Auslieferungsregeln, HTTP-Prüfung und Rücknahme: `scripts/strato_activate.py`
- Isolierte Übertragung: `scripts/strato_stage.py`, `strato-stage.yml`
- Lesende Zugangskontrolle: `scripts/strato_sftp_check.py`, `strato-sftp-check.yml`
- Fehlerfalltests: `scripts/test_strato_*.py`
- Apache-/TLS-Integration: `scripts/verify_strato_apache.py`

Die Templates unter `server/deployment/` und `server/webspace/` sind Referenzen
für frühere Installation/Umstellung. Die produktive Root-`.htaccess` wird durch
obige Skripte erzeugt; sie nicht nebenher per FileZilla überschreiben.

Interne Umschreibungen auf versteckte Release-Verzeichnisse funktionierten auf
dem tatsächlichen STRATO-Webspace nicht zuverlässig. Deshalb liegen die
öffentlichen Dateien direkt im Webroot; isolierte Releases dienen der geprüften
Übertragung und Sicherung. Diese Architektur nicht ohne erneuten Origin-Test ändern.
