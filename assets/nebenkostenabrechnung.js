(() => {
  'use strict';
  const markup = "<main class=\"wrap\"><div class=\"shell\"><nav class=\"tabs\" aria-label=\"Bereiche\"><button class=\"tab active\" data-page=\"objekte\">Objekte</button><button class=\"tab\" data-page=\"einheiten\">Einheiten</button><button class=\"tab\" data-page=\"kontakte\">Kontakte</button><button class=\"tab\" data-page=\"schluessel\">Verteilerschlüssel</button><button class=\"tab\" data-page=\"einstellungen\">Einstellungen</button><button class=\"tab\" data-page=\"abrechnung\">Mieterabrechnung</button></nav>\n<section class=\"page active\" id=\"objekte\"><div class=\"page-head\"><div><h2>Objekte</h2><div class=\"subtle\">Objekte werden bei Bedarf aus einer WEG-Abrechnung erkannt oder manuell erfasst.</div></div><div class=\"actions\"><button class=\"btn primary\" id=\"addObject\">＋ Objekt hinzufügen</button></div></div><article class=\"card\"><h3>Noch keine Objekte vorhanden</h3><p class=\"muted\">Beim Belegeinlesen wird nur das erkannte Objekt übernommen. Die Adresse kannst du vor dem Speichern korrigieren.</p></article><article class=\"card object-detail\" id=\"objectDetailPanel\" style=\"display:none;margin-top:18px\"><div class=\"split\"><div><h3 id=\"objectDetailTitle\">Objekt erfassen</h3><div class=\"muted\">Objektadresse und Verantwortliche</div></div><button class=\"btn\" id=\"closeObjectDetail\">Schließen</button></div><div class=\"form-grid\"><div class=\"field full\"><label>Objektbezeichnung · WEG + Straße</label><input placeholder=\"Zum Beispiel WEG + Straßenname\"></div><div class=\"field full\"><label>Straße und Hausnummer</label><input placeholder=\"Wird aus dem WEG-Beleg übernommen\"></div><div class=\"field\"><label>Postleitzahl</label><input placeholder=\"Wird erkannt\"></div><div class=\"field\"><label>Ort</label><input placeholder=\"Wird erkannt\"></div><div class=\"field\"><label>Vermieter/in · Standard</label><select id=\"objectLandlord\"><option value=\"\">Kontakt auswählen</option></select></div><div class=\"field\"><label>Hausverwaltung / Verwalter/in</label><select id=\"objectManager\"><option value=\"\">Kontakt auswählen</option></select></div></div><div class=\"callout\">Die Zuordnung gilt für das Objekt. Wohnungen mit abweichendem Vermieter werden einzeln zugeordnet.</div><div class=\"foot-actions\"><button class=\"btn primary\">Objekt speichern</button></div></article></section>\n<section class=\"page\" id=\"einheiten\"><div class=\"page-head\"><div><h2>Einheiten</h2><div class=\"subtle\">Wohnungen werden aus vorhandenen Objektdaten übernommen oder einzeln erfasst.</div><div class=\"object-switcher\"><label for=\"unitObjectSelect\">Objekt</label><select id=\"unitObjectSelect\"><option value=\"\">Objekt auswählen</option></select></div></div><div class=\"actions\"><button class=\"btn primary\">＋ Einheit hinzufügen</button></div></div><div class=\"summary\"><div class=\"metric\"><span>Wohneinheiten</span><strong id=\"unitCount\">0</strong></div><div class=\"metric\"><span>Aktuell vermietet</span><strong id=\"rentedCount\">0</strong></div><div class=\"metric\"><span>Leerstand im Jahr</span><strong id=\"vacantCount\">0</strong></div><div class=\"metric\"><span>Abrechnungszeitraum</span><strong>—</strong></div></div><div class=\"grid two\"><article class=\"card\"><h3>Einheitenübersicht</h3><table class=\"table\"><thead><tr><th>Wohnungsnummer / Einheit</th><th>Etage / Lage</th><th>Fläche</th><th>MEA</th><th>Mietverhältnis</th></tr></thead><tbody id=\"unitRows\"><tr><td colspan=\"5\" class=\"muted\">Noch keine Einheiten erfasst. Beim Einlesen wird nur die eindeutig erkannte Wohnung ergänzt.</td></tr></tbody></table></article><article class=\"card\"><h3>Einheit erfassen</h3><div class=\"form-grid\"><div class=\"field full\"><label>Bezeichnung der Wohnungseinheit</label><input placeholder=\"Wohnungsnummer, Einheit oder Vertragsnummer\"></div><div class=\"field full\"><label>Etage / Lagezusatz · optional</label><input placeholder=\"Nur eintragen, wenn bekannt\"></div><div class=\"field full\"><label>Wohnfläche</label><input placeholder=\"m²\"></div><div class=\"field full\"><label>Eigentumsanteil</label><input placeholder=\"MEA\"></div><div class=\"field full\"><label>Mieter/in</label><select><option value=\"\">Kontakt auswählen</option></select></div></div><p class=\"mini\">Die Bezeichnung der Wohnungseinheit bleibt editierbar. Nicht erkannte Angaben und weitere Wohnungen werden nicht ergänzt.</p></article></div></section>\n<section class=\"page\" id=\"kontakte\"><div class=\"page-head\"><div><h2>Kontakte</h2><div class=\"subtle\">Zentrale Kontaktverwaltung für Vermieter, Verwalter und Mieter</div></div><div class=\"actions\"><button class=\"btn primary\">＋ Kontakt hinzufügen</button></div></div><div class=\"grid two\"><article class=\"card\"><h3>Noch keine Kontakte vorhanden</h3><p class=\"muted\">Kontakte werden einmal zentral angelegt und anschließend einem Objekt oder einer Wohnung zugeordnet.</p></article><article class=\"card\"><h3>Kontakt erfassen</h3><div class=\"form-grid\"><div class=\"field full\"><label>Kontaktrolle</label><select><option value=\"\">Rolle auswählen</option><option>Vermieter/in</option><option>Verwalter/in</option><option>Mieter/in</option></select></div><div class=\"field full\"><label>Vorname</label><input></div><div class=\"field full\"><label>Nachname / Firmenname</label><input></div><div class=\"field full\"><label>Telefon</label><input></div><div class=\"field full\"><label>E-Mail</label><input></div></div><div class=\"section-title\">Anschrift</div><div class=\"form-grid\"><div class=\"field full\"><label>Straße und Hausnummer</label><input></div><div class=\"field full\"><label>Postleitzahl</label><input inputmode=\"numeric\"></div><div class=\"field full\"><label>Ort</label><input></div></div><div class=\"section-title\">Bankverbindung · optional</div><div class=\"form-grid\"><div class=\"field full\"><label>Kontoinhaber/in</label><input></div><div class=\"field full\"><label>Kreditinstitut</label><input></div><div class=\"field full\"><label>IBAN</label><input autocomplete=\"off\"></div><div class=\"field full\"><label>BIC</label><input autocomplete=\"off\"></div></div></article></div></section>\n<section class=\"page\" id=\"schluessel\"><div class=\"page-head\"><div><h2>Verteilerschlüssel</h2><div class=\"subtle\">Je Objekt werden nur die benötigten Schlüssel aus dem globalen Katalog ausgewählt.</div></div></div><div class=\"field\" style=\"max-width:420px;margin-bottom:16px\"><label for=\"keyObjectSelect\">Objekt</label><select id=\"keyObjectSelect\"><option value=\"\">Objekt auswählen</option></select></div><article class=\"card\"><h3>Noch keine objektbezogenen Zuordnungen</h3><p class=\"muted\">Nach Auswahl eines Objekts ordnest du den vorhandenen globalen Schlüsseln die benötigten Kostenpositionen zu. Die Wohnung liefert ihren jeweiligen Anteil.</p><button class=\"btn\">Globalen Katalog unter Einstellungen öffnen</button></article></section>\n<section class=\"page\" id=\"einstellungen\"><div class=\"page-head\"><div><h2>Einstellungen</h2><div class=\"subtle\">Globale Grundlagen für die Abrechnung verwalten</div></div></div><div class=\"grid two\"><article class=\"card\"><div class=\"split\"><div><h3>Globaler Verteilerschlüssel</h3><div class=\"muted\">Ein zentraler Katalog, aus dem jedes Objekt die benötigten Schlüssel auswählt.</div></div><button class=\"btn primary\">＋ Verteilerschlüssel hinzufügen</button></div><div class=\"callout\" style=\"margin:14px 0\">Ein hier neu angelegter Schlüssel steht anschließend allen Objekten zur Auswahl. Er wird einem Objekt erst zugeordnet, wenn du ihn dort tatsächlich benötigst.</div><table class=\"table\"><thead><tr><th>Verteilerschlüssel</th><th>Bezugsgröße</th><th>Einheit</th><th>Status</th></tr></thead><tbody><tr><td><span class=\"name\">Wohnfläche</span></td><td>Fläche der Einheit</td><td>m²</td><td><span class=\"badge\">Global</span></td></tr><tr><td><span class=\"name\">Wohneinheit</span></td><td>gleicher Anteil je Einheit</td><td>Einheit</td><td><span class=\"badge\">Global</span></td></tr><tr><td><span class=\"name\">Eigentumsanteil (MEA)</span></td><td>Miteigentumsanteile</td><td>MEA</td><td><span class=\"badge\">Global</span></td></tr><tr><td><span class=\"name\">Verbrauch</span></td><td>Messwerte der Einheit</td><td>Messgröße</td><td><span class=\"badge\">Global</span></td></tr><tr><td><span class=\"name\">Direktzuordnung</span></td><td>vollständig einer Einheit zuordnen</td><td>Euro</td><td><span class=\"badge\">Global</span></td></tr></tbody></table><p class=\"mini\">Eigene Schlüssel legst du einmal hier an. Die Zuordnung zu Kostenarten und Objekten bleibt separat.</p></article><article class=\"card\"><h3>So greifen die Ebenen ineinander</h3><div class=\"section-title\"><span class=\"icon\">1</span>Globaler Katalog</div><p class=\"muted\">Verfügbare Rechenarten wie Wohnfläche, MEA oder Verbrauch.</p><div class=\"section-title\"><span class=\"icon\">2</span>Objekt</div><p class=\"muted\">Für jede Kostenposition wird der passende Schlüssel aus dem Katalog ausgewählt.</p><div class=\"section-title\"><span class=\"icon\">3</span>Einheit</div><p class=\"muted\">Die jeweilige Wohnung liefert ihren Anteil, zum Beispiel 43,14 m² oder den erfassten Verbrauch.</p><div class=\"callout\">Ein Schlüssel wird zentral gepflegt, aber nicht automatisch auf jedes Objekt angewendet. So kannst du ihn nur dort einsetzen, wo er gebraucht wird.</div></article></div></section>\n<section class=\"page\" id=\"abrechnung\"><div class=\"page-head\"><div><h2>Mieterabrechnung</h2><div class=\"subtle\">Abrechnung aus einem WEG-Beleg einlesen oder manuell erfassen</div></div><div class=\"actions\"><button class=\"btn\" id=\"showReceipts\">Abrechnungen anzeigen</button></div></div>\n<div id=\"entryModeState\" class=\"callout\" style=\"margin-bottom:16px\">Wähle den Start: Beim Upload liest das System den Beleg ein. Bei der manuellen Erfassung überspringst du diesen Schritt.</div><div id=\"uploadSelection\" class=\"mini\" aria-live=\"polite\" style=\"margin:-8px 0 16px\"></div>\n<div class=\"wizard-steps\" role=\"tablist\" aria-label=\"Abrechnungsschritte\"><button class=\"wizard-step active\" type=\"button\" data-step=\"0\"><b>1 · Beleg</b><span>Hochladen und erkennen</span></button><button class=\"wizard-step\" type=\"button\" data-step=\"1\"><b>2 · Angaben</b><span>Objekt, Einheit, Kontakt</span></button><button class=\"wizard-step\" type=\"button\" data-step=\"2\"><b>3 · Positionen</b><span>Zuordnen und erfassen</span></button><button class=\"wizard-step\" type=\"button\" data-step=\"3\"><b>4 · Verteilung</b><span>Je Wohnung prüfen</span></button><button class=\"wizard-step\" type=\"button\" data-step=\"4\"><b>5 · Vorschau</b><span>Abrechnung ansehen</span></button></div>\n<div class=\"wizard-panel active\" data-panel=\"0\"><div class=\"step-heading\"><h3>1. Beleg hochladen oder manuell erfassen</h3><button class=\"btn primary\" data-next>Weiter zu den Angaben →</button></div><p class=\"muted\">Wähle hier, ob du die WEG-Abrechnung hochladen, die Abrechnung manuell erfassen oder eine Heizkostenabrechnung ergänzen möchtest. Beim Upload liest das System die erkennbaren Angaben aus und übernimmt nur die eindeutig identifizierte Wohnung.</p><div class=\"actions\"><button class=\"btn primary\" type=\"button\" id=\"wegUploadButton\">＋ WEG-Abrechnung hochladen</button><input id=\"wegUploadInput\" type=\"file\" accept=\".pdf,image/*\" multiple hidden><button class=\"btn\" type=\"button\" id=\"startManual\">＋ Manuell erfassen</button><input id=\"heaterUploadInput\" type=\"file\" accept=\".pdf,image/*\" multiple hidden><button class=\"btn\" type=\"button\" id=\"heaterUpload\">＋ Heizkostenabrechnung ergänzen</button></div><div id=\"heatingSelection\" class=\"mini\" style=\"margin-top:10px\"></div><div class=\"wizard-nav\"><span class=\"mini\">Bei manueller Erfassung wird dieser Schritt übersprungen.</span></div></div>\n<div class=\"wizard-panel\" data-panel=\"1\"><div class=\"step-heading\"><h3>2. Erkannte Angaben prüfen oder manuell ergänzen</h3><div class=\"step-heading-actions\"><button class=\"btn back-step\" data-prev>← Zurück</button><button class=\"btn primary\" data-next>Weiter zu den Positionen →</button></div></div><div class=\"section-title\"><span class=\"icon\">⌂</span>Objekt</div><div class=\"form-grid\"><div class=\"field full\"><label for=\"objectName\">Objektbezeichnung · WEG + Straße</label><input id=\"objectName\" type=\"text\" placeholder=\"Wird aus WEG-Name und Straße gebildet\"></div><div class=\"field full\"><label for=\"objectStreet\">Straße und Hausnummer</label><input id=\"objectStreet\" type=\"text\" placeholder=\"Wird aus dem Beleg übernommen\"></div><div class=\"field\"><label for=\"objectPostal\">Postleitzahl</label><input id=\"objectPostal\" type=\"text\" inputmode=\"numeric\" placeholder=\"Wird erkannt\"></div><div class=\"field\"><label for=\"objectCity\">Ort</label><input id=\"objectCity\" type=\"text\" placeholder=\"Wird erkannt\"></div><div class=\"field\"><label for=\"wizardYear\">Abrechnungsjahr</label><input id=\"wizardYear\" type=\"number\" placeholder=\"Wird aus dem Beleg erkannt\"></div><div class=\"field\"><label for=\"wizardFrom\">WEG-Beginn · fest</label><input id=\"wizardFrom\" type=\"text\" placeholder=\"01.01. des Abrechnungsjahres\" readonly></div><div class=\"field\"><label for=\"wizardTo\">WEG-Ende · fest</label><input id=\"wizardTo\" type=\"text\" placeholder=\"31.12. des Abrechnungsjahres\" readonly></div></div><div class=\"section-title\"><span class=\"icon\">⌂</span>Eine erkannte Wohnung</div><div class=\"form-grid\"><div class=\"field full\"><label for=\"reviewUnit\">Bezeichnung der Wohnungseinheit</label><input id=\"reviewUnit\" type=\"text\" placeholder=\"Wohnungsnummer, Einheit oder Vertragsnummer\"></div><div class=\"field\"><label for=\"unitLocation\">Etage / Lagezusatz · optional</label><input id=\"unitLocation\" type=\"text\" placeholder=\"Nur ausfüllen, wenn erkannt\"></div><div class=\"field\"><label for=\"tenantContact\">Mieter/in</label><select id=\"tenantContact\"><option value=\"\">Kontakt auswählen oder ergänzen</option></select></div><div class=\"field\"><label for=\"objectMatch\">Vorhandenes Objekt · optionaler Abgleich</label><select id=\"objectMatch\"><option value=\"\">Adresse mit vorhandenem Objekt abgleichen</option></select></div></div><div class=\"section-title\"><span class=\"icon\">◷</span>Mietzeitraum der Wohnung</div><div class=\"form-grid\"><div class=\"field\"><label for=\"tenantFrom\">Mietbeginn</label><input id=\"tenantFrom\" type=\"date\"></div><div class=\"field\"><label for=\"tenantTo\">Mietende</label><input id=\"tenantTo\" type=\"date\"></div></div><p class=\"mini\">Der WEG-Zeitraum läuft vom 1. Januar bis 31. Dezember. Bei Ein- oder Auszug passt du hier den Mietzeitraum an.</p><div class=\"wizard-nav\"><span class=\"mini\">Straße, Hausnummer, Postleitzahl und Ort werden aus dem Beleg übernommen und bleiben korrigierbar. Für die Einheit wird nur die erkannte Nummer oder Bezeichnung angelegt; ein Lagezusatz erscheint nur, wenn er erkennbar ist.</span></div></div>\n<div class=\"wizard-panel\" data-panel=\"2\"><div class=\"step-heading\"><h3>3. Positionen zuordnen und erfassen</h3><div class=\"step-heading-actions\"><button class=\"btn back-step\" data-prev>← Zurück</button><button class=\"btn primary\" data-next>Weiter zur Verteilung →</button></div></div><p class=\"muted\" id=\"positionModeHint\">Beim Upload werden erkannte Positionen und Beträge hier eingetragen. Bei manueller Erfassung bleiben die Betragsfelder leer; Standardpositionen sind bereits vorbereitet.</p><div class=\"position-table-wrap\"><table class=\"table review-table position-table\" id=\"unitReviewTable\"><thead><tr><th>Position</th><th>Verteilerschlüssel</th><th>Verteilungsrelevanter Betrag</th><th>Gesamtverteiler</th><th>Ihr Anteil</th><th>Ihr Betrag</th><th aria-label=\"Aktion\"></th></tr></thead><tbody id=\"positionTemplateBody\"></tbody></table></div><div class=\"split\" style=\"margin-top:12px\"><button class=\"btn\" id=\"addReviewPosition\">＋ Eigene Position hinzufügen</button><span class=\"mini\">Die sechs Spalten sind für beide Erfassungswege gleich. Zwischensummen und Endsummen werden je Kostenblock gebildet.</span></div><div class=\"wizard-nav\"><span class=\"mini\">Nicht im Muster enthaltene Zeilen kannst du ergänzen.</span></div></div>\n<div class=\"wizard-panel\" data-panel=\"3\"><div class=\"step-heading\"><h3>4. Verteilung je Wohnung prüfen</h3><div class=\"step-heading-actions\"><button class=\"btn back-step\" data-prev>← Zurück</button><button class=\"btn primary\" data-next>Weiter zur Mietervorschau →</button></div></div><div class=\"callout\">Prüfe die Verteilung ausschließlich für die eine erkannte oder manuell bezeichnete Wohnung. Das Objekt liefert den vorgesehenen Verteilerschlüssel; ihre Fläche, MEA oder Verbrauchswerte werden nur übernommen, wenn sie vorhanden und eindeutig zugeordnet sind.</div><div class=\"card\" style=\"margin-top:14px\"><h4>Prüfstatus der Einheiten</h4><div id=\"unitDistributionStatus\" class=\"mini\">Nach der Bestätigung wird ausschließlich die erkannte oder manuell bezeichnete Wohnung geprüft. Nicht erkannte Etagen, Lagezusätze oder weitere Wohnungen werden nicht ergänzt.</div></div><div class=\"wizard-nav\"><span class=\"mini\">Korrekturen an Positionen bleiben in Schritt 3 möglich.</span></div></div>\n<div class=\"wizard-panel\" data-panel=\"4\"><div class=\"step-heading\"><h3>5. Mietervorschau</h3><div class=\"step-heading-actions\"><button class=\"btn back-step\" data-prev>← Zurück</button><button class=\"btn primary\" id=\"showPreview\">Mietervorschau erstellen →</button></div></div><div class=\"callout\">Die Vorschau enthält die bestätigten, umlagefähigen Kosten, die Vorauszahlungen und das Ergebnis für die ausgewählte Wohnung. Sie ist die fertige Abrechnung zum Prüfen und Versenden.</div><div id=\"previewReady\" class=\"metric\" style=\"margin-top:14px\"><span>Abrechnung</span><strong>Vorschau noch nicht erstellt</strong></div><div class=\"wizard-nav\"><span class=\"mini\">Die Vorschau ist nicht mehr die Eingabemaske.</span></div></div>\n<div class=\"callout\"><b>Erfassungswege:</b> Beim Upload wird diese Vorlage mit den erkannten Werten befüllt. Bei manueller Erfassung startet dieselbe Tabelle leer mit den Standardpositionen. Die Heizkostenabrechnung kann zusätzlich angehängt werden.</div>\n</section>\n</div></main>\n<div class=\"preview-overlay\" id=\"printPreview\" role=\"dialog\" aria-modal=\"true\" aria-label=\"A4-Abrechnungsvorschau\">\n  <div class=\"preview-toolbar\"><span>Abrechnungsvorschau · A4 Hochformat</span><div><button class=\"btn\" id=\"closePreview\">Schließen</button><button class=\"btn primary\" id=\"printPreviewButton\">Drucken / PDF</button></div></div>\n  <div class=\"preview-modes\"><button class=\"btn active\" data-preview-mode=\"tenant\">Mietervorschau · ausgewählte Wohnung</button></div>\n  <section class=\"a4-page tenant-doc\"><div class=\"a4-head\"><div><h2>Betriebskostenabrechnung</h2><p><b>Mietervorschau · ausgewählte Wohnung</b></p><p>Objekt und Anschrift werden aus den bestätigten Angaben übernommen.</p></div><div class=\"a4-meta\">Abrechnungszeitraum<br><b>Zeitraum aus den bestätigten Angaben</b></div></div><div class=\"tenant-content\"></div><div class=\"a4-note\">Diese Mietervorschau enthält ausschließlich als umlagefähig gekennzeichnete Positionen. Vorauszahlungen und das daraus entstehende Guthaben oder die Nachzahlung werden in der fertigen Mieterabrechnung zusätzlich berücksichtigt.</div><footer class=\"a4-footer\"><p><b>Vermieter/in</b> · [Name] · [Anschrift]<br>[Telefon] · [E-Mail]</p><p><b>Bankverbindung</b> · [Kontoinhaber/in] · [Bank]<br>IBAN [IBAN] · BIC [BIC]</p></footer></section>\n</div>";
  const styles = "\n:host{--nic-font:system-ui,-apple-system,\"Segoe UI\",sans-serif;--nic-body-font-size:16px;--nic-subtext-font-size:14px;--nic-hint-font-size:12px;--nic-h1-size:45px;--nic-h2-size:22px;--nic-brand-radius:22px;--nic-background:#F5F7FB;--nic-outer-background:#F6F1E9;--nic-ink:#172033;--nic-green:#075C55;--nic-teal:#16867A;--nic-mint:#DDECE8;--nic-border:#E2E9E5;--nic-button:#0F172A;--nic-muted:#687385;--nic-red:#B42318;--nic-red-bg:#FEECEB;--nic-yellow:#FDE68A;--nic-card:#fff;--nic-shadow:0 10px 30px rgba(23,32,51,.07)}\n*{box-sizing:border-box}:host{display:block;min-width:0;color:var(--nic-ink);font:400 var(--nic-body-font-size)/1.5 var(--nic-font)}button,input,select{font:inherit;color:inherit}button{cursor:pointer}.brandbar{background:#fff;border-bottom:1px solid #e9e1d6}.brand-inner{max-width:1240px;margin:auto;padding:14px 28px;min-height:86px;display:grid;grid-template-columns:250px 1fr auto;gap:22px;align-items:center}.brand{display:flex;align-items:center;gap:10px;color:var(--nic-green);font-weight:800;letter-spacing:-.04em;font-size:20px;white-space:nowrap}.brand-mark{width:34px;height:34px;border:3px solid var(--nic-green);border-radius:10px 10px 10px 2px;display:grid;place-items:center;font-size:17px}.brand-desc{border-left:1px solid #cbd2cf;padding-left:18px;font-size:13px;line-height:1.45;color:#52605e}.topnav{display:flex;align-items:center;gap:24px;font-size:14px;white-space:nowrap}.topnav a{color:var(--nic-ink);text-decoration:none}.topnav .portal{border-radius:14px;background:var(--nic-green);color:white;padding:9px 15px;font-weight:700}.hero{background:linear-gradient(95deg,#f6f1e9 0%,#f2eee8 53%,#e4ece6 100%);border-bottom:1px solid rgba(7,92,85,.08)}.hero-inner{max-width:1184px;margin:auto;padding:30px 28px 27px}.eyebrow{color:var(--nic-green);font-size:var(--nic-subtext-font-size);font-weight:700;letter-spacing:.06em;text-transform:uppercase}.hero h1{font-size:var(--nic-h1-size);line-height:1.1;letter-spacing:-.035em;margin:5px 0 8px;color:var(--nic-green)}.hero p{margin:0;color:#354543;max-width:820px}.wrap{width:100%;max-width:none;margin:0;padding:0}.shell{background:var(--nic-card);border:1px solid var(--nic-border);border-radius:var(--nic-brand-radius);box-shadow:var(--nic-shadow);overflow:visible}.tabs{display:flex;gap:4px;padding:14px 20px 0;border-radius:21px 21px 0 0;border-bottom:1px solid var(--nic-border);background:#fff}.tab{border:0;background:transparent;padding:11px 18px 13px;color:#596674;border-bottom:3px solid transparent;font-weight:650}.tab.active{color:var(--nic-green);border-color:var(--nic-green)}.page{display:none;padding:24px}.page.active{display:block}.page-head{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;margin-bottom:20px}.object-switcher{display:flex;align-items:center;gap:10px;margin-top:12px}.object-switcher label{font-size:var(--nic-subtext-font-size);font-weight:650;color:#596674}.object-switcher select{min-width:310px;border:1px solid #d8dfdc;border-radius:10px;background:#fff;padding:9px 12px;min-height:42px}.page-head h2{margin:0 0 3px;color:var(--nic-ink);font-size:var(--nic-h2-size);line-height:1.25}.subtle{color:var(--nic-muted);font-size:var(--nic-subtext-font-size)}.actions{display:flex;gap:10px;flex-wrap:wrap}.btn{border:1px solid var(--nic-border);background:#fff;border-radius:12px;padding:9px 14px;font-weight:650;font-size:var(--nic-subtext-font-size)}.btn.primary{border-color:var(--nic-green);background:var(--nic-green);color:#fff}.btn.soft{color:var(--nic-green);background:#f2f8f6}#abrechnung>.page-head .actions{flex-wrap:nowrap;gap:8px}#abrechnung>.page-head .actions>.btn{flex:0 1 204px;width:204px;min-width:190px;padding:8px;font-size:13px;white-space:nowrap;text-align:center}#abrechnung [data-panel=\"0\"] .actions{flex-wrap:nowrap}#abrechnung [data-panel=\"0\"] .actions>.btn{flex:0 0 240px;width:240px;min-width:240px;white-space:nowrap;text-align:center}#abrechnung [data-panel=\"0\"] #heaterUpload{flex:0 0 280px;width:280px;min-width:280px}#abrechnung .wizard-step{white-space:nowrap}.grid{display:grid;gap:18px}.grid.two{grid-template-columns:1.15fr .85fr}.grid.equal{grid-template-columns:1fr 1fr}.card{background:#fff;border:1px solid var(--nic-border);border-radius:16px;padding:18px}.card h3{margin:0 0 14px;font-size:18px;line-height:1.25}.card h4{margin:0 0 10px;font-size:15px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px 16px}.field label{display:block;font-size:var(--nic-subtext-font-size);color:#596674;margin-bottom:5px}.field input,.field select{width:100%;border:1px solid #d8dfdc;border-radius:10px;background:#fff;padding:10px 12px;min-height:42px}.field .hint{display:block;margin-top:4px;color:var(--nic-muted);font-size:var(--nic-hint-font-size)}.full{grid-column:1/-1}.toolbar{display:flex;gap:12px;align-items:center;margin-bottom:16px}.search{flex:1;max-width:400px;border:1px solid #d8dfdc;background:#f7f8f9;border-radius:11px;padding:10px 13px}.table{width:100%;border-collapse:collapse;font-size:var(--nic-subtext-font-size)}.table th{text-align:left;color:#687385;font-size:12px;font-weight:700;border-bottom:1px solid var(--nic-border);padding:10px 9px}.table td{padding:12px 9px;border-bottom:1px solid #edf0ef;vertical-align:middle}.table tr:last-child td{border-bottom:0}.name{font-weight:680;color:var(--nic-ink)}.muted{color:var(--nic-muted)}.badge{display:inline-flex;align-items:center;border-radius:999px;padding:4px 10px;background:var(--nic-mint);color:var(--nic-green);font-size:12px;font-weight:750;white-space:nowrap}.badge.warn{background:#fff4d7;color:#7b5700}.badge.red{background:var(--nic-red-bg);color:var(--nic-red)}.section-title{display:flex;align-items:center;gap:9px;color:var(--nic-green);font-weight:750;margin:18px 0 10px}.section-title:first-child{margin-top:0}.icon{width:25px;height:25px;border-radius:8px;background:var(--nic-mint);display:inline-grid;place-items:center;color:var(--nic-green);font-size:14px}.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}.metric{border:1px solid var(--nic-border);border-radius:13px;background:#fbfcfc;padding:12px 14px}.metric span{display:block;color:var(--nic-muted);font-size:12px}.metric strong{font-size:17px}.meter-list{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.meter{border:1px solid var(--nic-border);border-radius:12px;padding:12px}.meter b{display:block;font-size:14px}.meter small{color:var(--nic-muted)}.callout{padding:12px 14px;background:#f1f8f6;border-left:3px solid var(--nic-green);border-radius:8px;color:#40514e;font-size:var(--nic-subtext-font-size)}.split{display:flex;align-items:center;justify-content:space-between;gap:12px}.mini{font-size:12px;color:var(--nic-muted)}.footer{max-width:1184px;margin:16px auto 30px;padding:14px 28px;color:#64716e;font-size:12px;display:flex;justify-content:space-between}.badge-count{margin-left:6px;background:#e9eef1;color:#41515a;border-radius:999px;padding:2px 8px;font-size:12px}.screen-note{font-size:11px;color:#74817f;margin-top:12px}.keyline{display:grid;grid-template-columns:minmax(150px,1.1fr) minmax(190px,1.15fr) minmax(200px,1.2fr) minmax(100px,.75fr) 72px;gap:10px;align-items:center;padding:12px 10px;border-bottom:1px solid #edf0ef;font-size:var(--nic-subtext-font-size)}.keyline>*{min-width:0;text-align:left;justify-self:stretch}.keyline.head{color:#687385;font-size:12px;font-weight:700}.keyline.head>*{text-align:left}.keyline select{text-align:left;text-align-last:left}.keyline:last-child{border-bottom:0}.grid.two>.card{min-width:0}.rent-history{width:100%;max-width:100%;min-width:0}.rent-history .keyline{grid-template-columns:minmax(0,1.55fr) minmax(0,.9fr) repeat(3,minmax(0,.85fr));gap:4px;min-width:0;padding:8px 3px;font-size:10px}.rent-history .keyline>*{white-space:normal;overflow-wrap:anywhere;line-height:1.3}.rent-history .keyline.head{display:grid}.control{color:var(--nic-green);font-weight:700}.bank{font-family:ui-monospace,monospace;font-size:12px}.right{text-align:right}.smallcaps{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#71807d}.foot-actions{display:flex;justify-content:flex-end;gap:9px;margin-top:16px}\n.open-object{border:0;background:transparent;padding:0;font:inherit}.open-object:hover{text-decoration:underline}.object-detail{scroll-margin-top:20px}.review-toolbar{display:grid;grid-template-columns:1fr 1fr 150px;gap:14px;align-items:end;margin:12px 0}.review-period{border:1px solid var(--nic-border);border-radius:10px;padding:8px 12px;min-height:42px}.review-period span,.review-period strong{display:block}.review-period strong{font-size:15px}.review-table-wrap{width:100%;max-height:520px;overflow:auto}.position-table-wrap{width:100%;max-height:520px;overflow:auto;overscroll-behavior:contain}.position-table{width:100%;border-collapse:separate;border-spacing:0}.position-table thead th{position:sticky;top:0;background:#fff;z-index:5;box-shadow:0 1px 0 var(--nic-border)}.position-table .group-row td{background:#f1f8f6;color:var(--nic-green);font-weight:750}.position-table .subtotal-row td{background:#f8faf9;font-weight:700}.position-table .add-row td{padding:5px 9px}.position-table .review-input{min-width:0}.review-table{min-width:900px;table-layout:fixed}.review-table th:nth-child(1){width:16%}.review-table th:nth-child(2){width:17%}.review-table th:nth-child(3){width:19%}.review-table th:nth-child(4){width:16%}.review-table th:nth-child(5){width:13%}.review-table th:nth-child(6){width:13%}.review-table th:nth-child(7){width:6%}.position-action-cell{text-align:center!important;padding-left:2px!important;padding-right:2px!important}.remove-position{width:25px;height:25px;padding:0;border:1px solid #d8dfdc;border-radius:50%;background:#fff;color:#687385;font-size:18px;line-height:1}.remove-position:hover{border-color:#b42318;background:#feeceb;color:#b42318}.review-input{width:100%;min-width:0;min-height:38px;border:1px solid #d8dfdc;border-radius:8px;padding:7px 8px;background:#fff;font-size:13px}.wizard-steps{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin:4px 0 12px}.wizard-step{border:1px solid var(--nic-border);background:#fff;border-radius:14px;padding:11px 12px;text-align:left;color:var(--nic-ink)}.wizard-step b,.wizard-step span{display:block}.wizard-step span{font-size:12px;color:var(--nic-muted);margin-top:3px}.wizard-step.active{border-color:var(--nic-green);background:#f1f8f7;color:var(--nic-green)}.wizard-panel{display:none;height:420px;border:1px solid var(--nic-border);border-radius:16px;padding:18px;margin-bottom:18px;background:#fff}.wizard-panel.active{display:flex;flex-direction:column}#abrechnung .wizard-panel[data-panel=\"1\"]{height:auto;min-height:420px;padding:14px}#abrechnung .wizard-panel[data-panel=\"1\"] .form-grid{gap:8px 12px}#abrechnung .wizard-panel[data-panel=\"1\"] .field label{margin-bottom:3px}#abrechnung .wizard-panel[data-panel=\"1\"] .field input,#abrechnung .wizard-panel[data-panel=\"1\"] .field select{min-height:36px;padding:7px 9px}#abrechnung .wizard-panel[data-panel=\"2\"]{height:auto;min-height:420px}#abrechnung .wizard-panel[data-panel=\"2\"] .position-table-wrap{flex:none;min-height:0;max-height:520px;overflow:auto;overscroll-behavior:contain}.wizard-panel h3{margin:0;font-size:18px}.wizard-panel .step-heading{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:12px}.step-heading-actions{display:flex;align-items:center;gap:14px;flex:0 0 auto}.step-heading-actions .back-step{font-size:13px;padding:7px 11px;min-height:36px;white-space:nowrap}.wizard-panel .step-heading h3{flex:1;min-width:0}.wizard-panel .step-heading button[data-next],.wizard-panel .step-heading #showPreview{width:220px;min-width:220px;flex:0 0 220px;white-space:nowrap;text-align:center;background:#f6c944;border-color:#e1b52b;color:#302600}.wizard-panel .step-heading button[data-next]:hover,.wizard-panel .step-heading #showPreview:hover{background:#edbd2f}.wizard-nav{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:auto;padding-top:18px}.wizard-nav .mini{flex:1}@media(max-width:850px){#abrechnung .wizard-panel[data-panel=\"1\"] .form-grid{grid-template-columns:1fr}.wizard-panel{height:520px}.review-toolbar{grid-template-columns:1fr}.review-table{min-width:860px}.wizard-steps{grid-template-columns:repeat(2,minmax(0,1fr))}.wizard-nav{flex-wrap:wrap}.wizard-nav .mini{flex-basis:100%;order:3}}\n.preview-overlay{display:none;position:fixed;inset:0;z-index:50;background:rgba(18,28,39,.72);overflow:auto;padding:24px}.preview-overlay.open{display:block}.preview-toolbar{max-width:210mm;margin:0 auto 14px;display:flex;justify-content:space-between;align-items:center;color:#fff}.preview-toolbar .btn{margin-left:8px;color:#172033}.preview-toolbar .btn.primary{color:#fff}.preview-modes{display:flex;gap:8px;margin:0 auto 14px;max-width:210mm}.preview-modes .btn.active{background:#dceeea;border-color:#8bbeb5;color:#075c55}.preview-overlay.landlord-mode .tenant-doc{display:none}.preview-overlay.tenant-mode .landlord-doc{display:none}.tenant-doc{display:none}.preview-overlay.tenant-mode .tenant-doc{display:block}.a4-page{position:relative;width:210mm;min-height:297mm;margin:0 auto 18px;padding:14mm 13mm;background:white;box-shadow:0 12px 44px rgba(0,0,0,.24);color:#172033;font:10px/1.35 Arial,sans-serif}.a4-head{display:flex;justify-content:space-between;gap:12px;border-bottom:2px solid #075c55;padding-bottom:8px;margin-bottom:9px}.a4-head h2{font-size:19px;margin:0 0 4px;color:#075c55}.a4-head p{margin:2px 0}.a4-meta{text-align:right;font-size:9px}.a4-section{margin:8px 0 3px;padding:4px 6px;background:#e9efed;color:#172033;font-weight:bold}.a4-table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:8px;line-height:1.2}.a4-table th{background:#f2f4f4;text-align:left;font-size:7px;padding:4px 3px;border:1px solid #cfd6d3}.a4-table td{padding:3px;border-bottom:1px solid #e3e7e5;vertical-align:top;overflow-wrap:anywhere}.a4-table .num{text-align:right;white-space:nowrap}.a4-table .total td{font-weight:bold;border-top:1px solid #89938f;background:#f8f9f9}.a4-summary{margin-top:9px;border-top:2px solid #075c55;padding-top:6px;display:flex;justify-content:space-between;font-size:10px;font-weight:bold}.a4-note{font-size:8px;color:#596674;margin-top:8px}.a4-footer{position:absolute;left:13mm;right:13mm;bottom:7mm;display:grid;grid-template-columns:1fr 1fr;gap:12px;padding-top:6px;border-top:1px solid #ccd5d2;font-size:8px;line-height:1.35;color:#596674}.a4-footer p{margin:0}.a4-page{padding-bottom:24mm}@media(max-width:850px){.preview-overlay{padding:10px}.a4-page{width:100%;min-height:0;padding:18px 18px 92px;overflow-x:auto}.a4-footer{left:18px;right:18px;bottom:16px;grid-template-columns:1fr 1fr;gap:8px}.preview-toolbar{padding:0 4px}}@media print{.preview-overlay{display:block!important;position:static;padding:0;background:white;overflow:visible}.preview-toolbar,.preview-modes,:host-context(body.settlement-printing) .wrap{display:none!important}.preview-overlay.landlord-mode .tenant-doc{display:none!important}.preview-overlay.tenant-mode .landlord-doc{display:none!important}.preview-overlay.tenant-mode .tenant-doc{display:block!important}.preview-overlay.landlord-mode .landlord-doc:nth-of-type(2){page-break-after:auto}.preview-overlay.tenant-mode .tenant-doc{page-break-after:auto}.a4-page{width:210mm;height:297mm;min-height:297mm;margin:0;box-shadow:none;page-break-after:always;overflow:hidden;padding:12mm}.a4-footer{left:12mm;right:12mm;bottom:7mm}.a4-page:last-child{page-break-after:auto}}\n@media(max-width:850px){.brand-inner{grid-template-columns:1fr auto}.brand-desc,.topnav a:not(.portal){display:none}.topnav{gap:8px}.hero h1{font-size:34px}.wrap{padding:0}.hero-inner{padding:22px 16px}.grid.two,.grid.equal{grid-template-columns:1fr}.summary{grid-template-columns:repeat(2,1fr)}.page{padding:16px}.keyline{grid-template-columns:1fr 1fr}.keyline.head{display:none}.footer{padding:12px 16px}}\n\n\n#unitReviewTable [aria-invalid=\"true\"]{border:2px solid #b42318;outline-offset:2px}\n#unitReviewTable .confirm-review-field{display:block;font-size:.75rem;margin-top:.25rem;padding:.2rem .35rem}\n\n.shell { border:0; border-radius:0; box-shadow:none; }\n.preview-overlay { z-index:10000; }\n@media print { .preview-overlay:not(.open) { display:none!important; } }\n\n@media screen {\n .tabs { flex-wrap:wrap; }\n}\n@container (max-width: 900px) {\n .tabs { padding-inline: 10px; }\n .page-head, .wizard-panel .step-heading { flex-direction:column; align-items:stretch; gap:10px; }\n .wizard-panel { height:auto; min-height:0; }\n #abrechnung .wizard-panel[data-panel=\"1\"], #abrechnung .wizard-panel[data-panel=\"2\"] { min-height:0; }\n #abrechnung > .page-head .actions, #abrechnung [data-panel=\"0\"] .actions, .step-heading-actions { flex-wrap:wrap; gap:8px; }\n #abrechnung > .page-head .actions > .btn, #abrechnung [data-panel=\"0\"] .actions > .btn,\n #abrechnung [data-panel=\"0\"] #heaterUpload,\n .wizard-panel .step-heading button[data-next], .wizard-panel .step-heading #showPreview {\n  flex:0 1 auto; min-width:0; width:auto; max-width:100%; white-space:normal;\n }\n}\n\n@media screen {\n :host { container-type:inline-size; }\n .object-switcher select { min-width:0; max-width:100%; }\n #abrechnung .wizard-steps { grid-template-columns:repeat(auto-fit,minmax(min(100%, 112px),1fr)); }\n #abrechnung .wizard-step { min-width:0; white-space:normal; overflow-wrap:anywhere; }\n}\n";

  function initialize(root, printSettlement) {
    root.querySelectorAll('.tab').forEach(button=>button.addEventListener('click',()=>{root.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b===button));root.querySelectorAll('.page').forEach(p=>p.classList.toggle('active',p.id===button.dataset.page));}));
    root.getElementById('addObject')?.addEventListener('click',()=>{const panel=root.getElementById('objectDetailPanel');if(panel){panel.style.display='block';panel.scrollIntoView({behavior:'smooth',block:'start'});}});
    root.getElementById('closeObjectDetail')?.addEventListener('click',()=>{root.getElementById('objectDetailPanel').style.display='none'});
    const previewOverlay=root.getElementById('printPreview');
    const tenantContent=previewOverlay?.querySelector('.tenant-content');
    let activeWizardStep=0;
    let entryMode='';
    const wizardSteps=[...root.querySelectorAll('.wizard-step')];
    const wizardPanels=[...root.querySelectorAll('.wizard-panel')];
    function setWizardStep(index){
     activeWizardStep=Math.max(0,Math.min(4,index));
     wizardSteps.forEach((button,i)=>{
      const skipped=entryMode==='manual'&&i===0;
      button.disabled=skipped;
      button.classList.toggle('skipped',skipped);
      button.classList.toggle('active',i===activeWizardStep);
      button.setAttribute('aria-selected',i===activeWizardStep?'true':'false');
     });
     wizardPanels.forEach((panel,i)=>panel.classList.toggle('active',i===activeWizardStep));
    }
    function setEntryMode(mode){
     entryMode=mode;
     const status=root.getElementById('entryModeState');
     const detailsHint=root.getElementById('detailsModeHint');
     const positionHint=root.getElementById('positionModeHint');
     if(mode==='manual'){
      if(status)status.textContent='Manuelle Erfassung: Der Upload-Schritt wird übersprungen. Objekt, Zeitraum, Einheit und Kontakt werden im nächsten Schritt ausgewählt.';
      if(detailsHint)detailsHint.textContent='Wähle Objekt, Zeitraum, Einheit und Mietkontakt. Bereits gespeicherte Stammdaten kannst du übernehmen.';
      if(positionHint)positionHint.textContent='Die Standardpositionen sind vorbereitet. Beträge und Anteile bleiben leer und werden von dir erfasst.';
      setWizardStep(1);
     }else{
      if(status)status.textContent='Belegerfassung: Der WEG-Beleg wird zuerst eingelesen. Danach bestätigst du die erkannten Angaben und prüfst die Positionen.';
      if(detailsHint)detailsHint.textContent='Nach dem Einlesen werden eindeutig erkannte Angaben vorgeschlagen. Eine unsichere Wohnungszuordnung wird zur Bestätigung angezeigt; weitere Einheiten werden nicht angelegt.';
      if(positionHint)positionHint.textContent='Erkannte Positionen und Beträge werden in die gleiche Vorlage übernommen. Nicht erkannte Zeilen kannst du ergänzen.';
      setWizardStep(0);
     }
    }
    root.getElementById('wegUploadButton')?.addEventListener('click',()=>{setEntryMode('upload');root.getElementById('wegUploadInput')?.click()});
    root.getElementById('startManual')?.addEventListener('click',()=>setEntryMode('manual'));
    root.getElementById('wegUploadInput')?.addEventListener('change',event=>{
     const files=[...event.target.files];
     const label=root.getElementById('uploadSelection');
     if(label)label.textContent=files.length?'Ausgewählt: '+files.map(file=>file.name).join(', '):'';
     if(files.length){setEntryMode('upload');setWizardStep(1);const mode=root.getElementById('detailsModeHint');if(mode)mode.textContent='Beleg ausgewählt. Nach dem Einlesen bestätigst du hier die erkannten Angaben; nicht verfügbare Werte ergänzt du.'}
    });
    root.getElementById('heaterUpload')?.addEventListener('click',()=>root.getElementById('heaterUploadInput')?.click());
    root.getElementById('heaterUploadInput')?.addEventListener('change',event=>{
     const files=[...event.target.files];const label=root.getElementById('heatingSelection');
     if(label)label.textContent=files.length?'Zusätzlicher Beleg: '+files.map(file=>file.name).join(', '):'';
    });
    wizardSteps.forEach(button=>button.addEventListener('click',()=>{if(!(entryMode==='manual'&&Number(button.dataset.step)===0))setWizardStep(Number(button.dataset.step))}));
    root.querySelectorAll('[data-next]').forEach(button=>button.addEventListener('click',()=>{
     if(!entryMode&&activeWizardStep===0)setEntryMode('upload');
     else setWizardStep(activeWizardStep+1);
    }));
    root.querySelectorAll('[data-prev]').forEach(button=>button.addEventListener('click',()=>{
     if(entryMode==='manual'&&activeWizardStep===1){entryMode='';setWizardStep(0);const status=root.getElementById('entryModeState');if(status)status.textContent='Wähle den Start: Beim Upload liest das System den Beleg ein. Bei der manuellen Erfassung überspringst du diesen Schritt.'}
     else setWizardStep(activeWizardStep-1);
    }));
    const standardSections=[
     {id:'umlagefaehig',title:'Umlagefähige Kosten',positions:['Hausmeister','Gartenpflege','Winterdienst','Gebäudereinigung','Glasreinigung','Gebäudeversicherung','Haftpflichtversicherung','Beleuchtung','Breitbandkabelgebühren','Entwässerung','Straßenreinigung','Müllgebühren','Rauchmelderservice','Wartung Rauchabzug','Ungezieferbekämpfung','Heiz- und Wasserkosten']},
     {id:'nicht_umlagefaehig',title:'Nicht umlagefähige Kosten',positions:['Laufende Erhaltung','Erhaltung allgemein','Erhaltung aus Rücklage','Rücklagenentnahme','Verwaltervergütung','Beiratsaufwandsentschädigung','Kontoführungsgebühren','Mahngebühren','Raumkosten Eigentümerversammlung','Gerichts- und Anwaltskosten','Honorare Sachverständige']},
     {id:'ruecklage',title:'Zuführung zur Erhaltungsrücklage',positions:['Zuführung zur Erhaltungsrücklage']},
     {id:'einnahmen',title:'Einnahmen / Gutschriften · falls im Beleg vorhanden',positions:['Waschgeld / sonstige Einnahmen','Zinsen / Erstattungen']}
    ];
    function makePositionRow(sectionId,label,canRemove=false){
     const tr=document.createElement('tr');tr.className='review-position-row';tr.dataset.category=sectionId;
     const removeButton=canRemove?'<button class="remove-position" type="button" aria-label="Position löschen" title="Position löschen">−</button>':'';
     tr.innerHTML='<td><input class="review-input review-position" aria-label="Position" value="'+label.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;')+'"></td><td><select class="review-input review-key" aria-label="Verteilerschlüssel"><option value="Objektvorgabe" selected>Objektvorgabe</option><option>Wohnfläche</option><option>Wohneinheit</option><option>MEA</option><option>Verbrauch</option><option>Direktzuordnung</option></select></td><td><input class="review-input review-money" aria-label="Verteilungsrelevanter Betrag" inputmode="decimal" placeholder="Betrag"></td><td><input class="review-input review-base" aria-label="Gesamtverteiler" inputmode="decimal" placeholder="Basis"></td><td><input class="review-input review-share" aria-label="Ihr Anteil" inputmode="decimal" placeholder="Anteil"></td><td><input class="review-input review-result" aria-label="Ihr Betrag" inputmode="decimal" placeholder="Betrag"></td><td class="position-action-cell">'+removeButton+'</td>';
     return tr;
    }
    function renderStandardTemplate(){
     const body=root.getElementById('positionTemplateBody');if(!body)return;body.innerHTML='';
     standardSections.forEach(section=>{
      const heading=document.createElement('tr');heading.className='group-row';heading.innerHTML='<td colspan="7">'+section.title+'</td>';body.appendChild(heading);
      section.positions.forEach(label=>body.appendChild(makePositionRow(section.id,label)));
      const subtotal=document.createElement('tr');subtotal.className='subtotal-row';subtotal.dataset.subtotal=section.id;
      subtotal.innerHTML='<td colspan="2">Zwischensumme · '+section.title+'</td><td class="subtotal-total">—</td><td></td><td></td><td class="subtotal-share">—</td><td class="position-action-cell"></td>';body.appendChild(subtotal);
      const add=document.createElement('tr');add.className='add-row';add.innerHTML='<td colspan="7"><button class="btn soft" type="button" data-add-position="'+section.id+'">＋ Position zu diesem Block hinzufügen</button></td>';body.appendChild(add);
     });
     const grand=document.createElement('tr');grand.className='subtotal-row grand-total-row';grand.innerHTML='<td colspan="2">Summe aller erfassten Positionen · Abgleich mit dem WEG-Beleg</td><td class="grand-total">—</td><td></td><td></td><td class="grand-share">—</td><td class="position-action-cell"></td>';body.appendChild(grand);
     updateSubtotals();
    }
    function parseGermanNumber(value){const normalized=String(value||'').replace(/\./g,'').replace(',','.');const number=Number(normalized);return Number.isFinite(number)?number:0}
    function germanMoney(value){return Number(value||0).toLocaleString('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2})+' €'}
    function reviewRows(){return [...root.querySelectorAll('#unitReviewTable tbody tr.review-position-row')]}
    function recalculateReviewRow(row){
     const amount=parseGermanNumber(row.querySelector('.review-money')?.value);
     const base=parseGermanNumber(row.querySelector('.review-base')?.value);
     const share=parseGermanNumber(row.querySelector('.review-share')?.value);
     const result=row.querySelector('.review-result');
     if(base>0&&amount&&share)result.value=germanMoney(amount*share/base).replace(' €','');
    }
    function updateSubtotals(){
     standardSections.forEach(section=>{
      const rows=reviewRows().filter(row=>row.dataset.category===section.id);
      const total=rows.reduce((sum,row)=>sum+parseGermanNumber(row.querySelector('.review-money')?.value),0);
      const share=rows.reduce((sum,row)=>sum+parseGermanNumber(row.querySelector('.review-result')?.value),0);
      const subtotal=root.querySelector('[data-subtotal="'+section.id+'"]');
      if(subtotal){subtotal.querySelector('.subtotal-total').textContent=total?germanMoney(total):'—';subtotal.querySelector('.subtotal-share').textContent=share?germanMoney(share):'—'}
     });
     const rows=reviewRows();
     const grandTotal=rows.reduce((sum,row)=>sum+parseGermanNumber(row.querySelector('.review-money')?.value),0);
     const grandShare=rows.reduce((sum,row)=>sum+parseGermanNumber(row.querySelector('.review-result')?.value),0);
     const grandRow=root.querySelector('.grand-total-row');
     if(grandRow){grandRow.querySelector('.grand-total').textContent=grandTotal?germanMoney(grandTotal):'—';grandRow.querySelector('.grand-share').textContent=grandShare?germanMoney(grandShare):'—'}
    }
    function syncBillingPeriodFields(){
     const year=String(root.getElementById('wizardYear')?.value||'').trim();
     const wegFrom=root.getElementById('wizardFrom');
     const wegTo=root.getElementById('wizardTo');
     const tenantFrom=root.getElementById('tenantFrom');
     const tenantTo=root.getElementById('tenantTo');
     if(!/^\d{4}$/.test(year)){
      if(wegFrom)wegFrom.value='';if(wegTo)wegTo.value='';
      if(tenantFrom&&!tenantFrom.dataset.userEdited)tenantFrom.value='';
      if(tenantTo&&!tenantTo.dataset.userEdited)tenantTo.value='';
      return;
     }
     if(wegFrom)wegFrom.value='01.01.'+year;
     if(wegTo)wegTo.value='31.12.'+year;
     if(tenantFrom&&!tenantFrom.dataset.userEdited)tenantFrom.value=year+'-01-01';
     if(tenantTo&&!tenantTo.dataset.userEdited)tenantTo.value=year+'-12-31';
    }
    root.getElementById('wizardYear')?.addEventListener('input',syncBillingPeriodFields);
    root.getElementById('wizardYear')?.addEventListener('change',syncBillingPeriodFields);
    ['tenantFrom','tenantTo'].forEach(id=>root.getElementById(id)?.addEventListener('input',event=>{event.target.dataset.userEdited='true'}));
    renderStandardTemplate();
    root.getElementById('unitReviewTable')?.addEventListener('input',event=>{
     const row=event.target.closest('.review-position-row');if(row&&!event.target.classList.contains('review-result'))recalculateReviewRow(row);updateSubtotals();
    });
    root.getElementById('unitReviewTable')?.addEventListener('change',updateSubtotals);
    root.getElementById('unitReviewTable')?.addEventListener('click',event=>{
     const removeButton=event.target.closest('.remove-position');
     if(removeButton){removeButton.closest('.review-position-row')?.remove();updateSubtotals();return}
     const button=event.target.closest('[data-add-position]');if(!button)return;
     const sectionId=button.dataset.addPosition;const rows=reviewRows().filter(row=>row.dataset.category===sectionId);
     const row=makePositionRow(sectionId,'',true);root.querySelector('[data-subtotal="'+sectionId+'"]').before(row);row.querySelector('.review-position').focus();
    });
    function syncReviewToPreview(){
     if(!tenantContent)return;
     const selectedUnit=root.getElementById('reviewUnit')?.value||'Erkannte Wohnung';
     const heading=previewOverlay?.querySelector('.tenant-doc .a4-head p');
     if(heading)heading.textContent='Mietervorschau · '+selectedUnit;
     const title=previewOverlay?.querySelector('.tenant-doc .a4-head h2');if(title)title.textContent='Betriebskostenabrechnung';
     tenantContent.innerHTML='';
     standardSections.forEach(section=>{
      const rows=reviewRows().filter(row=>row.dataset.category===section.id&&(
       row.querySelector('.review-money').value.trim()||
       row.querySelector('.review-result').value.trim()
      ));
      if(!rows.length)return;
      const label=document.createElement('div');label.className='a4-section';label.textContent=section.title;tenantContent.appendChild(label);
      const table=document.createElement('table');table.className='a4-table';
      const head=document.createElement('thead');const header=document.createElement('tr');
      ['Position','Verteilerschlüssel','Verteilungsrelevanter Betrag','Gesamtverteiler','Ihr Anteil','Ihr Betrag'].forEach(text=>{const th=document.createElement('th');th.textContent=text;header.appendChild(th)});
      head.appendChild(header);table.appendChild(head);const body=document.createElement('tbody');let total=0;
      rows.forEach(row=>{
       const values=[row.querySelector('.review-position').value,row.querySelector('.review-key').value,row.querySelector('.review-money').value,row.querySelector('.review-base').value,row.querySelector('.review-share').value,row.querySelector('.review-result').value];
       total+=parseGermanNumber(values[5]);const tr=document.createElement('tr');
       values.forEach((value,i)=>{const td=document.createElement('td');td.textContent=value+(i===2||i===5?' €':'');if(i>=2)td.className='num';tr.appendChild(td)});
       body.appendChild(tr);
      });
      const totalRow=document.createElement('tr');totalRow.className='total';const labelCell=document.createElement('td');labelCell.colSpan=5;labelCell.textContent='Zwischensumme';const amountCell=document.createElement('td');amountCell.className='num';amountCell.textContent=germanMoney(total);totalRow.append(labelCell,amountCell);body.appendChild(totalRow);
      table.appendChild(body);tenantContent.appendChild(table);
     });
     const tenantNote=previewOverlay?.querySelector('.tenant-doc .a4-note');
     if(tenantNote)tenantNote.textContent='Die Vorschau wird aus den erfassten Positionen der ausgewählten Wohnung erzeugt. Prüfe vor dem Versand den Abrechnungszeitraum, den Mietvertrag und die hinterlegten Vorauszahlungen.';
    }
    
    root.querySelectorAll('[data-preview-mode]').forEach(button=>button.addEventListener('click',()=>{const mode=button.dataset.previewMode;previewOverlay?.classList.toggle('tenant-mode',mode==='tenant');previewOverlay?.classList.toggle('landlord-mode',mode==='landlord');root.querySelectorAll('[data-preview-mode]').forEach(item=>item.classList.toggle('active',item===button))}));root.getElementById('showPreview')?.addEventListener('click',()=>{syncReviewToPreview();previewOverlay?.classList.remove('landlord-mode');previewOverlay?.classList.add('tenant-mode');root.querySelectorAll('[data-preview-mode]').forEach(item=>item.classList.toggle('active',item.dataset.previewMode==='tenant'));previewOverlay?.classList.add('open')});root.getElementById('closePreview')?.addEventListener('click',()=>previewOverlay?.classList.remove('open'));root.getElementById('printPreviewButton')?.addEventListener('click',printSettlement);previewOverlay?.addEventListener('click',event=>{if(event.target===previewOverlay)previewOverlay.classList.remove('open')});root.addEventListener('keydown',event=>{if(event.key==='Escape')previewOverlay?.classList.remove('open')});
    
    
    
    const byId = id => root.getElementById(id);
    
    function flagReviewField(input) {
     if (input.nextElementSibling?.classList.contains('confirm-review-field')) return;
     input.setAttribute('aria-invalid', 'true');
     const label = input.getAttribute('aria-label');
     const button = action('Geprüft', () => {
      if (!input.value.trim() || (input.classList.contains('review-key') && input.value === 'Objektvorgabe')) {
       input.focus();
       return;
      }
      input.removeAttribute('aria-invalid');
      input.focus();
      button.remove();
     });
     button.classList.add('confirm-review-field');
     button.setAttribute('aria-label', label + ' mit dem Original abgeglichen');
     button.title = 'Nach dem Abgleich mit dem Original bestätigen';
     input.after(button);
    }
    
    const positionFields = ['position','key','money','base','share','result'];
    const valuesOf = row => positionFields.map(field => row.querySelector('.review-' + field).value);
    const insertPosition = (category, name) => {
     const row = makePositionRow(category, name, true);
     root.querySelector('[data-subtotal="' + category + '"]').before(row);
     return row;
    };
    function normalizedLabel(value) {
     return value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, '');
    }
    function extractRows(text) {
     let category = '';
     const rows = [];
     for (const line of text.split(/\r?\n/)) {
      const heading = normalizedLabel(line).replace(/^\d+/, '');
      if (/^nichtumlag/.test(heading)) { category = 'nicht_umlagefaehig'; continue; }
      if (/^(?:ublicherweise)?umlag/.test(heading)) { category = 'umlagefaehig'; continue; }
      if (/^(?:zufuhrungzurerhaltungsrucklage|beitragezurrucklage)$/.test(heading)) { category = 'ruecklage'; continue; }
      if (/^(?:einnahmen|gutschriften)$/.test(heading)) { category = 'einnahmen'; continue; }
      if (/^(?:zwischensumme|summe|abrechnungssumme|saldo|gesamtbetrag|vortrag|kostenumlag|kostennichtumlag)/.test(heading)) {
       category = '';
       continue;
      }
      const cells = line.split(/€|\bEUR\b/i);
      if (cells.length < 2) continue;
      const amount = /(?:^|\s)([-−]?(?:\d{1,3}(?:\.\d{3})+|\d+),\d{2})\s*$/;
      const first = cells[0].match(amount);
      const last = cells.length >= 3 ? cells.at(-2).match(amount) : null;
      const name = cells[0].slice(0, first?.index ?? cells[0].length)
       .replace(/^\s*\d{4,}[\s_]+0[\s_.]+/, '')
       .replace(/\s+(?:m[²2^]+\s+)?Wohnfläche\s+ges\.?\s*$/i,'').trim();
      if (!first || !/[a-zäöü]{3}/i.test(name)) continue;
      const candidates = standardSections.filter(section => section.positions.some(label => normalizedLabel(label) === normalizedLabel(name)));
      const block = category || (candidates.length === 1 ? candidates[0].id : '');
      const context = normalizedLabel(cells[0] + ' ' + (cells[1] || ''));
      const key = /wohnfl/.test(context) ? 'Wohnfläche' : /\bMEA\b/i.test(line) ? 'MEA' : /\b(?:Wohn)?Einheit(?:en)?\b/i.test(line) ? 'Wohneinheit' : '';
      const distribution = (cells[1] || '').slice(0,last?.index ?? 0);
      const quantities = distribution.match(/(?:\d{1,3}(?:\.\d{3})+|\d+),\d{4}(?!\d)/g)
       || distribution.match(/(?:\d{1,3}(?:\.\d{3})+|\d+),\d{2}(?!\d)/g) || [];
      rows.push({name, block, key, base: quantities[0] || '', part: quantities[1] || '',
       total: first[1].replace('−','-'), share: last ? last[1].replace('−','-') : ''});
     }
     return rows;
    }
    let ocrRunning = false;
    const importStatus = byId('uploadSelection');
    const ocrText = document.createElement('details');
    ocrText.innerHTML = '<summary>Erkannten Belegtext ansehen</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere"></pre>';
    ocrText.hidden = true;
    importStatus.after(ocrText);
    let engineScript;
    function loadEngine() {
     if (!engineScript) engineScript = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/tesseract.js@7.0.0/dist/tesseract.min.js';
      script.onload = () => resolve(window.Tesseract);
      script.onerror = () => { engineScript = null; script.remove(); reject(new Error('OCR konnte nicht geladen werden.')); };
      document.head.append(script);
     });
     return engineScript;
    }
    byId('wegUploadInput').addEventListener('change', async event => {
     event.stopImmediatePropagation();
     const files = Array.from(event.target.files);
     event.target.value = '';
     if (ocrRunning || !files.length) return;
     ocrRunning = true;
     byId('wegUploadButton').disabled = true;
     importStatus.setAttribute('role','status');
     importStatus.textContent = 'Belege werden gelesen …';
     let worker, pdfjs;
     const pages = [];
     try {
      const recognize = async image => {
       if (!worker) {
        const engine = await loadEngine();
        worker = await engine.createWorker('deu');
       }
       return (await worker.recognize(image)).data.text;
      };
      const endpoint = window.nicWegImportEndpoint;
      const proposals = [];
      for (const file of files) {
       if (endpoint) {
        const url = new URL(endpoint, window.location.href);
        if (url.origin !== window.location.origin) throw new Error('Der OCR-Dienst muss zur selben Website gehören.');
        const pdf = file.type === 'application/pdf' || /\.pdf$/i.test(file.name);
        importStatus.textContent = 'Beleg wird auf dem eigenen Erkennungsdienst verarbeitet …';
        const response = await fetch(url, {method:'POST', headers:{'Content-Type':'application/octet-stream','X-Weg-Type':pdf?'pdf':'image'}, body:file});
        if (!response.ok) throw new Error('Erkennungsdienst: HTTP ' + response.status);
        for (const page of await response.json()) {
         pages.push(Array.isArray(page.text) ? page.text.join('\n') : page.text);
         if (page.qwenProposal) proposals.push(page.qwenProposal);
         if (page.secondReadError) proposals.push({Hinweis:'Qwen konnte den Beleg nicht erneut lesen.'});
        }
        continue;
       }
       if (file.type === 'application/pdf' || /\.pdf$/i.test(file.name)) {
        if (!pdfjs) {
         const path = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/';
         pdfjs = await import(path + 'pdf.mjs');
         pdfjs.GlobalWorkerOptions.workerSrc = path + 'pdf.worker.mjs';
        }
        const pdf = await pdfjs.getDocument({data: await file.arrayBuffer(), isEvalSupported:false}).promise;
        try {
         for (let i = 1; i <= pdf.numPages; i++) {
          importStatus.textContent = 'PDF-Seite ' + i + ' von ' + pdf.numPages + ' wird gelesen …';
          const page = await pdf.getPage(i);
          const viewport = page.getViewport({scale: 2.6});
          const canvas = document.createElement('canvas');
          canvas.width = Math.ceil(viewport.width);
          canvas.height = Math.ceil(viewport.height);
          await page.render({canvasContext: canvas.getContext('2d'), viewport}).promise;
          pages.push(await recognize(canvas));
         }
        } finally { await pdf.destroy(); }
       } else {
        importStatus.textContent = 'Bild ' + (pages.length + 1) + ' wird gelesen …';
        pages.push(await recognize(file));
       }
      }
      const recognized = pages.join('\n\n');
      ocrText.querySelector('pre').textContent = recognized + (proposals.length ? '\n\nQwen · Vorschläge zur Prüfung\n' + JSON.stringify(proposals, null, 2) : '');
      ocrText.hidden = false;
      const extracted = extractRows(recognized);
      const units = Array.from(new Set([...recognized.matchAll(/(?:Wohnungsnummer|Einheit)\s*:\s*([^\n]+)/gi)].map(match => match[1].trim())));
      if (units.length > 1) {
       importStatus.textContent = 'Mehrere unterschiedliche Wohnungsangaben erkannt. Bitte nur die Seiten einer Wohnung gemeinsam einlesen.';
       return;
      }
      if (units.length === 1 && !byId('reviewUnit').value) byId('reviewUnit').value = units[0];
      const year = recognized.match(/01\.01\.(20\d{2})\s*[-–]\s*31\.12\.\1/);
      if (year && !byId('wizardYear').value) { byId('wizardYear').value = year[1]; syncBillingPeriodFields(); }
      let imported = 0;
      for (const item of extracted) {
       if (!item.block) continue;
       const existing = reviewRows().find(row => row.dataset.category === item.block &&
        normalizedLabel(valuesOf(row)[0]) === normalizedLabel(item.name) && !valuesOf(row)[2] && !valuesOf(row)[5]);
       const row = existing || insertPosition(item.block, item.name);
       if (item.key) row.querySelector('.review-key').value = item.key;
       row.querySelector('.review-base').value = item.base;
       row.querySelector('.review-share').value = item.part;
       row.querySelector('.review-money').value = item.total;
       row.querySelector('.review-result').value = item.share;
       for (const [field, value] of [['key',item.key],['base',item.base],['share',item.part],['result',item.share]]) {
        if (!value) flagReviewField(row.querySelector('.review-' + field));
       }
       imported++;
      }
      updateSubtotals();
      importStatus.textContent = imported + ' Positionen übernommen. Vergleiche Beträge und Zuordnung mit dem Beleg. ' +
       (extracted.length - imported ? (extracted.length - imported) + ' Zeilen ohne eindeutigen Kostenblock stehen im erkannten Belegtext.' : '');
      if (imported) { readBalanceReferences(recognized); setWizardStep(2); }
     } catch (error) {
      importStatus.textContent = 'Beleg konnte nicht gelesen werden: ' + error.message;
     } finally {
      try { await worker?.terminate(); }
      finally { ocrRunning = false; byId('wegUploadButton').disabled = false; }
     }
    }, true);
    
    byId('addReviewPosition').addEventListener('click', () => {
     const select = root.querySelector('[data-add-position="umlagefaehig"]');
     select.click();
    });
    
    const contactCard = root.querySelector('#kontakte .grid article:last-child');
    const contactFields = Array.from(contactCard.querySelectorAll('input,select'));
    let contacts = [];
    function updateContacts() {
     for (const [id, role] of [['tenantContact','Mieter/in'],['objectLandlord','Vermieter/in'],['objectManager','Verwalter/in']]) {
      const select = byId(id);
      const previous = select.value;
      select.replaceChildren(new Option('Kontakt auswählen',''));
      contacts.forEach((contact, index) => {
       if (contact[0] === role) select.add(new Option([contact[1],contact[2]].filter(Boolean).join(' '),String(index)));
      });
      select.value = previous;
     }
    }
    function action(label, handler) {
     const button = document.createElement('button');
     button.type = 'button';
     button.className = 'btn';
     button.textContent = label;
     button.addEventListener('click', handler);
     return button;
    }
    const contactList = root.querySelector('#kontakte .grid article:first-child');
    contactCard.append(action('Kontakt übernehmen', () => {
     const contact = contactFields.map(field => field.value.trim());
     if (!contact[0] || !(contact[1] || contact[2])) { contactFields[0].focus(); return; }
     contacts.push(contact);
     contactFields.forEach(field => field.value = '');
     updateContacts();
     renderContacts();
    }));
    function renderContacts() {
     contactList.replaceChildren();
     if (!contacts.length) contactList.textContent = 'Noch keine Kontakte vorhanden';
     for (const [role, first, last] of contacts) {
      const line = document.createElement('p');
      line.textContent = [first,last,role].filter(Boolean).join(' · ');
      contactList.append(line);
     }
    }
    const notes = document.createElement('div');
    notes.setAttribute('role','status');
    
    const amountPattern = /^[-−]?(?:\d{1,3}(?:\.\d{3})+|\d+),\d{2}$/;
    function cents(value) {
     const cleaned = value.trim().replace(/\s*€$/, '');
     return amountPattern.test(cleaned) ? Number(cleaned.replace(/\./g, '').replace(',', '').replace('−','-')) : null;
    }
    const balanceBlocks = [...standardSections, {id:'all',title:'Endsumme WEG'}];
    const balancePanel = document.createElement('details');
    balancePanel.innerHTML = '<summary>Zwischen- und Endsummen mit dem Beleg abgleichen</summary>';
    const balanceFields = {};
    for (const {id,title} of balanceBlocks) {
     const group = document.createElement('fieldset');
     group.className = 'form-grid';
     const legend = document.createElement('legend');
     legend.textContent = title;
     group.append(legend);
     balanceFields[id] = ['Gesamtbetrag laut Beleg','Wohnungsbetrag laut Beleg'].map(label => {
      const field = document.createElement('label');
      field.textContent = label + ' ';
      const input = document.createElement('input');
      input.inputMode = 'decimal';
      input.placeholder = '0,00';
      const status = document.createElement('small');
      status.setAttribute('aria-live','polite');
      field.append(input, status);
      group.append(field);
      input.addEventListener('input', updateBalance);
      return {input,status};
     });
     balancePanel.append(group);
    }
    byId('unitReviewTable').closest('.position-table-wrap').after(balancePanel);
    function updateBalance() {
     for (const {id} of balanceBlocks) {
      const rows = reviewRows().filter(row => (id === 'all' || row.dataset.category === id) &&
       (valuesOf(row)[2].trim() || valuesOf(row)[5].trim()));
      balanceFields[id].forEach(({input,status}, index) => {
       const expected = cents(input.value);
       if (expected === null) {
        status.textContent = input.value.trim() ? ' Betrag mit zwei Nachkommastellen eingeben.' : '';
        return;
       }
       const amounts = rows.map(row => cents(valuesOf(row)[index ? 5 : 2]));
       if (!amounts.length || amounts.includes(null)) {
        status.textContent = ' Abgleich offen · Beträge fehlen oder sind ungültig.';
        return;
       }
       const sum = amounts.reduce((total, value) => total + value, 0);
       const difference = sum - expected;
       status.textContent = difference === 0 ? ' Summe stimmt · ' + germanMoney(sum / 100) :
        ' Erfasst: ' + germanMoney(sum / 100) + ' · Differenz zum Beleg: ' + germanMoney(difference / 100);
      });
     }
    }
    function readBalanceReferences(text) {
     const map = [
      [/^(?:summe )?kosten nicht umlag|^summe nicht umlag/i,'nicht_umlagefaehig'],
      [/^(?:summe )?kosten umlag|^summe umlag/i,'umlagefaehig'],
      [/^summe (?:erhaltungsrücklage|zuführung)|^beiträge zur rücklage/i,'ruecklage'],
      [/^summe einnahmen/i,'einnahmen'],
      [/^abrechnungssumme\b/i,'all']
     ];
     for (const line of text.split(/\r?\n/)) {
      const match = map.find(([pattern]) => pattern.test(line.trim()));
      if (!match) continue;
      const values = [...line.matchAll(/(?<![\d.,])([-−]?(?:\d{1,3}(?:\.\d{3})+|\d+),\d{2})\s*€/g)];
      if (values.length !== 2) continue;
      balanceFields[match[1]].forEach(({input},i) => { if (!input.value) input.value = values[i][1]; });
      balancePanel.open = true;
     }
     updateBalance();
    }
    
    const draftFields = [...root.querySelectorAll('#abrechnung input[id]:not([type=file]), #abrechnung select[id], #objectLandlord, #objectManager')];
    const storageKey = 'nic-settlement-draft-v1';
    byId('showReceipts').after(action('Entwurf lokal speichern', () => {
     try {
      localStorage.setItem(storageKey, JSON.stringify({
       fields: Object.fromEntries(draftFields.map(field => [field.id, field.value])),
       references: Object.fromEntries(Object.entries(balanceFields).map(([key, fields]) => [key, fields.map(field => field.input.value)])),
       contacts, rows: reviewRows().map(row => [row.dataset.category, valuesOf(row), positionFields.filter(field => row.querySelector(".review-" + field).getAttribute("aria-invalid") === "true")])
      }));
      notes.textContent = 'Entwurf in diesem Browser gespeichert.';
     } catch { notes.textContent = 'Der Browser konnte den Entwurf nicht speichern.'; }
    }), notes);
    try {
     const saved = JSON.parse(localStorage.getItem(storageKey));
     if (saved) {
      contacts = saved.contacts;
      for (const [key, fields] of Object.entries(balanceFields)) fields.forEach(({input}, index) => { input.value = saved.references?.[key]?.[index] || ''; });
      updateContacts();
      renderContacts();
      for (const field of draftFields) field.value = saved.fields[field.id] ?? '';
      byId('positionTemplateBody').querySelectorAll('.review-position-row').forEach(row => row.remove());
      for (const [block, values, flagged = []] of saved.rows) {
       const row = insertPosition(block, '');
       positionFields.forEach((name, i) => row.querySelector('.review-' + name).value = values[i]);
       for (const field of flagged) if (positionFields.includes(field)) flagReviewField(row.querySelector('.review-' + field));
      }
      updateSubtotals();
     }
    } catch { notes.textContent = 'Der gespeicherte Entwurf konnte nicht geladen werden.'; }
    
    updateBalance();
    byId('unitReviewTable').addEventListener('input', updateBalance);
    byId('unitReviewTable').addEventListener('click', updateBalance);
    const previewModes = previewOverlay.querySelector('.preview-modes');
    let landlordMode = false;
    function fillPreview() {
     syncReviewToPreview();
     const groups = [...tenantContent.querySelectorAll('.a4-section')];
     const validSections = standardSections.filter(section => reviewRows().some(row =>
      row.dataset.category === section.id && (valuesOf(row)[2].trim() || valuesOf(row)[5].trim())));
     groups.forEach((group,i) => {
      const block = validSections[i];
      if (!landlordMode && block?.id !== 'umlagefaehig') { group.nextElementSibling?.remove(); group.remove(); }
     });
     const name = id => {
      const index = byId(id).value;
      return index === '' ? [] : contacts[Number(index)] || [];
     };
     const owner = name('objectLandlord'), tenant = name('tenantContact');
     const header = previewOverlay.querySelector('.a4-head');
     header.querySelector('p').textContent = (landlordMode ? 'Vermietervorschau' : 'Mietervorschau') + ' · ' +
      [byId('reviewUnit').value, tenant.slice(1,3).filter(Boolean).join(' ')].filter(Boolean).join(' · ');
     header.querySelectorAll('p')[1].textContent = ['objectName','objectStreet','objectPostal','objectCity'].map(id => byId(id).value).filter(Boolean).join(' · ');
     header.querySelector('.a4-meta').textContent = [byId('wizardFrom').value,byId('wizardTo').value].filter(Boolean).join(' – ');
     const footer = previewOverlay.querySelector('.a4-footer');
     footer.children[0].textContent = ['Vermieter/in',...owner.slice(1,8)].filter(Boolean).join(' · ');
     footer.children[1].textContent = owner.slice(8).some(Boolean) ? ['Bankverbindung',...owner.slice(8)].filter(Boolean).join(' · ') : '';
    }
    previewModes.append(action('Vermietervorschau', () => { landlordMode = true; fillPreview(); }));
    previewModes.firstElementChild.addEventListener('click', () => { landlordMode = false; fillPreview(); });
    byId('showPreview').addEventListener('click', () => { landlordMode = false; fillPreview(); });
    root.querySelector('[data-page="abrechnung"]').click();
    setWizardStep(0);

    const close = root.getElementById('closePreview');
    const open = root.getElementById('showPreview');
    const observer = new MutationObserver(() => {
      const showing = previewOverlay.classList.contains('open');
      const isActive = root.activeElement && previewOverlay.contains(root.activeElement);
      if (showing && !isActive) close.focus();
      if (!showing) open.focus();
    });
    observer.observe(previewOverlay, {attributes: true, attributeFilter: ['class']});
    root.addEventListener('keydown', event => {
      if (event.key !== 'Tab' || !previewOverlay.classList.contains('open')) return;
      const controls = [...previewOverlay.querySelectorAll('button:not(:disabled)')];
      if (!controls.length) return;
      if (event.shiftKey && root.activeElement === controls[0]) {
        event.preventDefault();
        controls.at(-1).focus();
      } else if (!event.shiftKey && root.activeElement === controls.at(-1)) {
        event.preventDefault();
        controls[0].focus();
      }
    });
  }

  let savedWorkspace;
  function placeWorkspace(host, workspace) {
    const settings = window.NICSettings;
    const defaults = settings?.contentPageDefaults?.settlement;
    const content = settings?.current?.content?.settlement;
    const hasCustomContent = defaults && content && ['boxTitle', 'description'].some(key => content[key] !== defaults[key]);
    if (hasCustomContent) host.prepend(workspace);
    else host.replaceChildren(workspace);
  }
  function mount() {
    if (!/\/nebenkostenabrechnung\/?$/.test(location.pathname)) return;
    if (window.NICCalculators && window.NICCalculators.active !== 'settlement') return;
    const host = document.getElementById('nicContentView');
    if (!host) return;
    if (host.querySelector('[data-settlement]')) return;
    if (savedWorkspace) {
      placeWorkspace(host, savedWorkspace);
      return;
    }
    const workspace = document.createElement('section');
    workspace.dataset.settlement = '';
    workspace.setAttribute('aria-label', 'Nebenkostenabrechnung');
    const root = workspace.attachShadow({mode: 'open'});
    const style = document.createElement('style');
    style.textContent = styles;
    root.innerHTML = markup;
    root.prepend(style);

    if (!document.getElementById('settlement-print-style')) {
      const printStyle = document.createElement('style');
      printStyle.id = 'settlement-print-style';
      printStyle.textContent = `
        @media print {
          @page { size: A4 portrait; margin: 0; }
          body.settlement-printing::before { display:none!important; content:none!important; }
          body.settlement-printing :is(body, body *):has([data-settlement]) > :not([data-settlement]):not(:has([data-settlement])),
          body.settlement-printing > :not([data-settlement]):not(:has([data-settlement])) { display:none!important; }
          body.settlement-printing :has([data-settlement]), body.settlement-printing [data-settlement] {
            margin:0!important; padding:0!important; width:auto!important; max-width:none!important;
            min-height:0!important; overflow:visible!important; border:0!important; box-shadow:none!important;
            visibility:visible!important;
          }
        }
      `;
      document.head.append(printStyle);
    }
    initialize(root, () => {
      document.body.classList.add('settlement-printing');
      window.addEventListener('afterprint', () => document.body.classList.remove('settlement-printing'), {once:true});
      window.print();
    });
    savedWorkspace = workspace;
    placeWorkspace(host, workspace);
  }
  function boot() {
    mount();
    window.addEventListener('nic-route-changed', mount);
    new MutationObserver(mount).observe(document.body, {childList: true, subtree: true});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, {once: true});
  else boot();
})();
