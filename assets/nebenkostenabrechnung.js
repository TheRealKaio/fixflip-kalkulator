(() => {
  'use strict';
  const markup = "<main class=\"wrap\"><div class=\"shell\"><nav class=\"tabs\" aria-label=\"Bereiche\"><button type=\"button\" class=\"tab\" data-page=\"kontakte\">1. Kontakte</button><button type=\"button\" class=\"tab\" data-page=\"objekte\">2. Objekte</button><button type=\"button\" class=\"tab\" data-page=\"einheiten\">3. Einheiten</button><button type=\"button\" class=\"tab\" data-page=\"schluessel\">4. Verteilerschlüssel</button><button type=\"button\" class=\"tab\" data-page=\"einstellungen\">5. Einstellungen</button><button type=\"button\" class=\"tab active\" data-page=\"abrechnung\">6. Mieterabrechnung</button></nav>\n<section class=\"page\" id=\"objekte\"><div class=\"page-head\"><div><h2>Objekte</h2><div class=\"subtle\">Objekte werden bei Bedarf aus einer WEG-Abrechnung erkannt oder manuell erfasst.</div></div><div class=\"actions\"><button class=\"btn settlement-highlight\" id=\"addObject\">＋ Objekt hinzufügen</button></div></div><article class=\"card\"><h3>Noch keine Objekte vorhanden</h3><p class=\"muted\">Beim Belegeinlesen wird nur das erkannte Objekt übernommen. Die Adresse kannst du vor dem Speichern korrigieren.</p></article><article class=\"card object-detail\" id=\"objectDetailPanel\" style=\"display:none;margin-top:18px\"><div class=\"split\"><div><h3 id=\"objectDetailTitle\">Objekt erfassen</h3><div class=\"muted\">Objektadresse und Verantwortliche</div></div><button class=\"btn\" id=\"closeObjectDetail\">Schließen</button></div><div class=\"form-grid\"><div class=\"field full\"><label for=\"propertyName\">Objektbezeichnung · WEG + Straße</label><input id=\"propertyName\" placeholder=\"Zum Beispiel WEG + Straßenname\"></div><div class=\"field full\"><label for=\"propertyStreet\">Straße und Hausnummer</label><input id=\"propertyStreet\" placeholder=\"Wird aus dem WEG-Beleg übernommen\"></div><div class=\"field\"><label for=\"propertyPostal\">Postleitzahl</label><input id=\"propertyPostal\" placeholder=\"z. B. 20095\"></div><div class=\"field\"><label for=\"propertyCity\">Ort</label><input id=\"propertyCity\" placeholder=\"z. B. Hamburg\"></div><div class=\"field\"><label for=\"propertyArea\">Objektfläche (m²)</label><div class=\"input-with-unit\" data-unit=\"m²\"><input id=\"propertyArea\" type=\"number\" inputmode=\"decimal\" min=\"0\" step=\"0.01\"></div></div><div class=\"field\"><label for=\"propertyUnits\">Anzahl Wohneinheiten</label><input id=\"propertyUnits\" type=\"number\" inputmode=\"numeric\" min=\"1\" step=\"1\" placeholder=\"z. B. 6\"></div><div class=\"field\"><label for=\"propertyOwnershipShare\">Eigentumsanteil</label><div class=\"input-with-unit\" data-unit=\"MEA\"><input id=\"propertyOwnershipShare\" type=\"text\"></div></div><div class=\"field object-contact-first\"><label for=\"objectLandlord\">Vermieter/in</label><select id=\"objectLandlord\"><option value=\"\">Kontakt auswählen</option></select></div><div class=\"field\"><label for=\"objectManager\">Hausverwaltung</label><select id=\"objectManager\"><option value=\"\">Kontakt auswählen</option></select></div></div><div class=\"foot-actions\"><span id=\"propertySaveStatus\" role=\"status\"></span><button class=\"btn settlement-highlight\" type=\"button\" id=\"saveProperty\">Objekt speichern</button></div></article></section>\n<section class=\"page\" id=\"einheiten\"><div class=\"page-head\"><div><h2>Einheiten</h2><div class=\"subtle\">Wohnungen werden aus vorhandenen Objektdaten übernommen oder einzeln erfasst.</div></div><div class=\"actions object-header-actions\"><div class=\"object-switcher\"><select id=\"unitObjectSelect\" aria-label=\"Objekt wählen\"><option value=\"\">Objekt wählen</option></select></div><button class=\"btn settlement-highlight\" type=\"button\" id=\"addUnit\">＋ Einheit hinzufügen</button></div></div><div class=\"summary\"><div class=\"metric\"><span>Wohneinheiten</span><strong id=\"unitCount\">0</strong></div><div class=\"metric\"><span>Aktuell vermietet</span><strong id=\"rentedCount\">0</strong></div><div class=\"metric\"><span>Leerstand im Jahr</span><strong id=\"vacantCount\">0</strong></div><div class=\"metric\"><span>Abrechnungszeitraum</span><strong></strong></div></div><div class=\"grid two\"><article class=\"card\"><h3>Einheitenübersicht</h3><table class=\"table\"><thead><tr><th>Wohnungsnummer / Einheit</th><th>Etage / Lage</th><th>Fläche</th><th>MEA</th><th>Mieter/in</th></tr></thead><tbody id=\"unitRows\"><tr><td colspan=\"5\" class=\"muted\">Noch keine Einheiten erfasst. Beim Einlesen wird nur die eindeutig erkannte Wohnung ergänzt.</td></tr></tbody></table></article><article class=\"card\"><h3>Einheit erfassen</h3><div class=\"form-grid\"><div class=\"field full\"><label for=\"unitName\">Bezeichnung der Wohnungseinheit</label><input id=\"unitName\" placeholder=\"Wohnungsnummer, Einheit oder Vertragsnummer\"></div><div class=\"field full\"><label for=\"unitFloor\">Etage / Lagezusatz · optional</label><input id=\"unitFloor\" placeholder=\"Nur eintragen, wenn bekannt\"></div><div class=\"field full\"><label for=\"unitArea\">Wohnfläche</label><div class=\"input-with-unit\" data-unit=\"m²\"><input id=\"unitArea\" inputmode=\"decimal\"></div></div><div class=\"field full\"><label for=\"unitShare\">Eigentumsanteil</label><div class=\"input-with-unit\" data-unit=\"MEA\"><input id=\"unitShare\"></div></div><div class=\"field full\"><label for=\"unitTenant\">Mieter/in</label><select id=\"unitTenant\"><option value=\"\">Kontakt auswählen</option></select></div></div><p class=\"mini\">Die Bezeichnung der Wohnungseinheit bleibt editierbar. Nicht erkannte Angaben und weitere Wohnungen werden nicht ergänzt.</p><div class=\"foot-actions\"><button class=\"btn settlement-highlight\" type=\"button\" id=\"saveUnit\">Einheit übernehmen</button></div><p id=\"unitSaveStatus\" role=\"status\" hidden></p></article></div></section>\n<section class=\"page\" id=\"kontakte\"><div class=\"page-head\"><div><h2>Kontakte</h2><div class=\"subtle\">Zentrale Kontaktverwaltung für Vermieter, Verwalter und Mieter</div></div><div class=\"actions\"><button class=\"btn settlement-highlight\" type=\"button\" id=\"addContact\">＋ Kontakt hinzufügen</button></div></div><div class=\"grid two\"><article class=\"card\"><h3>Noch keine Kontakte vorhanden</h3><p class=\"muted\">Kontakte werden einmal zentral angelegt und anschließend einem Objekt oder einer Wohnung zugeordnet.</p></article><article class=\"card\"><h3>Kontakt erfassen</h3><div class=\"form-grid\"><div class=\"field full\"><label>Kontaktrolle</label><select><option value=\"\">Rolle auswählen</option><option>Vermieter/in</option><option>Verwalter/in</option><option>Mieter/in</option></select></div><div class=\"field full\"><label>Vorname</label><input></div><div class=\"field full\"><label>Nachname / Firmenname</label><input></div><div class=\"field full\"><label>Telefon</label><input></div><div class=\"field full\"><label>E-Mail</label><input></div></div><details class=\"billing-group contact-detail-group\"><summary>Anschrift</summary><div class=\"form-grid\"><div class=\"field full\"><label>Straße und Hausnummer</label><input></div><div class=\"field full\"><label>Postleitzahl</label><input inputmode=\"numeric\"></div><div class=\"field full\"><label>Ort</label><input></div></div></details><details class=\"billing-group contact-detail-group\"><summary>Bankverbindung · optional</summary><div class=\"form-grid\"><div class=\"field full\"><label>Kontoinhaber/in</label><input></div><div class=\"field full\"><label>Kreditinstitut</label><input></div><div class=\"field full\"><label>IBAN</label><input autocomplete=\"off\"></div><div class=\"field full\"><label>BIC</label><input autocomplete=\"off\"></div></div></details></article></div></section>\n<section class=\"page\" id=\"schluessel\"><div class=\"page-head\"><div><h2>Verteilerschlüssel</h2><div class=\"subtle\">Je Objekt werden nur die benötigten Schlüssel aus dem globalen Katalog ausgewählt.</div></div><div class=\"actions object-header-actions\"><div class=\"object-switcher\"><select id=\"keyObjectSelect\" aria-label=\"Objekt wählen\"><option value=\"\">Objekt wählen</option></select></div></div></div><article class=\"card\"><h3>Noch keine objektbezogenen Zuordnungen</h3><p class=\"muted\">Nach Auswahl eines Objekts ordnest du den vorhandenen globalen Schlüsseln die benötigten Kostenpositionen zu. Die Wohnung liefert ihren jeweiligen Anteil.</p><button class=\"btn\">Globalen Katalog unter Einstellungen öffnen</button></article></section>\n<section class=\"page\" id=\"einstellungen\"><div class=\"page-head\"><div><h2>Einstellungen</h2><div class=\"subtle\">Globale Grundlagen für die Abrechnung verwalten</div></div></div><div class=\"grid two\"><article class=\"card\"><div class=\"split\"><div><h3>Globaler Verteilerschlüssel</h3><div class=\"muted\">Ein zentraler Katalog, aus dem jedes Objekt die benötigten Schlüssel auswählt.</div></div><button class=\"btn primary\">＋ Verteilerschlüssel hinzufügen</button></div><div class=\"callout\" style=\"margin:14px 0\">Ein hier neu angelegter Schlüssel steht anschließend allen Objekten zur Auswahl. Er wird einem Objekt erst zugeordnet, wenn du ihn dort tatsächlich benötigst.</div><table class=\"table\"><thead><tr><th>Verteilerschlüssel</th><th>Bezugsgröße</th><th>Einheit</th><th>Status</th></tr></thead><tbody><tr><td><span class=\"name\">Wohnfläche</span></td><td>Fläche der Einheit</td><td>m²</td><td><span class=\"badge\">Global</span></td></tr><tr><td><span class=\"name\">Wohneinheit</span></td><td>gleicher Anteil je Einheit</td><td>Einheit</td><td><span class=\"badge\">Global</span></td></tr><tr><td><span class=\"name\">Eigentumsanteil (MEA)</span></td><td>Miteigentumsanteile</td><td>MEA</td><td><span class=\"badge\">Global</span></td></tr><tr><td><span class=\"name\">Verbrauch</span></td><td>Messwerte der Einheit</td><td>Messgröße</td><td><span class=\"badge\">Global</span></td></tr><tr><td><span class=\"name\">Direktzuordnung</span></td><td>vollständig einer Einheit zuordnen</td><td>Euro</td><td><span class=\"badge\">Global</span></td></tr></tbody></table><p class=\"mini\">Eigene Schlüssel legst du einmal hier an. Die Zuordnung zu Kostenarten und Objekten bleibt separat.</p></article><article class=\"card\"><h3>So greifen die Ebenen ineinander</h3><div class=\"section-title\"><span class=\"icon\">1</span>Globaler Katalog</div><p class=\"muted\">Verfügbare Rechenarten wie Wohnfläche, MEA oder Verbrauch.</p><div class=\"section-title\"><span class=\"icon\">2</span>Objekt</div><p class=\"muted\">Für jede Kostenposition wird der passende Schlüssel aus dem Katalog ausgewählt.</p><div class=\"section-title\"><span class=\"icon\">3</span>Einheit</div><p class=\"muted\">Die jeweilige Wohnung liefert ihren Anteil, zum Beispiel 43,14 m² oder den erfassten Verbrauch.</p><div class=\"callout\">Ein Schlüssel wird zentral gepflegt, aber nicht automatisch auf jedes Objekt angewendet. So kannst du ihn nur dort einsetzen, wo er gebraucht wird.</div></article></div></section>\n<section class=\"page active\" id=\"abrechnung\"><div class=\"page-head\"><div><h2>Mieterabrechnung</h2><div class=\"subtle\">Abrechnung aus einem WEG-Beleg einlesen oder manuell erfassen</div></div><div class=\"actions\"><button class=\"btn\" id=\"showReceipts\">Abrechnungen anzeigen</button></div></div>\n<div id=\"entryModeState\" class=\"callout\" style=\"margin-bottom:16px\">Wähle den Start: Beim Upload liest das System den Beleg ein. Bei der manuellen Erfassung überspringst du diesen Schritt.</div><div id=\"uploadSelection\" class=\"mini\" aria-live=\"polite\" style=\"margin:-8px 0 16px\"></div>\n<div class=\"wizard-steps\" role=\"tablist\" aria-label=\"Abrechnungsschritte\"><button class=\"wizard-step active\" type=\"button\" data-step=\"0\"><b>1 · Beleg</b><span>Hochladen und erkennen</span></button><button class=\"wizard-step\" type=\"button\" data-step=\"1\"><b>2 · Angaben</b><span>Objekt, Einheit, Kontakt</span></button><button class=\"wizard-step\" type=\"button\" data-step=\"2\"><b>3 · Positionen</b><span>Zuordnen und erfassen</span></button><button class=\"wizard-step\" type=\"button\" data-step=\"3\"><b>4 · Verteilung</b><span>Je Wohnung prüfen</span></button><button class=\"wizard-step\" type=\"button\" data-step=\"4\"><b>5 · Vorschau</b><span>Abrechnung ansehen</span></button></div>\n<div class=\"wizard-panel active\" data-panel=\"0\"><div class=\"step-heading\"><h3>1. Beleg hochladen oder manuell erfassen</h3><button class=\"btn primary\" data-next>Weiter zu den Angaben →</button></div><p class=\"muted\">Wähle hier, ob du die WEG-Abrechnung hochladen, die Abrechnung manuell erfassen oder eine Heizkostenabrechnung ergänzen möchtest. Beim Upload liest das System die erkennbaren Angaben aus und übernimmt nur die eindeutig identifizierte Wohnung.</p><div class=\"actions\"><button class=\"btn primary\" type=\"button\" id=\"wegUploadButton\">＋ WEG-Abrechnung hochladen</button><input id=\"wegUploadInput\" type=\"file\" accept=\".pdf,image/*\" multiple hidden><button class=\"btn\" type=\"button\" id=\"startManual\">＋ Manuell erfassen</button><input id=\"heaterUploadInput\" type=\"file\" accept=\".pdf,image/*\" multiple hidden><button class=\"btn\" type=\"button\" id=\"heaterUpload\">＋ Heizkostenabrechnung ergänzen</button></div><div id=\"heatingSelection\" class=\"mini\" style=\"margin-top:10px\"></div><div class=\"wizard-nav\"><span class=\"mini\">Bei manueller Erfassung wird dieser Schritt übersprungen.</span></div></div>\n<div class=\"wizard-panel\" data-panel=\"1\"><div class=\"step-heading\"><h3>2. Angaben zur Abrechnung</h3><div class=\"step-heading-actions\"><button class=\"btn back-step\" data-prev>← Zurück</button><button class=\"btn primary\" data-next>Weiter zu den Positionen →</button></div></div>\n<details class=\"billing-group\">\n <summary>1. Objekt</summary>\n<div class=\"billing-object-grid\"><div class=\"billing-object-row billing-object-row-2\"><div class=\"field\"><label for=\"objectMatch\">Vorhandenes Objekt übernehmen</label><select id=\"objectMatch\"><option value=\"\">Objekt auswählen</option></select></div><div class=\"field\"><label for=\"billingObjectLandlord\">Vermieter/in</label><select id=\"billingObjectLandlord\"></select></div></div><div class=\"billing-object-row billing-object-row-1\"><div class=\"field\"><label for=\"objectName\">Objektbezeichnung · WEG + Straße</label><input id=\"objectName\" type=\"text\"></div></div><div class=\"billing-object-row billing-object-row-1\"><div class=\"field\"><label for=\"objectStreet\">Straße und Hausnummer</label><input id=\"objectStreet\" type=\"text\"></div></div><div class=\"billing-object-row billing-object-row-2\"><div class=\"field\"><label for=\"objectPostal\">Postleitzahl</label><input id=\"objectPostal\" type=\"text\" inputmode=\"numeric\"></div><div class=\"field\"><label for=\"objectCity\">Ort</label><input id=\"objectCity\" type=\"text\"></div></div><div class=\"billing-object-row billing-object-row-3\"><div class=\"field\"><label for=\"billingObjectArea\">Objektfläche (m²)</label><div class=\"input-with-unit\" data-unit=\"m²\"><input id=\"billingObjectArea\" type=\"number\" min=\"0\" step=\"0.01\" inputmode=\"decimal\"></div></div><div class=\"field\"><label for=\"billingObjectUnits\">Anzahl Wohneinheiten</label><input id=\"billingObjectUnits\" type=\"number\" min=\"1\" step=\"1\" inputmode=\"numeric\"></div><div class=\"field\"><label for=\"billingObjectShare\">Eigentumsanteil</label><div class=\"input-with-unit\" data-unit=\"MEA\"><input id=\"billingObjectShare\"></div></div></div><div class=\"billing-object-row billing-object-row-2\"><div class=\"field\"><label for=\"wizardYear\">Abrechnungsjahr</label><input id=\"wizardYear\" type=\"number\" placeholder=\"z. B. 2025\"></div></div><div class=\"billing-object-row billing-object-row-2\"><div class=\"field\"><label for=\"wizardFrom\">Abrechnungsperiode Beginn</label><input id=\"wizardFrom\" type=\"date\"></div><div class=\"field\"><label for=\"wizardTo\">Abrechnungsperiode Ende</label><input id=\"wizardTo\" type=\"date\"></div></div></div>\n</details>\n<details class=\"billing-group\">\n <summary>2. Wohnung</summary>\n <div class=\"form-grid billing-unit-grid\">\n  <div class=\"field\"><label for=\"billingUnit\">Vorhandene Wohnung übernehmen</label><select id=\"billingUnit\"><option value=\"\">Wohnung auswählen</option></select></div>\n  <div class=\"field\"><label for=\"billingUnitTenant\">Mieter/in</label><select id=\"billingUnitTenant\"></select></div>\n  <div class=\"field\"><label for=\"reviewUnit\">Bezeichnung der Wohnungseinheit</label><input id=\"reviewUnit\" type=\"text\"></div>\n  <div class=\"field\"><label for=\"unitLocation\">Etage / Lagezusatz</label><input id=\"unitLocation\"></div>\n  <div class=\"field\"><label for=\"billingUnitShare\">Eigentumsanteil</label><div class=\"input-with-unit\" data-unit=\"MEA\"><input id=\"billingUnitShare\"></div></div>\n  <div class=\"field\"><label for=\"billingUnitArea\">Wohnfläche</label><div class=\"input-with-unit\" data-unit=\"m²\"><input id=\"billingUnitArea\" inputmode=\"decimal\"></div></div>\n  \n </div>\n</details>\n<details class=\"billing-group\">\n <summary>3. Mieter</summary>\n <div class=\"form-grid\">\n  <div class=\"field full\"><label for=\"tenantContact\">Mieter/in</label><select id=\"tenantContact\"></select></div>\n </div>\n <div id=\"billingTenantDetails\"></div>\n <div class=\"section-title\">Mietzeitraum für die Abrechnung</div>\n <div class=\"form-grid\">\n  <div class=\"field\"><label for=\"tenantFrom\">Beginn des Mietzeitraums</label><input id=\"tenantFrom\" type=\"date\"></div>\n  <div class=\"field\"><label for=\"tenantTo\">Ende des Mietzeitraums</label><input id=\"tenantTo\" type=\"date\"></div>\n </div>\n</details>\n<details class=\"billing-group\">\n <summary>4. Vermieter</summary>\n <div class=\"form-grid\">\n  <div class=\"field full\"><label for=\"billingLandlord\">Vermieter/in</label><select id=\"billingLandlord\"></select></div>\n </div>\n <div id=\"billingLandlordDetails\"></div>\n</details></div>\n<div class=\"wizard-panel\" data-panel=\"2\"><div class=\"step-heading\"><h3>3. Positionen zuordnen und erfassen</h3><div class=\"step-heading-actions\"><button class=\"btn back-step\" data-prev>← Zurück</button><button class=\"btn primary\" data-next>Weiter zur Verteilung →</button></div></div><p class=\"muted\" id=\"positionModeHint\">Beim Upload werden erkannte Positionen und Beträge hier eingetragen. Bei manueller Erfassung bleiben die Betragsfelder leer; Standardpositionen sind bereits vorbereitet.</p><div class=\"position-table-wrap\"><table class=\"table review-table position-table\" id=\"unitReviewTable\"><thead><tr><th>Position</th><th>Verteilerschlüssel</th><th>Verteilungsrelevanter<br>Betrag</th><th>Gesamtverteiler</th><th>Ihr Anteil</th><th>Ihr Betrag</th><th aria-label=\"Aktion\"></th></tr></thead><tbody id=\"positionTemplateBody\"></tbody></table></div><div class=\"split\" style=\"margin-top:12px\"><button class=\"btn\" id=\"addReviewPosition\">Position hinzufügen</button></div></div>\n<div class=\"wizard-panel\" data-panel=\"3\"><div class=\"step-heading\"><h3>4. Verteilung je Wohnung prüfen</h3><div class=\"step-heading-actions\"><button class=\"btn back-step\" data-prev>← Zurück</button><button class=\"btn primary\" data-next>Weiter zur Mietervorschau →</button></div></div><div class=\"callout\">Prüfe die Verteilung ausschließlich für die eine erkannte oder manuell bezeichnete Wohnung. Das Objekt liefert den vorgesehenen Verteilerschlüssel; ihre Fläche, MEA oder Verbrauchswerte werden nur übernommen, wenn sie vorhanden und eindeutig zugeordnet sind.</div><div class=\"card\" style=\"margin-top:14px\"><h4>Prüfstatus der Einheiten</h4><div id=\"unitDistributionStatus\" class=\"mini\">Nach der Bestätigung wird ausschließlich die erkannte oder manuell bezeichnete Wohnung geprüft. Nicht erkannte Etagen, Lagezusätze oder weitere Wohnungen werden nicht ergänzt.</div></div><div class=\"wizard-nav\"><span class=\"mini\">Korrekturen an Positionen bleiben in Schritt 3 möglich.</span></div></div>\n<div class=\"wizard-panel\" data-panel=\"4\"><div class=\"step-heading\"><h3>5. Mietervorschau</h3><div class=\"step-heading-actions\"><button class=\"btn back-step\" data-prev>← Zurück</button><button class=\"btn primary\" id=\"showPreview\">Mietervorschau erstellen →</button></div></div><div class=\"callout\">Die Vorschau enthält die bestätigten, umlagefähigen Kosten, die Vorauszahlungen und das Ergebnis für die ausgewählte Wohnung. Sie ist die fertige Abrechnung zum Prüfen und Versenden.</div><div id=\"previewReady\" class=\"metric\" style=\"margin-top:14px\"><span>Abrechnung</span><strong>Vorschau noch nicht erstellt</strong></div></div>\n<div class=\"callout\"><b>Erfassungswege:</b> Beim Upload wird diese Vorlage mit den erkannten Werten befüllt. Bei manueller Erfassung startet dieselbe Tabelle leer mit den Standardpositionen. Die Heizkostenabrechnung kann zusätzlich angehängt werden.</div>\n</section>\n</div></main>\n<div class=\"preview-overlay\" id=\"printPreview\" role=\"region\" aria-label=\"A4-Abrechnungsvorschau\">\n  <div class=\"preview-toolbar\"><span>Abrechnungsvorschau · A4 Hochformat</span><div><button class=\"btn\" id=\"closePreview\">Schließen</button><button class=\"btn primary\" id=\"printPreviewButton\">Drucken / PDF</button></div></div>\n  <div class=\"preview-modes\"><button class=\"btn active\" data-preview-mode=\"tenant\">Mietervorschau · ausgewählte Wohnung</button></div>\n  <section class=\"a4-page tenant-doc\"><div class=\"a4-head\"><div><h2>Betriebskostenabrechnung</h2><p><b>Mietervorschau · ausgewählte Wohnung</b></p><p>Objekt und Anschrift werden aus den bestätigten Angaben übernommen.</p></div><div class=\"a4-meta\">Abrechnungszeitraum<br><b>Zeitraum aus den bestätigten Angaben</b></div></div><div class=\"tenant-content\"></div><div class=\"a4-note\">Diese Mietervorschau enthält ausschließlich als umlagefähig gekennzeichnete Positionen. Vorauszahlungen und das daraus entstehende Guthaben oder die Nachzahlung werden in der fertigen Mieterabrechnung zusätzlich berücksichtigt.</div><footer class=\"a4-footer\"><p><b>Vermieter/in</b> · [Name] · [Anschrift]<br>[Telefon] · [E-Mail]</p><p><b>Bankverbindung</b> · [Kontoinhaber/in] · [Bank]<br>IBAN [IBAN] · BIC [BIC]</p></footer></section>\n</div>";
  const styles = "\n:host{--nic-font:system-ui,-apple-system,\"Segoe UI\",sans-serif;--nic-body-font-size:16px;--nic-subtext-font-size:14px;--nic-hint-font-size:12px;--nic-h1-size:45px;--nic-h2-size:22px;--nic-brand-radius:22px;--nic-background:#F5F7FB;--nic-outer-background:#F6F1E9;--nic-ink:#172033;--nic-green:#075C55;--nic-teal:#16867A;--nic-mint:#DDECE8;--nic-border:#E2E9E5;--nic-button:#0F172A;--nic-muted:#687385;--nic-red:#B42318;--nic-red-bg:#FEECEB;--nic-yellow:#FDE68A;--nic-card:#fff;--nic-shadow:0 10px 30px rgba(23,32,51,.07)}\n*{box-sizing:border-box}:host{display:block;min-width:0;color:var(--nic-ink);font:400 var(--nic-body-font-size)/1.5 var(--nic-font)}button,input,select{font:inherit;color:inherit}button{cursor:pointer}.brandbar{background:#fff;border-bottom:1px solid #e9e1d6}.brand-inner{max-width:1240px;margin:auto;padding:14px 28px;min-height:86px;display:grid;grid-template-columns:250px 1fr auto;gap:22px;align-items:center}.brand{display:flex;align-items:center;gap:10px;color:var(--nic-green);font-weight:800;letter-spacing:-.04em;font-size:20px;white-space:nowrap}.brand-mark{width:34px;height:34px;border:3px solid var(--nic-green);border-radius:10px 10px 10px 2px;display:grid;place-items:center;font-size:17px}.brand-desc{border-left:1px solid #cbd2cf;padding-left:18px;font-size:13px;line-height:1.45;color:#52605e}.topnav{display:flex;align-items:center;gap:24px;font-size:14px;white-space:nowrap}.topnav a{color:var(--nic-ink);text-decoration:none}.topnav .portal{border-radius:14px;background:var(--nic-green);color:white;padding:9px 15px;font-weight:700}.hero{background:linear-gradient(95deg,#f6f1e9 0%,#f2eee8 53%,#e4ece6 100%);border-bottom:1px solid rgba(7,92,85,.08)}.hero-inner{max-width:1184px;margin:auto;padding:30px 28px 27px}.eyebrow{color:var(--nic-green);font-size:var(--nic-subtext-font-size);font-weight:700;letter-spacing:.06em;text-transform:uppercase}.hero h1{font-size:var(--nic-h1-size);line-height:1.1;letter-spacing:-.035em;margin:5px 0 8px;color:var(--nic-green)}.hero p{margin:0;color:#354543;max-width:820px}.wrap{width:100%;max-width:none;margin:0;padding:0}.shell{background:var(--nic-card);border:1px solid var(--nic-border);border-radius:var(--nic-brand-radius);box-shadow:var(--nic-shadow);overflow:visible}.tabs{display:flex;gap:4px;padding:14px 20px 0;border-radius:21px 21px 0 0;border-bottom:1px solid var(--nic-border);background:#fff}.tab{border:0;background:transparent;padding:11px 18px 13px;color:#596674;border-bottom:3px solid transparent;font-weight:650}.tab.active{color:var(--nic-green);border-color:var(--nic-green)}.page{display:none;padding:24px}.page.active{display:block}.page-head{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;margin-bottom:20px}.object-switcher{display:flex;align-items:center;gap:10px;margin-top:12px}.object-switcher label{font-size:var(--nic-subtext-font-size);font-weight:650;color:#596674}.object-switcher select{min-width:310px;border:1px solid #d8dfdc;border-radius:10px;background:#fff;padding:9px 12px;min-height:42px}.page-head h2{margin:0 0 3px;color:var(--nic-ink);font-size:var(--nic-h2-size);line-height:1.25}.subtle{color:var(--nic-muted);font-size:var(--nic-subtext-font-size)}.actions{display:flex;gap:10px;flex-wrap:wrap}.btn{border:1px solid var(--nic-border);background:#fff;border-radius:12px;padding:9px 14px;font-weight:650;font-size:var(--nic-subtext-font-size)}.btn.primary{border-color:var(--nic-green);background:var(--nic-green);color:#fff}.btn.soft{color:var(--nic-green);background:#f2f8f6}#abrechnung>.page-head .actions{flex-wrap:nowrap;gap:8px}#abrechnung>.page-head .actions>.btn{flex:0 1 204px;width:204px;min-width:190px;padding:8px;font-size:13px;white-space:nowrap;text-align:center}#abrechnung [data-panel=\"0\"] .actions{flex-wrap:nowrap}#abrechnung [data-panel=\"0\"] .actions>.btn{flex:0 0 240px;width:240px;min-width:240px;white-space:nowrap;text-align:center}#abrechnung [data-panel=\"0\"] #heaterUpload{flex:0 0 280px;width:280px;min-width:280px}#abrechnung .wizard-step{white-space:nowrap}.grid{display:grid;gap:18px}.grid.two{grid-template-columns:1.15fr .85fr}.grid.equal{grid-template-columns:1fr 1fr}.card{background:#fff;border:1px solid var(--nic-border);border-radius:16px;padding:18px}.card h3{margin:0 0 14px;font-size:18px;line-height:1.25}.card h4{margin:0 0 10px;font-size:15px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px 16px}.field label{display:block;font-size:var(--nic-subtext-font-size);color:#596674;margin-bottom:5px}.field input,.field select{width:100%;border:1px solid #d8dfdc;border-radius:10px;background:#fff;padding:10px 12px;min-height:42px}.field .hint{display:block;margin-top:4px;color:var(--nic-muted);font-size:var(--nic-hint-font-size)}.full{grid-column:1/-1}.toolbar{display:flex;gap:12px;align-items:center;margin-bottom:16px}.search{flex:1;max-width:400px;border:1px solid #d8dfdc;background:#f7f8f9;border-radius:11px;padding:10px 13px}.table{width:100%;border-collapse:collapse;font-size:var(--nic-subtext-font-size)}.table th{text-align:left;color:#687385;font-size:12px;font-weight:700;border-bottom:1px solid var(--nic-border);padding:10px 9px}.table td{padding:12px 9px;border-bottom:1px solid #edf0ef;vertical-align:middle}.table tr:last-child td{border-bottom:0}.name{font-weight:680;color:var(--nic-ink)}.muted{color:var(--nic-muted)}.badge{display:inline-flex;align-items:center;border-radius:999px;padding:4px 10px;background:var(--nic-mint);color:var(--nic-green);font-size:12px;font-weight:750;white-space:nowrap}.badge.warn{background:#fff4d7;color:#7b5700}.badge.red{background:var(--nic-red-bg);color:var(--nic-red)}.section-title{display:flex;align-items:center;gap:9px;color:var(--nic-green);font-weight:750;margin:18px 0 10px}.section-title:first-child{margin-top:0}.icon{width:25px;height:25px;border-radius:8px;background:var(--nic-mint);display:inline-grid;place-items:center;color:var(--nic-green);font-size:14px}.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}.metric{border:1px solid var(--nic-border);border-radius:13px;background:#fbfcfc;padding:12px 14px}.metric span{display:block;color:var(--nic-muted);font-size:12px}.metric strong{font-size:17px}.meter-list{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.meter{border:1px solid var(--nic-border);border-radius:12px;padding:12px}.meter b{display:block;font-size:14px}.meter small{color:var(--nic-muted)}.callout{padding:12px 14px;background:#f1f8f6;border-left:3px solid var(--nic-green);border-radius:8px;color:#40514e;font-size:var(--nic-subtext-font-size)}.split{display:flex;align-items:center;justify-content:space-between;gap:12px}.mini{font-size:12px;color:var(--nic-muted)}.footer{max-width:1184px;margin:16px auto 30px;padding:14px 28px;color:#64716e;font-size:12px;display:flex;justify-content:space-between}.badge-count{margin-left:6px;background:#e9eef1;color:#41515a;border-radius:999px;padding:2px 8px;font-size:12px}.screen-note{font-size:11px;color:#74817f;margin-top:12px}.keyline{display:grid;grid-template-columns:minmax(150px,1.1fr) minmax(190px,1.15fr) minmax(200px,1.2fr) minmax(100px,.75fr) 72px;gap:10px;align-items:center;padding:12px 10px;border-bottom:1px solid #edf0ef;font-size:var(--nic-subtext-font-size)}.keyline>*{min-width:0;text-align:left;justify-self:stretch}.keyline.head{color:#687385;font-size:12px;font-weight:700}.keyline.head>*{text-align:left}.keyline select{text-align:left;text-align-last:left}.keyline:last-child{border-bottom:0}.grid.two>.card{min-width:0}.rent-history{width:100%;max-width:100%;min-width:0}.rent-history .keyline{grid-template-columns:minmax(0,1.55fr) minmax(0,.9fr) repeat(3,minmax(0,.85fr));gap:4px;min-width:0;padding:8px 3px;font-size:10px}.rent-history .keyline>*{white-space:normal;overflow-wrap:anywhere;line-height:1.3}.rent-history .keyline.head{display:grid}.control{color:var(--nic-green);font-weight:700}.bank{font-family:ui-monospace,monospace;font-size:12px}.right{text-align:right}.smallcaps{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#71807d}.foot-actions{display:flex;justify-content:flex-end;gap:9px;margin-top:16px}\n.open-object{border:0;background:transparent;padding:0;font:inherit}.open-object:hover{text-decoration:underline}.object-detail{scroll-margin-top:20px}.review-toolbar{display:grid;grid-template-columns:1fr 1fr 150px;gap:14px;align-items:end;margin:12px 0}.review-period{border:1px solid var(--nic-border);border-radius:10px;padding:8px 12px;min-height:42px}.review-period span,.review-period strong{display:block}.review-period strong{font-size:15px}.review-table-wrap{width:100%;max-height:520px;overflow:auto}.position-table-wrap{width:100%;max-height:520px;overflow:auto;overscroll-behavior:contain}.position-table{width:100%;border-collapse:separate;border-spacing:0}.position-table thead th{position:sticky;top:0;background:#fff;z-index:5;box-shadow:0 1px 0 var(--nic-border)}.position-table .group-row td{background:#f1f8f6;color:var(--nic-green);font-weight:750}.position-table .subtotal-row td{background:#f8faf9;font-weight:700}.position-table .add-row td{padding:5px 9px}.position-table .review-input{min-width:0}.review-table{min-width:900px;table-layout:fixed}.review-table th:nth-child(1){width:16%}.review-table th:nth-child(2){width:17%}.review-table th:nth-child(3){width:19%}.review-table th:nth-child(4){width:16%}.review-table th:nth-child(5){width:13%}.review-table th:nth-child(6){width:13%}.review-table th:nth-child(7){width:6%}.position-action-cell{text-align:center!important;padding-left:2px!important;padding-right:2px!important}.remove-position{width:25px;height:25px;padding:0;border:1px solid #d8dfdc;border-radius:50%;background:#fff;color:#687385;font-size:18px;line-height:1}.remove-position:hover{border-color:#b42318;background:#feeceb;color:#b42318}.review-input{width:100%;min-width:0;min-height:38px;border:1px solid #d8dfdc;border-radius:8px;padding:7px 8px;background:#fff;font-size:13px}.wizard-steps{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin:4px 0 12px}.wizard-step{border:1px solid var(--nic-border);background:#fff;border-radius:14px;padding:11px 12px;text-align:left;color:var(--nic-ink)}.wizard-step b,.wizard-step span{display:block}.wizard-step span{font-size:12px;color:var(--nic-muted);margin-top:3px}.wizard-step.active{border-color:var(--nic-green);background:#f1f8f7;color:var(--nic-green)}.wizard-panel{display:none;height:420px;border:1px solid var(--nic-border);border-radius:16px;padding:18px;margin-bottom:18px;background:#fff}.wizard-panel.active{display:flex;flex-direction:column}#abrechnung .wizard-panel[data-panel=\"1\"]{height:auto;min-height:420px}#abrechnung .wizard-panel[data-panel=\"1\"] .form-grid{gap:8px 12px}#abrechnung .wizard-panel[data-panel=\"1\"] .field label{margin-bottom:3px}#abrechnung .wizard-panel[data-panel=\"1\"] .field input,#abrechnung .wizard-panel[data-panel=\"1\"] .field select{min-height:36px;padding:7px 9px}#abrechnung .wizard-panel[data-panel=\"2\"]{height:auto;min-height:420px}#abrechnung .wizard-panel[data-panel=\"2\"] .position-table-wrap{flex:none;min-height:0;max-height:520px;overflow:auto;overscroll-behavior:contain}.wizard-panel h3{margin:0;font-size:18px}.wizard-panel .step-heading{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:12px}.step-heading-actions{display:flex;align-items:center;gap:14px;flex:0 0 auto}.step-heading-actions .back-step{font-size:13px;padding:7px 11px;min-height:36px;white-space:nowrap}.wizard-panel .step-heading h3{flex:1;min-width:0}.wizard-panel .step-heading button[data-next],.wizard-panel .step-heading #showPreview{width:220px;min-width:220px;flex:0 0 220px;white-space:nowrap;text-align:center;background:#f6c944;border-color:#e1b52b;color:#302600}.wizard-panel .step-heading button[data-next]:hover,.wizard-panel .step-heading #showPreview:hover{background:#edbd2f}.wizard-nav{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:auto;padding-top:18px}.wizard-nav .mini{flex:1}@media(max-width:850px){#abrechnung .wizard-panel[data-panel=\"1\"] .form-grid{grid-template-columns:1fr}.wizard-panel{height:520px}.review-toolbar{grid-template-columns:1fr}.review-table{min-width:860px}.wizard-steps{grid-template-columns:repeat(2,minmax(0,1fr))}.wizard-nav{flex-wrap:wrap}.wizard-nav .mini{flex-basis:100%;order:3}}\n.preview-overlay{display:none;position:fixed;inset:0;z-index:50;background:rgba(18,28,39,.72);overflow:auto;padding:24px}.preview-overlay.open{display:block}.preview-toolbar{max-width:210mm;margin:0 auto 14px;display:flex;justify-content:space-between;align-items:center;color:#fff}.preview-toolbar .btn{margin-left:8px;color:#172033}.preview-toolbar .btn.primary{color:#fff}.preview-modes{display:flex;gap:8px;margin:0 auto 14px;max-width:210mm}.preview-modes .btn.active{background:#dceeea;border-color:#8bbeb5;color:#075c55}.preview-overlay.landlord-mode .tenant-doc{display:none}.preview-overlay.tenant-mode .landlord-doc{display:none}.tenant-doc{display:none}.preview-overlay.tenant-mode .tenant-doc{display:block}.a4-page{position:relative;width:210mm;min-height:297mm;margin:0 auto 18px;padding:14mm 13mm;background:white;box-shadow:0 12px 44px rgba(0,0,0,.24);color:#172033;font:10px/1.35 Arial,sans-serif}.a4-head{display:flex;justify-content:space-between;gap:12px;border-bottom:2px solid #075c55;padding-bottom:8px;margin-bottom:9px}.a4-head h2{font-size:19px;margin:0 0 4px;color:#075c55}.a4-head p{margin:2px 0}.a4-meta{text-align:right;font-size:9px}.a4-section{margin:8px 0 3px;padding:4px 6px;background:#e9efed;color:#172033;font-weight:bold}.a4-table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:8px;line-height:1.2}.a4-table th{background:#f2f4f4;text-align:left;font-size:7px;padding:4px 3px;border:1px solid #cfd6d3}.a4-table td{padding:3px;border-bottom:1px solid #e3e7e5;vertical-align:top;overflow-wrap:anywhere}.a4-table .num{text-align:right;white-space:nowrap}.a4-table .total td{font-weight:bold;border-top:1px solid #89938f;background:#f8f9f9}.a4-summary{margin-top:9px;border-top:2px solid #075c55;padding-top:6px;display:flex;justify-content:space-between;font-size:10px;font-weight:bold}.a4-note{font-size:8px;color:#596674;margin-top:8px}.a4-footer{position:absolute;left:13mm;right:13mm;bottom:7mm;display:grid;grid-template-columns:1fr 1fr;gap:12px;padding-top:6px;border-top:1px solid #ccd5d2;font-size:8px;line-height:1.35;color:#596674}.a4-footer p{margin:0}.a4-page{padding-bottom:24mm}@media(max-width:850px){.preview-overlay{padding:10px}.a4-page{width:100%;min-height:0;padding:18px 18px 92px;overflow-x:auto}.a4-footer{left:18px;right:18px;bottom:16px;grid-template-columns:1fr 1fr;gap:8px}.preview-toolbar{padding:0 4px}}@media print{.preview-overlay{display:block!important;position:static;padding:0;background:white;overflow:visible}.preview-toolbar,.preview-modes,:host-context(body.settlement-printing) .wrap{display:none!important}.preview-overlay.landlord-mode .tenant-doc{display:none!important}.preview-overlay.tenant-mode .landlord-doc{display:none!important}.preview-overlay.tenant-mode .tenant-doc{display:block!important}.preview-overlay.landlord-mode .landlord-doc:nth-of-type(2){page-break-after:auto}.preview-overlay.tenant-mode .tenant-doc{page-break-after:auto}.a4-page{width:210mm;height:297mm;min-height:297mm;margin:0;box-shadow:none;page-break-after:always;overflow:hidden;padding:12mm}.a4-footer{left:12mm;right:12mm;bottom:7mm}.a4-page:last-child{page-break-after:auto}}\n@media(max-width:850px){.brand-inner{grid-template-columns:1fr auto}.brand-desc,.topnav a:not(.portal){display:none}.topnav{gap:8px}.hero h1{font-size:34px}.wrap{padding:0}.hero-inner{padding:22px 16px}.grid.two,.grid.equal{grid-template-columns:1fr}.summary{grid-template-columns:repeat(2,1fr)}.page{padding:16px}.keyline{grid-template-columns:1fr 1fr}.keyline.head{display:none}.footer{padding:12px 16px}}\n\n\n#unitReviewTable [aria-invalid=\"true\"]{border:2px solid #b42318;outline-offset:2px}\n#unitReviewTable .confirm-review-field{display:block;font-size:.75rem;margin-top:.25rem;padding:.2rem .35rem}\n\n.shell { border:0; border-radius:0; box-shadow:none; }\n.preview-overlay { z-index:10000; }\n@media print { .preview-overlay:not(.open) { display:none!important; } }\n\n@media screen {\n .tabs { flex-wrap:wrap; }\n}\n@container (max-width: 900px) {\n .tabs { padding-inline: 10px; }\n .page-head, .wizard-panel .step-heading { flex-direction:column; align-items:stretch; gap:10px; }\n .wizard-panel { height:auto; min-height:0; }\n #abrechnung .wizard-panel[data-panel=\"1\"], #abrechnung .wizard-panel[data-panel=\"2\"] { min-height:0; }\n #abrechnung > .page-head .actions, #abrechnung [data-panel=\"0\"] .actions, .step-heading-actions { flex-wrap:wrap; gap:8px; }\n #abrechnung > .page-head .actions > .btn, #abrechnung [data-panel=\"0\"] .actions > .btn,\n #abrechnung [data-panel=\"0\"] #heaterUpload,\n .wizard-panel .step-heading button[data-next], .wizard-panel .step-heading #showPreview {\n  flex:0 1 auto; min-width:0; width:auto; max-width:100%; white-space:normal;\n }\n}\n\n@media screen {\n :host { container-type:inline-size; }\n .object-switcher select { min-width:0; max-width:100%; }\n #abrechnung .wizard-steps { grid-template-columns:repeat(auto-fit,minmax(min(100%, 112px),1fr)); }\n #abrechnung .wizard-step { min-width:0; white-space:normal; overflow-wrap:anywhere; }\n}\n\n.btn.settlement-highlight {\n background: var(--nic-highlight-bg, #FDE68A);\n border-color: var(--nic-highlight-bg, #FDE68A);\n color: var(--nic-highlight-text, #172033);\n}\n.foot-actions { align-items:center; flex-wrap:wrap; }\n";

  function initialize(root, printSettlement) {
    const previewOverlay=root.getElementById('printPreview');
    root.querySelectorAll('.tab').forEach(button=>button.addEventListener('click',()=>{root.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b===button));root.querySelectorAll('.page').forEach(p=>p.classList.toggle('active',p.id===button.dataset.page));if(button.dataset.page!=='abrechnung')previewOverlay.classList.remove('open');}));
    root.getElementById('addObject')?.addEventListener('click',()=>{const panel=root.getElementById('objectDetailPanel');if(panel){panel.style.display='block';panel.scrollIntoView({behavior:'smooth',block:'start'});}});
    root.getElementById('closeObjectDetail')?.addEventListener('click',()=>{root.getElementById('objectDetailPanel').style.display='none'});
    const tenantContent=previewOverlay?.querySelector('.tenant-content');
    let activeWizardStep=0;
    let entryMode='';
    const wizardSteps=[...root.querySelectorAll('.wizard-step')];
    const wizardPanels=[...root.querySelectorAll('.wizard-panel')];
    function setWizardStep(index, moveFocus=false){
     activeWizardStep=Math.max(0,Math.min(4,index));
     if(activeWizardStep!==4)previewOverlay.classList.remove('open');
     wizardSteps.forEach((button,i)=>{
      const skipped=entryMode==='manual'&&i===0;
      button.disabled=skipped;
      button.classList.toggle('skipped',skipped);
      button.classList.toggle('active',i===activeWizardStep);
      button.setAttribute('aria-selected',i===activeWizardStep?'true':'false');
     });
     wizardPanels.forEach((panel,i)=>panel.classList.toggle('active',i===activeWizardStep));
     if(activeWizardStep===2)refreshPositionAllocations();
     if (moveFocus) {
      const heading=wizardPanels[activeWizardStep].querySelector('.step-heading h3');
      heading.tabIndex=-1;
      heading.focus({preventScroll:true});
      heading.scrollIntoView({block:'center'});
     }
    }
    function setEntryMode(mode, moveFocus = true){
     entryMode=mode;
     const status=root.getElementById('entryModeState');
     if (status) status.hidden = mode === 'manual';
     const detailsHint=root.getElementById('detailsModeHint');
     const positionHint=root.getElementById('positionModeHint');
     if(mode==='manual'){
      if(detailsHint)detailsHint.textContent='Gib Objekt, Abrechnungsjahr und Wohnung ein. Gehe anschließend zu den Kostenpositionen.';
      if(positionHint){positionHint.textContent='';positionHint.hidden=true;}
      setWizardStep(1,moveFocus);
     }else{
      if(status)status.textContent='Belegerfassung: Der WEG-Beleg wird zuerst eingelesen. Danach bestätigst du die erkannten Angaben und prüfst die Positionen.';
      if(detailsHint)detailsHint.textContent='Nach dem Einlesen werden eindeutig erkannte Angaben vorgeschlagen. Eine unsichere Wohnungszuordnung wird zur Bestätigung angezeigt; weitere Einheiten werden nicht angelegt.';
      if(positionHint){positionHint.hidden=false;positionHint.textContent='Erkannte Positionen und Beträge werden in die gleiche Vorlage übernommen. Nicht erkannte Zeilen kannst du ergänzen.';}
      setWizardStep(0);
     }
    }
    root.getElementById('wegUploadButton')?.addEventListener('click',()=>{setEntryMode('upload');root.getElementById('wegUploadInput')?.click()});
    const startManual = (moveFocus = true) => setEntryMode('manual', moveFocus);
    root.getElementById('startManual')?.addEventListener('click', () => startManual());
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
     else setWizardStep(activeWizardStep+1,true);
    }));
    root.querySelectorAll('[data-prev]').forEach(button=>button.addEventListener('click',()=>{
     if (entryMode === 'manual' && activeWizardStep === 1) {
      entryMode = '';
      setWizardStep(0, true);
      const status = root.getElementById('entryModeState');
      if (status) {
       status.hidden = false;
       status.textContent = 'Wähle den Start: Beim Upload liest das System den Beleg ein. Bei der manuellen Erfassung überspringst du diesen Schritt.';
      }
     }
     else setWizardStep(activeWizardStep-1,true);
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
     tr.innerHTML='<td><input class="review-input review-position" aria-label="Position" value="'+label.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;')+'"></td><td><select class="review-input review-key" aria-label="Verteilerschlüssel"><option value="Objektvorgabe" selected>Objektvorgabe</option><option>Wohnfläche</option><option>Wohneinheit</option><option>MEA</option><option>Verbrauch</option><option>Direktzuordnung</option></select></td><td><input class="review-input review-money" aria-label="Verteilungsrelevanter Betrag" inputmode="decimal"></td><td><input class="review-input review-base" aria-label="Gesamtverteiler" inputmode="decimal"></td><td><input class="review-input review-share" aria-label="Ihr Anteil" inputmode="decimal"></td><td><input class="review-input review-result" aria-label="Ihr Betrag" inputmode="decimal"></td><td class="position-action-cell">'+removeButton+'</td>';
     for (const cell of tr.cells) {
      if(cell.querySelector('.review-money,.review-result'))cell.classList.add('position-money-cell');
      cell.dataset.label = cell.firstElementChild?.getAttribute('aria-label') || '';
     }
     return tr;
    }
    function setPositionSectionExpanded(sectionId, expanded){
     const body=root.getElementById('positionTemplateBody');
     if(!body)return;
     body.classList.toggle('collapsed-'+sectionId,!expanded);
     const toggle=body.querySelector('[data-toggle-position-section="'+sectionId+'"]');
     if(toggle)toggle.setAttribute('aria-expanded',String(expanded));
    }
    function renderStandardTemplate(){
     const body=root.getElementById('positionTemplateBody');if(!body)return;body.innerHTML='';
     standardSections.forEach(section=>{
      const heading=document.createElement('tr');heading.className='group-row';
      const cell=heading.insertCell();cell.colSpan=7;
      const toggle=document.createElement('button');toggle.type='button';toggle.className='position-section-toggle';toggle.dataset.togglePositionSection=section.id;
      const title=document.createElement('span');title.textContent=section.title;
      const symbol=document.createElement('span');symbol.className='position-section-symbol';symbol.setAttribute('aria-hidden','true');
      toggle.append(title,symbol);cell.append(toggle);body.appendChild(heading);
      setPositionSectionExpanded(section.id,false);
      section.positions.forEach(label=>body.appendChild(makePositionRow(section.id,label)));
      const subtotal=document.createElement('tr');subtotal.className='subtotal-row';subtotal.dataset.subtotal=section.id;
      subtotal.innerHTML='<td colspan="2">Zwischensumme · '+section.title+'</td><td class="subtotal-total"></td><td></td><td></td><td class="subtotal-share"></td><td class="position-action-cell"></td>';body.appendChild(subtotal);
      const add=document.createElement('tr');add.className='add-row';add.dataset.positionSection=section.id;add.innerHTML='<td colspan="7"><button class="btn soft" type="button" data-add-position="'+section.id+'">Position hinzufügen</button></td>';body.appendChild(add);
     });
     const grand=document.createElement('tr');grand.className='subtotal-row grand-total-row';grand.innerHTML='<td colspan="2">Summe aller erfassten Positionen</td><td class="grand-total"></td><td></td><td></td><td class="grand-share"></td><td class="position-action-cell"></td>';body.appendChild(grand);
     updateSubtotals();
    }
    function parseGermanNumber(value){const normalized=String(value??'').trim().replace(/\s*€$/,'').replace(/\./g,'').replace(',','.').replace('−','-');const number=Number(normalized);return Number.isFinite(number)?number:0}
    function validReviewNumber(value){return /^[-−]?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?$/.test(String(value??'').trim())}
    function formatReviewMoney(input){if(validReviewNumber(input.value))input.value=germanMoney(parseGermanNumber(input.value)).replace(' €','')}
    function sumDisplay(rows,selector,total){return rows.some(row=>validReviewNumber(row.querySelector(selector)?.value))?germanMoney(total):''}
    function germanMoney(value){return Number(value||0).toLocaleString('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2})+' €'}
    function reviewRows(){return [...root.querySelectorAll('#unitReviewTable tbody tr.review-position-row')]}
    function recalculateReviewRow(row){
     const amount=parseGermanNumber(row.querySelector('.review-money')?.value);
     const base=parseGermanNumber(row.querySelector('.review-base')?.value);
     const share=parseGermanNumber(row.querySelector('.review-share')?.value);
     const result=row.querySelector('.review-result');
     const fields=['money','base','share'].map(name=>row.querySelector('.review-'+name));
     if(base>0&&fields.every(field=>validReviewNumber(field.value))){
      result.value=germanMoney(amount*share/base).replace(' €','');
      result.dataset.calculated='true';
     }else if(result.dataset.calculated){result.value='';delete result.dataset.calculated}
    }
    function updateSubtotals(){
     standardSections.forEach(section=>{
      const rows=reviewRows().filter(row=>row.dataset.category===section.id);
      const total=rows.reduce((sum,row)=>sum+parseGermanNumber(row.querySelector('.review-money')?.value),0);
      const share=rows.reduce((sum,row)=>sum+parseGermanNumber(row.querySelector('.review-result')?.value),0);
      const subtotal=root.querySelector('[data-subtotal="'+section.id+'"]');
      if(subtotal){subtotal.querySelector('.subtotal-total').textContent=sumDisplay(rows,'.review-money',total);subtotal.querySelector('.subtotal-share').textContent=sumDisplay(rows,'.review-result',share)}
     });
     const rows=reviewRows();
     const grandTotal=rows.reduce((sum,row)=>sum+parseGermanNumber(row.querySelector('.review-money')?.value),0);
     const grandShare=rows.reduce((sum,row)=>sum+parseGermanNumber(row.querySelector('.review-result')?.value),0);
     const grandRow=root.querySelector('.grand-total-row');
     if(grandRow){grandRow.querySelector('.grand-total').textContent=sumDisplay(rows,'.review-money',grandTotal);grandRow.querySelector('.grand-share').textContent=sumDisplay(rows,'.review-result',grandShare)}
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
     if(wegFrom&&!wegFrom.dataset.userEdited)wegFrom.value=year+'-01-01';
     if(wegTo&&!wegTo.dataset.userEdited)wegTo.value=year+'-12-31';
     if(tenantFrom&&!tenantFrom.dataset.userEdited)tenantFrom.value=year+'-01-01';
     if(tenantTo&&!tenantTo.dataset.userEdited)tenantTo.value=year+'-12-31';
    }
    root.getElementById('wizardYear')?.addEventListener('input',syncBillingPeriodFields);
    root.getElementById('wizardYear')?.addEventListener('change',syncBillingPeriodFields);
    ['tenantFrom','tenantTo','wizardFrom','wizardTo'].forEach(id=>root.getElementById(id)?.addEventListener('input',event=>{event.target.dataset.userEdited='true'}));
    renderStandardTemplate();
    root.getElementById('unitReviewTable')?.addEventListener('input',event=>{
     const row=event.target.closest('.review-position-row');
     if(row){
      if(event.target.matches('.review-base,.review-share')){delete event.target.dataset.autoValue;event.target.dataset.manualValue='true'}
      if(event.target.matches('.review-result'))delete event.target.dataset.calculated;
      else if(!event.target.matches('.review-key,.review-position'))recalculateReviewRow(row);
     }
     updateSubtotals();
    });
    root.getElementById('unitReviewTable')?.addEventListener('change',event=>{
     const row=event.target.closest('.review-position-row');
     if(row&&event.target.matches('.review-key,.review-position'))applyPositionAllocation(row);
     if(row&&event.target.matches('.review-money,.review-result'))formatReviewMoney(event.target);
     updateSubtotals();
    });
    root.getElementById('unitReviewTable')?.addEventListener('click',event=>{
     const sectionToggle=event.target.closest('[data-toggle-position-section]');
     if(sectionToggle){setPositionSectionExpanded(sectionToggle.dataset.togglePositionSection,sectionToggle.getAttribute('aria-expanded')!=='true');return}
     const removeButton=event.target.closest('.remove-position');
     if(removeButton){removeButton.closest('.review-position-row')?.remove();updateSubtotals();return}
     const button=event.target.closest('[data-add-position]');if(!button)return;
     const sectionId=button.dataset.addPosition;
     setPositionSectionExpanded(sectionId,true);
     const row=makePositionRow(sectionId,'',true);root.querySelector('[data-subtotal="'+sectionId+'"]').before(row);applyPositionAllocation(row);row.querySelector('.review-position').focus();
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
       values.forEach((value,i)=>{const td=document.createElement('td');td.textContent=value+(value&&(i===2||i===5)?' €':'');if(i>=2)td.className='num';tr.appendChild(td)});
       body.appendChild(tr);
      });
      const totalRow=document.createElement('tr');totalRow.className='total';const labelCell=document.createElement('td');labelCell.colSpan=5;labelCell.textContent='Zwischensumme';const amountCell=document.createElement('td');amountCell.className='num';amountCell.textContent=germanMoney(total);totalRow.append(labelCell,amountCell);body.appendChild(totalRow);
      table.appendChild(body);tenantContent.appendChild(table);
     });
     const tenantNote=previewOverlay?.querySelector('.tenant-doc .a4-note');
     if(tenantNote)tenantNote.textContent='Die Vorschau wird aus den erfassten Positionen der ausgewählten Wohnung erzeugt. Prüfe vor dem Versand den Abrechnungszeitraum, den Mietvertrag und die hinterlegten Vorauszahlungen.';
    }
    
    root.querySelectorAll('[data-preview-mode]').forEach(button=>button.addEventListener('click',()=>{const mode=button.dataset.previewMode;previewOverlay?.classList.toggle('tenant-mode',mode==='tenant');previewOverlay?.classList.toggle('landlord-mode',mode==='landlord');root.querySelectorAll('[data-preview-mode]').forEach(item=>item.classList.toggle('active',item===button))}));root.getElementById('showPreview')?.addEventListener('click',()=>{syncReviewToPreview();previewOverlay?.classList.remove('landlord-mode');previewOverlay?.classList.add('tenant-mode');root.querySelectorAll('[data-preview-mode]').forEach(item=>item.classList.toggle('active',item.dataset.previewMode==='tenant'));previewOverlay?.classList.add('open')});root.getElementById('closePreview')?.addEventListener('click',()=>previewOverlay?.classList.remove('open'));root.getElementById('printPreviewButton')?.addEventListener('click',printSettlement);root.addEventListener('keydown',event=>{if(event.key==='Escape'&&previewOverlay.classList.contains('open'))byId('closePreview').click()});
    
    
    
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
    contactFields.forEach((field, index) => {
     field.id = 'settlementContactField' + index;
     field.previousElementSibling.htmlFor = field.id;
    });
    let contacts = [];
    const contactSelections = [
     ['tenantContact','Mieter/in'], ['unitTenant','Mieter/in'], ['billingUnitTenant','Mieter/in'],
     ['objectLandlord','Vermieter/in'], ['objectManager','Verwalter/in'],
     ['billingObjectLandlord','Vermieter/in'], ['billingLandlord','Vermieter/in']
    ];
    function updateContacts() {
     for (const [id, role] of contactSelections) {
      const select = byId(id);
      const previous = select.value;
      select.replaceChildren(new Option('Kontakt auswählen',''));
      contacts.forEach((contact, index) => {
       if (contact?.[0] === role) select.add(new Option([contact[1],contact[2]].filter(Boolean).join(' '),String(index)));
      });
      select.value = previous;
     }
     renderBillingContacts();
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
    const contactTitle = contactCard.querySelector('h3');
    const contactRole = contactFields[0];
    const tenancyPanel = document.createElement('section');
    tenancyPanel.id = 'tenantDetails';
    tenancyPanel.hidden = true;
    tenancyPanel.innerHTML = `<h4 class="section-title">Mietverhältnis</h4>
     <div class="form-grid">
      <div class="field"><label for="tenantStart">Mietbeginn</label><input type="date" id="tenantStart"></div>
      <div class="field"><label for="tenantEnd">Mietende</label><input type="date" id="tenantEnd"></div>
      <div class="field full"><label><input type="checkbox" id="tenantActive" checked> Aktiv</label></div>
     </div>
     <h4 class="section-title">Miete und Vorauszahlungen</h4>
     <div id="tenantRentHistory"></div>`;
    contactCard.append(tenancyPanel);
    const tenantStart = byId('tenantStart');
    const tenantEnd = byId('tenantEnd');
    const tenantActive = byId('tenantActive');
    const rentHistory = byId('tenantRentHistory');
    const rentFields = [
     ['validFrom', 'Gültig ab'], ['coldRent', 'Kaltmiete (€)'],
     ['operatingCosts', 'Betriebskosten (€)'], ['heatingCosts', 'Heizkosten (€)']
    ];
    let editingContact = null;

    function addRentPeriod(values = {}) {
     const row = document.createElement('fieldset');
     row.className = 'form-grid tenant-rent-period';
     const legend = document.createElement('legend');
     legend.textContent = 'Mietkonditionen';
     row.append(legend);
     for (const [key, caption] of rentFields) {
      const label = document.createElement('label');
      label.className = 'field';
      const name = document.createElement('span');
      name.textContent = caption;
      const input = document.createElement('input');
      input.name = key;
      input.type = key === 'validFrom' ? 'date' : 'number';
      if (input.type === 'number') {
       input.min = '0';
       input.step = '0.01';
       input.inputMode = 'decimal';
      }
      input.value = values[key] ?? '';
      label.append(name, input);
      row.append(label);
     }
     const remove = action('×', () => {
      if (!window.confirm('Diese Mietkonditionen entfernen?')) return;
      row.remove();
      if (!rentHistory.childElementCount) addRentPeriod();
      rentHistory.lastElementChild.append(addPeriod);
      addPeriod.focus();
     });
     remove.className = 'contact-delete rent-period-delete';
     remove.setAttribute('aria-label', 'Mietkonditionen entfernen');
     remove.title = 'Mietkonditionen entfernen';
     row.append(remove);
     rentHistory.append(row);
     row.append(addPeriod);
     return row.querySelector('input');
    }

    const addPeriod = action('＋ Mietanpassung hinzufügen', () => addRentPeriod().focus());
    addPeriod.className = 'full add-rent-period';
    function syncTenancyPanel() {
     tenancyPanel.hidden = contactRole.value !== 'Mieter/in';
    }
    contactRole.addEventListener('change', syncTenancyPanel);

    function openContact(index = null) {
     editingContact = index;
     const contact = contacts[index];
     const tenancy = contact?.[contactFields.length];
     contactFields.forEach((field, i) => { field.value = contact?.[i] ?? ''; });
     tenantStart.value = tenancy?.start ?? '';
     tenantEnd.value = tenancy?.end ?? '';
     tenantActive.checked = tenancy?.active ?? true;
     rentHistory.replaceChildren();
     for (const period of tenancy?.periods?.length ? tenancy.periods : [{}]) addRentPeriod(period);
     syncTenancyPanel();
     contactTitle.textContent = index === null ? 'Kontakt erfassen' : 'Kontakt bearbeiten';
     saveContact.textContent = index === null ? 'Kontakt übernehmen' : 'Änderungen speichern';
     contactStatus.textContent = '';
    }

    function readTenancy() {
     if (!tenantStart.reportValidity() || !tenantEnd.reportValidity()) return null;
     if (tenantStart.value && tenantEnd.value && tenantEnd.value < tenantStart.value) {
      contactStatus.textContent = 'Das Mietende darf nicht vor dem Mietbeginn liegen.';
      tenantEnd.focus();
      return null;
     }
     const periods = [];
     const dates = new Set();
     for (const row of rentHistory.children) {
      const inputs = [...row.querySelectorAll('input')];
      if (inputs.every(input => !input.value && !input.validity.badInput)) continue;
      for (const input of inputs) {
       input.required = true;
       const valid = input.reportValidity();
       input.required = false;
       if (!valid) return null;
      }
      const effectiveDate = inputs[0].value;
      if (dates.has(effectiveDate)) {
       contactStatus.textContent = 'Für dieses Gültigkeitsdatum gibt es bereits einen Eintrag.';
       inputs[0].focus();
       return null;
      }
      dates.add(effectiveDate);
      periods.push(Object.fromEntries(inputs.map(input => [input.name, input.value])));
     }
     periods.sort((first, second) => first.validFrom.localeCompare(second.validFrom));
     return {start: tenantStart.value, end: tenantEnd.value, active: tenantActive.checked, periods};
    }

    const contactActions = document.createElement('div');
    contactActions.className = 'foot-actions';
    const contactStatus = document.createElement('span');
    contactStatus.setAttribute('role', 'status');
    const saveContact = action('Kontakt übernehmen', () => {
     contactStatus.textContent = '';
     const contact = contactFields.map(field => field.value.trim());
     if (!contact[0] || !(contact[1] || contact[2])) { contactRole.focus(); return; }
     if (contact[0] === 'Mieter/in') {
      const tenancy = readTenancy();
      if (!tenancy) return;
      contact.push(tenancy);
     }
     const index = editingContact ?? contacts.length;
     const previous = contacts;
     contacts = contacts.slice();
     contacts[index] = contact;
     if (!saveDraft(contactStatus, '')) { contacts = previous; return; }
     openContact(editingContact === null ? null : index);
     updateContacts();
     renderContacts();
     renderUnits();
    });
    saveContact.classList.add('settlement-highlight');
    contactActions.append(contactStatus, saveContact);
    contactCard.append(contactActions);
    openContact();
    byId('addContact').addEventListener('click', () => {
     openContact();
     contactRole.focus();
    });
    function deleteContact(index, name) {
     if (!window.confirm('Kontakt „' + name + '“ löschen? Zugeordnete Objekte und Wohnungen bleiben bestehen.')) return;
     const previousContact = contacts[index];
     const previousUnits = savedUnits;
     const selected = contactSelections.map(([id]) => byId(id)).filter(field => field.value === String(index));
     for (const field of selected) field.value = '';
     // The index is referenced by existing records. Keep it vacant so later contacts get new indices.
     contacts[index] = null;
     savedUnits = savedUnits.map(unit => unit.tenant === String(index) ? {...unit, tenant: ''} : unit);
     if (!saveDraft(contactStatus, '')) {
      contacts[index] = previousContact;
      savedUnits = previousUnits;
      for (const field of selected) field.value = String(index);
      return;
     }
     if (editingContact === index) openContact();
     updateContacts();
     renderContacts();
     renderUnits();
     byId('addContact').focus();
    }
    function renderContacts() {
     contactList.replaceChildren();
     contacts.forEach((contact, index) => {
      if (!contact) return;
      const [role, first, last] = contact;
      const name = [first,last].filter(Boolean).join(' ');
      const label = [first,last,role].filter(Boolean).join(' · ');
      const edit = action(label, () => {
       openContact(index);
       contactRole.focus();
      });
      edit.className = 'contact-edit';
      edit.setAttribute('aria-label', label + ' bearbeiten');
      const remove = action('×', () => deleteContact(index, name));
      remove.className = 'contact-delete';
      remove.setAttribute('aria-label', name + ' löschen');
      remove.title = 'Kontakt löschen';
      const line = document.createElement('div');
      line.className = 'contact-row';
      line.append(edit, remove);
      contactList.append(line);
     });
     if (!contactList.childElementCount) contactList.textContent = 'Noch keine Kontakte vorhanden';
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
    balancePanel.className='position-balance-panel';
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
    
    // Per-position defaults for the currently stored object, using the existing catalogue.
    const keyPanel=root.querySelector('#schluessel article');
    const mappingTitle=keyPanel.querySelector('h3');
    mappingTitle.textContent='Verteilerschlüssel je Kostenposition';
    keyPanel.querySelector('p').textContent='Wähle den vorgesehenen Schlüssel je Position. Ohne Zuordnung bleibt die Objektvorgabe offen.';
    const mappingGrid=document.createElement('div');mappingGrid.className='form-grid';
    const objectKeyFields=new Map();
    const allocationKeys=['Wohnfläche','Wohneinheit','MEA','Verbrauch','Direktzuordnung'];
    for(const section of standardSections){
     const title=document.createElement('h4');title.className='full';title.textContent=section.title;mappingGrid.append(title);
     for(const label of section.positions){
      const field=document.createElement('div');field.className='field';
      const select=document.createElement('select');select.id='objectPositionKey'+objectKeyFields.size;
      select.add(new Option('Nicht zugeordnet',''));
      for(const key of allocationKeys)select.add(new Option(key,key));
      const caption=document.createElement('label');caption.htmlFor=select.id;caption.textContent=label;
      field.append(caption,select);mappingGrid.append(field);
      objectKeyFields.set(section.id+'|'+normalizedLabel(label),select);
     }
    }
    const mappingStatus=document.createElement('div');mappingStatus.setAttribute('role','status');
    const mappingSave=action('Zuordnungen speichern',()=>{
     if(!byId('propertyName').value.trim()){mappingStatus.textContent='Speichere zuerst ein Objekt.';return}
     saveDraft(mappingStatus,'Zuordnungen gespeichert.');
    });mappingSave.classList.add('settlement-highlight');
    const mappingActions=document.createElement('div');mappingActions.className='foot-actions';mappingActions.append(mappingStatus,mappingSave);
    keyPanel.querySelector('button').remove();keyPanel.append(mappingGrid,mappingActions);
    function decimalFromMaster(value,htmlNumber=false){
     const v=String(value??'').trim();
     if(!v)return '';
     if(htmlNumber&&/^\d+(?:\.\d+)?$/.test(v))return v.replace('.',',');
     return validReviewNumber(v)&&parseGermanNumber(v)>=0?v:'';
    }
    function meaParts(value){
     const v=String(value??'').trim();
     const ratio=v.match(/^([^/]+)\/([^/]+)$/);
     if(ratio)return [decimalFromMaster(ratio[1]),decimalFromMaster(ratio[2])];
     const percent=v.match(/^(.+?)\s*%$/);
     if(percent)return [decimalFromMaster(percent[1]),'100'];
     return [decimalFromMaster(v),''];
    }
    function allocationValues(key){
     const val=id=>byId(id).value;
     if(key==='Wohnfläche')return [decimalFromMaster(val('billingObjectArea'),true),decimalFromMaster(val('billingUnitArea'))];
     if(key==='Wohneinheit')return [decimalFromMaster(val('billingObjectUnits'),true),val('reviewUnit').trim()?'1':''];
     if(key==='MEA'){
      const [total,totalDen]=meaParts(val('billingObjectShare'));
      const [part,partDen]=meaParts(val('billingUnitShare'));
      if(totalDen&&partDen&&parseGermanNumber(totalDen)!==parseGermanNumber(partDen))return ['',''];
      if(!totalDen&&partDen&&parseGermanNumber(total)!==parseGermanNumber(partDen))return ['',''];
      if(totalDen&&!partDen)return [total,''];
      return [total,part];
     }
     if(key==='Direktzuordnung'&&val('reviewUnit').trim())return ['1','1'];
     return ['',''];
    }
    function applyPositionAllocation(row){
     const keyField=row.querySelector('.review-key');
     const label=row.querySelector('.review-position').value;
     const sameObject=byId('propertyName').value.trim()&&byId('propertyName').value.trim()===byId('objectName').value.trim();
     const mapped=sameObject?objectKeyFields.get(row.dataset.category+'|'+normalizedLabel(label))?.value:'';
     const key=keyField.value==='Objektvorgabe'?mapped:keyField.value;
     const values=allocationValues(key);
     ['base','share'].forEach((name,i)=>{
      const field=row.querySelector('.review-'+name);
      if(field.dataset.manualValue)return;
      if(!field.value.trim()||field.dataset.autoValue!==undefined){
       field.value=values[i];if(values[i])field.dataset.autoValue=values[i];else delete field.dataset.autoValue;
      }
     });
     if(row.querySelector('.review-result').dataset.calculated||!row.querySelector('.review-result').value.trim())recalculateReviewRow(row);
    }
    function refreshPositionAllocations(){
     for(const row of reviewRows())applyPositionAllocation(row);
     updateSubtotals();
    }
    const draftFields = [...root.querySelectorAll('#abrechnung input[id]:not([type=file]), #abrechnung select[id]:not(#objectMatch,#billingUnit,#billingUnitTenant), #objectDetailPanel input[id], #objectDetailPanel select[id], #schluessel select[id^=objectPositionKey]')];
    const storageKey = 'nic-settlement-draft-v1';
    let savedUnits = [];
    const objectFields = [
     ['propertyName','objectName'], ['propertyStreet','objectStreet'],
     ['propertyPostal','objectPostal'], ['propertyCity','objectCity'],
     ['propertyArea','billingObjectArea'], ['propertyUnits','billingObjectUnits'],
     ['propertyOwnershipShare','billingObjectShare'], ['objectLandlord','billingObjectLandlord']
    ];
    function refreshBillingChoices() {
     const name = byId('propertyName').value.trim();
     byId('objectMatch').replaceChildren(new Option('Objekt auswählen',''));
     if (name) byId('objectMatch').add(new Option(name,name));
     const keySelect=byId('keyObjectSelect');
     const previousKeyObject=keySelect.value;
     keySelect.replaceChildren(new Option('Objekt wählen',''));
     if(name)keySelect.add(new Option(name,name));
     if(name&&previousKeyObject===name)keySelect.value=name;
     const unitSelect = byId('billingUnit');
     unitSelect.replaceChildren(new Option('Wohnung auswählen',''));
     for (const unit of savedUnits) unitSelect.add(new Option(unit.name,unit.name));
     unitSelect.value = savedUnits.some(unit => unit.name === byId('reviewUnit').value) ? byId('reviewUnit').value : '';
    }
    byId('objectMatch').addEventListener('change', event => {
     if (!event.target.value) return;
     for (const [source,target] of objectFields) byId(target).value = byId(source).value;
     byId('billingLandlord').value = byId('billingObjectLandlord').value;
     renderBillingContacts();refreshPositionAllocations();
    });
    byId('billingObjectLandlord').addEventListener('change', () => {
     byId('billingLandlord').value = byId('billingObjectLandlord').value;
     renderBillingContacts();
    });
    byId('billingUnit').addEventListener('change', event => {
     const unit = savedUnits.find(item => item.name === event.target.value);
     if (!unit) return;
     for (const [id,value] of Object.entries({
      reviewUnit:unit.name, unitLocation:unit.floor, billingUnitArea:unit.area,
      billingUnitShare:unit.share, tenantContact:unit.tenant
     })) byId(id).value = value ?? '';
     renderBillingContacts();refreshPositionAllocations();
    });
    function appendBillingDetails(container, entries) {
     const list = document.createElement('dl');
     list.className = 'billing-contact-fields';
     for (const [label,value] of entries) {
      const field = document.createElement('div');
      const term = document.createElement('dt');
      const detail = document.createElement('dd');
      term.textContent = label;
      detail.textContent = value || '';
      field.append(term,detail);
      list.append(field);
     }
     container.append(list);
    }
    function renderBillingContacts() {
     byId('billingUnitTenant').value = byId('tenantContact').value;
     for (const [selectId,containerId] of [['tenantContact','billingTenantDetails'],['billingLandlord','billingLandlordDetails']]) {
      const container = byId(containerId);
      container.replaceChildren();
      const index = byId(selectId).value;
      const contact = index === '' ? null : contacts[Number(index)];
      const entries = contactFields.map((field,i) => [field.previousElementSibling.textContent,contact?.[i]]);
      if (selectId === 'tenantContact') {
       const tenancy = contact?.[contactFields.length];
       entries.push(['Mietbeginn',tenancy?.start?.split('-').reverse().join('.')],['Mietende',tenancy?.end?.split('-').reverse().join('.')],
        ['Aktiv',tenancy && (tenancy.active ? 'Ja' : 'Nein')]);
       appendBillingDetails(container,entries);
       for (const period of tenancy?.periods ?? []) {
        appendBillingDetails(container,rentFields.map(([key,label]) => [label,key === 'validFrom' ?
         period[key].split('-').reverse().join('.') : period[key] && germanMoney(Number(period[key]))]));
       }
      } else appendBillingDetails(container,entries);
     }
    }
    for (const id of ['tenantContact','billingLandlord']) byId(id).addEventListener('change',renderBillingContacts);
    byId('billingUnitTenant').addEventListener('change',event => {
     byId('tenantContact').value = event.target.value;
     renderBillingContacts();
    });
    function renderUnits() {
     const objectName = byId('propertyName').value.trim();
     const rows = byId('unitRows');
     const unitObjectSelect=byId('unitObjectSelect');
     const previousUnitObject=unitObjectSelect.value;
     unitObjectSelect.replaceChildren(new Option('Objekt wählen',''));
     if(objectName)unitObjectSelect.add(new Option(objectName,objectName));
     if(objectName&&previousUnitObject===objectName)unitObjectSelect.value=objectName;
     rows.replaceChildren();
     for (const unit of savedUnits) {
      const row = rows.insertRow();
      const contact = unit.tenant === '' ? null : contacts[Number(unit.tenant)];
      for (const value of [unit.name, unit.floor, unit.area ? unit.area + ' m²' : '', unit.share,
       contact ? [contact[1],contact[2]].filter(Boolean).join(' ') : '']) row.insertCell().textContent = value || '';
     }
     if (!savedUnits.length) {
      const cell = rows.insertRow().insertCell();
      cell.colSpan = 5;
      cell.textContent = 'Noch keine Einheiten erfasst.';
     }
     byId('unitCount').textContent = savedUnits.length;
     refreshBillingChoices();
    }
    byId('addUnit').addEventListener('click', () => byId('unitName').focus());
    byId('saveUnit').addEventListener('click', () => {
     const status = byId('unitSaveStatus');
     status.hidden = false;
     if (!byId('unitObjectSelect').value) {
      status.textContent = 'Speichere zuerst ein Objekt mit einer Bezeichnung.';
      return;
     }
     const unit = {name:byId('unitName').value.trim(), floor:byId('unitFloor').value.trim(),
      area:byId('unitArea').value.trim(), share:byId('unitShare').value.trim(), tenant:byId('unitTenant').value};
     if (!unit.name) {
      status.textContent = 'Gib eine Bezeichnung für die Einheit ein.';
      byId('unitName').focus();
      return;
     }
     const previous = savedUnits;
     savedUnits = [...savedUnits.filter(saved => saved.name !== unit.name), unit];
     if (!saveDraft(status, '')) { savedUnits = previous; return; }
     status.hidden = true;
     for (const id of ['unitName', 'unitFloor', 'unitArea', 'unitShare', 'unitTenant']) byId(id).value = '';
     renderUnits();
    });
    function saveDraft(status, message) {
     try {
      localStorage.setItem(storageKey, JSON.stringify({
       fields: Object.fromEntries(draftFields.map(field => [field.id, field.value])),
       references: Object.fromEntries(Object.entries(balanceFields).map(([key, fields]) => [key, fields.map(field => field.input.value)])),
       contacts, units: savedUnits, rows: reviewRows().map(row => [row.dataset.category, valuesOf(row), positionFields.filter(field => row.querySelector(".review-" + field).getAttribute("aria-invalid") === "true")])
      }));
      status.textContent = message;
      return true;
     } catch { status.textContent = 'Der Browser konnte die Angaben nicht speichern.'; return false; }
    }
    const saveDraftButton = action('Entwurf lokal speichern', () => saveDraft(notes, 'Entwurf in diesem Browser gespeichert.'));
    saveDraftButton.id = 'saveSettlementDraft';
    byId('showReceipts').after(saveDraftButton);
    notes.className = 'settlement-draft-status';
    byId('showReceipts').closest('.page-head').after(notes);
    byId('saveProperty').addEventListener('click', () => {
     for (const field of root.querySelectorAll('#objectDetailPanel input[type="number"]')) {
      if (!field.reportValidity()) return;
     }
     if (saveDraft(byId('propertySaveStatus'), '')) renderUnits();
    });
    try {
     const saved = JSON.parse(localStorage.getItem(storageKey));
     if (saved) {
      contacts = Array.isArray(saved.contacts) ? saved.contacts : [];
      savedUnits = Array.isArray(saved.units) ? saved.units : [];
      for (const [key, fields] of Object.entries(balanceFields)) fields.forEach(({input}, index) => { input.value = saved.references?.[key]?.[index] || ''; });
      updateContacts();
      renderContacts();
      for (const field of draftFields) field.value = saved.fields[field.id] ?? '';
      if (!Object.hasOwn(saved.fields,'billingLandlord')) byId('billingLandlord').value = byId('objectLandlord').value;
      byId('positionTemplateBody').querySelectorAll('.review-position-row').forEach(row => row.remove());
      for (const [block, values, flagged = []] of saved.rows) {
       const row = insertPosition(block, '');
       positionFields.forEach((name, i) => row.querySelector('.review-' + name).value = values[i]);
       for (const field of flagged) if (positionFields.includes(field)) flagReviewField(row.querySelector('.review-' + field));
      }
      updateSubtotals();
     }
    } catch { notes.textContent = 'Der gespeicherte Entwurf konnte nicht geladen werden.'; }
    
    renderUnits();
    renderBillingContacts();
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
     const owner = name('billingLandlord'), tenant = name('tenantContact');
     const header = previewOverlay.querySelector('.a4-head');
     header.querySelector('p').textContent = (landlordMode ? 'Vermietervorschau' : 'Mietervorschau') + ' · ' +
      [byId('reviewUnit').value, tenant.slice(1,3).filter(Boolean).join(' ')].filter(Boolean).join(' · ');
     header.querySelectorAll('p')[1].textContent = ['objectName','objectStreet','objectPostal','objectCity'].map(id => byId(id).value).filter(Boolean).join(' · ');
     header.querySelector('.a4-meta').textContent = [byId('wizardFrom').value,byId('wizardTo').value].filter(Boolean).map(value=>value.split('-').reverse().join('.')).join(' – ');
     const footer = previewOverlay.querySelector('.a4-footer');
     footer.children[0].textContent = ['Vermieter/in',...owner.slice(1,8)].filter(Boolean).join(' · ');
     footer.children[1].textContent = owner.slice(8,12).some(Boolean) ? ['Bankverbindung',...owner.slice(8,12)].filter(Boolean).join(' · ') : '';
    }
    previewModes.append(action('Vermietervorschau', () => { landlordMode = true; fillPreview(); }));
    previewModes.firstElementChild.addEventListener('click', () => { landlordMode = false; fillPreview(); });
    byId('showPreview').addEventListener('click', () => { landlordMode = false; fillPreview(); });
    root.querySelector('[data-page="abrechnung"]').click();
    setWizardStep(0);

    const close = byId('closePreview');
    const open = byId('showPreview');
    open.addEventListener('click', () => {
     close.focus({preventScroll:true});
     previewOverlay.scrollIntoView({block:'start'});
    });
    close.addEventListener('click', () => open.focus());
    return startManual;
  }

  const entryActions = [
    {action: 'upload', mode: 'upload', title: 'WEG-Abrechnung hochladen', description: 'Fertige Jahresabrechnung automatisch einlesen'},
    {action: 'manual', mode: 'manuell', title: 'Manuelle Erfassung', description: 'Betriebskosten selbst eintragen'}
  ];

  function prepareLanding(host) {
    const fallback = document.createElement('div');
    fallback.className = 'nic-settlement-actions nic-copy-tile-grid';
    for (const {action, mode, title, description} of entryActions) {
      const existing = host.querySelector('[data-nic-settlement-action="' + action + '"]') ||
        [...host.querySelectorAll('a.nic-copy-tile')].find(link =>
          link.querySelector('.nic-copy-tile__title')?.textContent.trim() === title
        );
      const control = existing || document.createElement('a');
      control.dataset.nicSettlementAction = action;
      if (control.matches('a')) {
        const destination = new URL(location.href);
        destination.searchParams.set('modus', mode);
        destination.hash = '';
        control.href = destination.href;
      }
      if (!existing) {
        control.className = 'nic-copy-tile';
        const label = document.createElement('strong');
        label.className = 'nic-copy-tile__title';
        label.textContent = title;
        const subtitle = document.createElement('small');
        subtitle.className = 'nic-copy-tile__description';
        subtitle.textContent = description;
        control.append(label, subtitle);
        fallback.append(control);
      }
    }
    if (fallback.childElementCount) host.append(fallback);
  }

  let savedWorkspace;
  function placeWorkspace(host, workspace) {
    host.replaceChildren(workspace);
  }
  function mount() {
    if (!/\/nebenkostenabrechnung(?:\/index\.html|\/)?$/.test(location.pathname)) return;
    // The direct route can render before the shared navigation finishes loading its settings.
    const host = document.getElementById('nicContentView');
    if (!host) return;
    const mode = new URLSearchParams(location.search).get('modus');
    if (!entryActions.some(action => action.mode === mode)) {
      prepareLanding(host);
      return;
    }
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
    // The workspace uses a shadow root, so the shared page button states need a local rule.
    style.textContent = styles + `
      .contact-row{display:flex;align-items:center;justify-content:space-between;gap:8px;border-bottom:1px solid var(--nic-border);padding:4px 0}
      .contact-edit,.contact-delete{color:var(--nic-ink);background:transparent;border:0;cursor:pointer}
      .contact-edit{min-width:0;padding:6px 4px;text-align:left;font-size:var(--nic-subtext-font-size);font-weight:650;overflow-wrap:anywhere}
      .contact-delete{flex:none;width:32px;height:32px;color:var(--nic-red);font-size:1.3em;line-height:1}
      button:not(:is(.tab,.contact-edit,.settlement-exit-button,.contact-delete,.position-section-toggle)){transition:filter .14s ease,box-shadow .14s ease,transform .12s ease}
      button:not(:is(.tab,.contact-edit,.settlement-exit-button,.contact-delete,.position-section-toggle)):enabled:hover{filter:brightness(.94);box-shadow:0 5px 12px rgba(15,23,42,.16)}
      button:not(:is(.tab,.contact-edit,.settlement-exit-button,.contact-delete,.position-section-toggle)):enabled:active{transform:translateY(2px);filter:brightness(.88);box-shadow:0 1px 2px rgba(15,23,42,.16)}
      :is(.tab,.contact-edit,.settlement-exit-button):is(:hover,:focus-visible){color:var(--nic-green)}
      :is(.tab,.contact-delete):is(:hover,:focus-visible){text-shadow:0 -2px 5px color-mix(in srgb,currentColor 35%,transparent)}
      @media(prefers-reduced-motion:reduce){button{transition:none}button:not(:is(.tab,.contact-edit,.settlement-exit-button,.contact-delete,.position-section-toggle)):enabled:active{transform:none}}
    `;
    root.innerHTML = markup;
    root.prepend(style);
    const exit = document.createElement('button');
    exit.type = 'button';
    exit.className = 'settlement-exit-button';
    exit.innerHTML = '<span aria-hidden="true">←</span> Abrechnung verlassen';
    exit.addEventListener('click', () => {
      const landing = new URL(location.href);
      landing.searchParams.delete('modus');
      landing.hash = '';
      location.assign(landing.href);
    });
    const exitActions = document.createElement('div');
    exitActions.className = 'settlement-exit';
    exitActions.append(exit);
    root.querySelector('.tabs').before(exitActions);
    style.textContent += `
      #abrechnung > .page-head{display:flex;flex-direction:row;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:10px 16px}
      #abrechnung > .page-head > div:first-child{flex:1 1 210px;min-width:0}
      #abrechnung > .page-head .actions{display:flex;flex:0 1 416px;flex-wrap:nowrap;justify-content:flex-end;align-items:center;margin-inline-start:auto;min-width:0;max-width:100%;gap:8px}
      #abrechnung > .page-head .actions > .btn{flex:1 1 0;width:204px;min-width:0;max-width:204px;min-height:38px;white-space:nowrap;text-align:center}
      .settlement-draft-status{color:var(--nic-muted);font-size:var(--nic-subtext-font-size);text-align:right;margin:0 0 10px}
      .settlement-draft-status:empty{display:none}
      @container (max-width:520px){
        #abrechnung > .page-head .actions{width:100%;flex:0 1 100%;gap:4px}
        #abrechnung > .page-head .actions > .btn{width:auto;padding-inline:4px;font-size:clamp(10px,2.7cqi,13px)}
      }
      :is(#kontakte,#objekte) > .page-head{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:start;gap:10px 16px}
      :is(#kontakte,#objekte) > .page-head > div:first-child{min-width:0}
      :is(#kontakte,#objekte) > .page-head > .actions{justify-self:end;justify-content:flex-end;flex-wrap:nowrap;margin:0}
      :is(#addContact,#addObject){white-space:nowrap;min-height:38px}
      @container (max-width:420px){
        :is(#kontakte,#objekte) > .page-head{column-gap:8px}
        :is(#addContact,#addObject){padding-inline:8px;font-size:clamp(11px,3.2cqi,14px)}
      }
      :is(#einheiten,#schluessel) > .page-head{flex-direction:row;flex-wrap:wrap;align-items:flex-start;justify-content:space-between;gap:10px 16px}
      :is(#einheiten,#schluessel) > .page-head > div:first-child{flex:1 1 180px;min-width:0}
      .object-header-actions{display:flex;flex:0 1 auto;justify-content:flex-end;align-items:center;margin-inline-start:auto;max-width:100%;gap:8px}
      .object-header-actions .object-switcher{margin:0;min-width:0;max-width:100%}
      .object-header-actions .object-switcher select{width:204px;max-width:100%;min-width:0}
      .object-header-actions .btn{white-space:nowrap;min-height:46px}
      @container (max-width:520px){
        .object-header-actions{flex-wrap:wrap}
      }
      .settlement-exit{padding:10px 20px 0}
      .settlement-exit-button,.add-rent-period{border:0;background:transparent;text-decoration:none;cursor:pointer;text-align:left}
      .settlement-exit-button{display:inline-flex;align-items:center;gap:8px;padding:6px 0;color:var(--nic-ink);font-size:max(16px,var(--nic-body-font-size));font-weight:700}
      .settlement-exit-button span{font-size:1.25em;line-height:1}
      .settlement-exit-button:focus-visible{outline:2px solid currentColor;outline-offset:3px}
      #abrechnung .wizard-panel{height:auto;min-height:0}
      .billing-group{border:1px solid var(--nic-border);border-radius:12px;padding:0 12px;margin-bottom:10px;min-width:0}
      .billing-group summary{display:flex;align-items:center;gap:8px;width:100%;list-style:none;padding:10px 0;font-weight:700;cursor:pointer}
      .billing-group summary::-webkit-details-marker{display:none}
      .billing-group summary::after{content:'+';margin-inline-start:auto;flex:none;color:var(--nic-green)}
      .billing-group[open] summary::after{content:'−'}
      .billing-group > :not(summary){margin-bottom:12px}
      .billing-group .field{min-width:0}
      #abrechnung .wizard-panel[data-panel="1"] .billing-unit-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
      .billing-unit-grid .field{min-width:0}
      .billing-object-grid{display:grid;gap:12px;min-width:0}
      .billing-object-row{display:grid;gap:12px;min-width:0}
      .billing-object-row-1{grid-template-columns:minmax(0,1fr)}
      .billing-object-row-2{grid-template-columns:repeat(2,minmax(0,1fr))}
      .billing-object-row-3{grid-template-columns:repeat(3,minmax(0,1fr))}
      .billing-object-row .field{min-width:0}
      .billing-object-row input,.billing-object-row select{width:100%;min-width:0}
      #objectDetailPanel .form-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
      #objectDetailPanel .object-contact-first{grid-column:1}
      #objectDetailPanel .field{min-width:0}
      .contact-detail-group:first-of-type{margin-top:16px}
      .contact-detail-group summary:focus-visible{outline:2px solid var(--nic-green);outline-offset:2px}
      .billing-contact-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 12px;margin:10px 0;overflow-wrap:anywhere}
      .billing-contact-fields dt{font-size:var(--nic-subtext-font-size);color:var(--nic-muted)}
      .billing-contact-fields dd{margin:0}
      #abrechnung .wizard-panel[data-panel="2"] .position-table-wrap{overflow:visible;max-height:none;container-type:inline-size}
      .position-table{min-width:0}
      .position-table th{overflow-wrap:anywhere;font-size:var(--nic-subtext-font-size)}
      .position-table .group-row td{padding:0;background:#eef0f2;border-radius:12px;overflow:hidden}
      .position-table .subtotal-row td:first-child{border-radius:12px 0 0 12px}
      .position-table .subtotal-row td:last-child{border-radius:0 12px 12px 0}
      .position-balance-panel{border-radius:12px;background:#eef0f2;padding:10px 12px;margin-block:10px}
      .position-balance-panel summary{border-radius:12px;cursor:pointer}
      .position-money-cell{position:relative}
      .position-money-cell::after{content:'€';position:absolute;right:17px;bottom:21px;color:var(--nic-muted);pointer-events:none;font-size:13px}
      .position-money-cell .review-input{padding-inline-end:24px;text-align:right}
      @container (max-width:720px){
        .position-table .subtotal-row{border-radius:12px;overflow:hidden;background:#f8faf9}
        .position-money-cell::after{right:11px;bottom:20px}
      }
      /* Match the 10px gap between the accordion groups in the details step. */
      .position-table{border-spacing:0 10px}
      @container (max-width:720px){
        .position-table .group-row{margin-bottom:10px}
      }
      .position-section-toggle{border-radius:12px}
      #abrechnung :is(button[data-add-position],#addReviewPosition){
        box-sizing:border-box;display:inline-flex;justify-content:flex-start;align-items:center;
        width:300px;max-width:100%;min-height:42px;white-space:normal;text-align:left;
        background:#f6c944;border-color:#e1b52b;color:#302600;
      }
      #abrechnung :is(button[data-add-position],#addReviewPosition):hover{background:#edbd2f}
      #abrechnung .position-table .add-row td{padding-inline:0}
      #abrechnung #positionModeHint[hidden]{display:none!important}
      .position-section-toggle{display:flex;align-items:center;justify-content:space-between;gap:12px;width:100%;border:0;background:transparent;color:inherit;font:inherit;text-align:left;padding:12px 10px;cursor:pointer;box-shadow:none}
      .position-section-toggle span:first-child{min-width:0;overflow-wrap:anywhere}
      .position-section-symbol{margin-inline-start:auto;flex:none;font-size:1.2em;line-height:1;color:var(--nic-green)}
      .position-section-symbol::before{content:'+'}
      .position-section-toggle[aria-expanded="true"] .position-section-symbol::before{content:'−'}
      .position-section-toggle:focus-visible{outline:2px solid var(--nic-green);outline-offset:-2px}
      #positionTemplateBody.collapsed-umlagefaehig > :is([data-category="umlagefaehig"],[data-subtotal="umlagefaehig"],[data-position-section="umlagefaehig"]),
      #positionTemplateBody.collapsed-nicht_umlagefaehig > :is([data-category="nicht_umlagefaehig"],[data-subtotal="nicht_umlagefaehig"],[data-position-section="nicht_umlagefaehig"]),
      #positionTemplateBody.collapsed-ruecklage > :is([data-category="ruecklage"],[data-subtotal="ruecklage"],[data-position-section="ruecklage"]),
      #positionTemplateBody.collapsed-einnahmen > :is([data-category="einnahmen"],[data-subtotal="einnahmen"],[data-position-section="einnahmen"]){display:none!important}
      .position-table thead th{position:static;vertical-align:top}
      .position-table .review-input{max-width:100%}
      @container (max-width:720px){
        .position-table,.position-table tbody{display:block}
        .position-table thead{position:absolute;width:1px;height:1px;clip-path:inset(50%);overflow:hidden}
        .position-table tr{display:block;margin-bottom:8px}
        .position-table td{display:block}
        .position-table td:empty{display:none}
        .position-table .review-position-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px;border:1px solid var(--nic-border);border-radius:8px;padding:6px}
        .position-table .review-position-row td{min-width:0;border:0}
        .position-table .review-position-row td:not(:empty)::before{content:attr(data-label);display:block;color:var(--nic-muted);overflow-wrap:anywhere}
        .position-table .subtotal-total::before,.position-table .grand-total::before{content:'Gesamtbetrag: '}
        .position-table .subtotal-share::before,.position-table .grand-share::before{content:'Ihr Betrag: '}
      }
      @media screen{
        .preview-overlay{position:static;z-index:auto;background:transparent;overflow:visible;padding:14px 0;scroll-margin-top:80px}
        .preview-toolbar{color:var(--nic-ink);flex-wrap:wrap;gap:8px}
        .preview-toolbar > div,.preview-modes{display:flex;gap:8px;flex-wrap:wrap}
        .a4-page{max-width:100%;overflow:visible;overflow-wrap:anywhere}
        .a4-table .num{white-space:normal}
      }
      /* Shared control dimensions, including native iOS Safari selects. */
      :host{--nic-field-height:max(46px,calc(1.5em + 22px));--nic-review-field-height:40px;--nic-next-width:19em}
      .field input:not([type=checkbox]):not([type=radio]):not([type=file]):not([type=hidden]),.field select,.object-switcher select,
      #abrechnung .wizard-panel[data-panel="1"] .field input:not([type=checkbox]):not([type=radio]):not([type=file]):not([type=hidden]),
      #abrechnung .wizard-panel[data-panel="1"] .field select{
        box-sizing:border-box;height:var(--nic-field-height);min-height:var(--nic-field-height);padding:10px 12px;
        font:inherit;line-height:1.5;min-width:0;
      }
      select.field,.field select,.object-switcher select,select.review-input{
        appearance:none;-webkit-appearance:none;
        background-color:#fff;
        background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'%3E%3Cpath d='M4 6l4 4 4-4' fill='none' stroke='%23596674' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
        background-repeat:no-repeat;background-position:right 10px center;background-size:16px;
        padding-inline-end:32px;
      }
      #abrechnung .wizard-panel[data-panel="1"] .field select{padding-inline-end:32px}
      .review-input{box-sizing:border-box;height:var(--nic-review-field-height);min-height:var(--nic-review-field-height);line-height:1.5}
      select.review-input{padding-inline-end:30px}
      .wizard-panel .step-heading{flex-wrap:wrap}
      .step-heading-actions{justify-content:flex-end;flex-wrap:wrap;min-width:0;max-width:100%;margin-inline-start:auto}
      .step-heading-actions .back-step{border:0;background:transparent;box-shadow:none}
      .step-heading-actions .back-step:focus-visible{outline:2px solid var(--nic-green);outline-offset:2px}
      .wizard-panel .step-heading button[data-next],.wizard-panel .step-heading #showPreview{
        box-sizing:border-box;width:var(--nic-next-width);min-width:0;max-width:100%;flex:0 0 auto;
        min-height:44px;margin-inline-start:auto;align-self:flex-end;white-space:normal;
      }
      @container (max-width:900px){
        .step-heading-actions{width:100%}
        .wizard-panel .step-heading button[data-next],.wizard-panel .step-heading #showPreview{width:min(100%,var(--nic-next-width))}
      }
      @media(max-width:600px){
        .field input:not([type=checkbox]):not([type=radio]):not([type=file]),.field select,.object-switcher select,.review-input,
        #abrechnung .wizard-panel[data-panel="1"] .field input:not([type=checkbox]):not([type=radio]):not([type=file]),
        #abrechnung .wizard-panel[data-panel="1"] .field select{font-size:16px}
      }
      .input-with-unit{position:relative;width:100%;min-width:0}
      .input-with-unit::after{content:attr(data-unit);position:absolute;inset-inline-end:12px;top:50%;transform:translateY(-50%);color:var(--nic-muted);font-size:var(--nic-subtext-font-size);line-height:1;pointer-events:none}
      .field .input-with-unit input,#abrechnung .wizard-panel[data-panel="1"] .field .input-with-unit input{padding-inline-end:48px}
      .input-with-unit input[type=number]{appearance:textfield;-moz-appearance:textfield}
      .input-with-unit input[type=number]::-webkit-inner-spin-button,.input-with-unit input[type=number]::-webkit-outer-spin-button{-webkit-appearance:none;margin:0}
      /* One shared size for all top-level menu header action buttons. */
      :host{--nic-header-action-width:204px;--nic-header-action-height:46px;--nic-header-action-font:var(--nic-subtext-font-size)}
      #kontakte > .page-head > .actions > .btn,
      #objekte > .page-head > .actions > .btn,
      #einheiten > .page-head > .actions > .btn,
      #schluessel > .page-head > .actions > .btn,
      #einstellungen > .page-head > .actions > .btn,
      #abrechnung > .page-head > .actions > .btn{
        box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center;
        flex:0 0 var(--nic-header-action-width);width:var(--nic-header-action-width);min-width:0;max-width:var(--nic-header-action-width);
        height:var(--nic-header-action-height);min-height:var(--nic-header-action-height);
        padding:8px 6px;font-size:var(--nic-header-action-font);white-space:nowrap;text-align:center;
      }
      #abrechnung > .page-head > .actions{flex-basis:calc(2 * var(--nic-header-action-width) + 8px)}
      @container (max-width:520px){
        :host{--nic-header-action-width:min(204px,calc((100cqi - 76px)/2));--nic-header-action-font:clamp(10px,2.7cqi,14px)}
        #abrechnung > .page-head > .actions{flex-basis:100%;gap:4px}
        :is(#kontakte,#objekte,#einheiten,#schluessel,#einstellungen,#abrechnung) > .page-head > .actions > .btn{padding-inline:3px}
      }
      .step-heading h3[tabindex="-1"]:focus{outline:none}
      #tenantDetails{margin-block-start:16px}
      #tenantDetails .form-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
      #tenantDetails .field,#tenantDetails .field input{min-width:0}
      #tenantDetails .field > span{display:block;font-size:var(--nic-subtext-font-size);color:#596674;margin-bottom:5px}
      #tenantActive{width:auto;min-height:0;margin-inline-end:4px}
      .tenant-rent-period{position:relative;border:1px solid var(--nic-border);border-radius:12px;margin:0 0 12px;padding:12px;min-width:0}
      .tenant-rent-period legend{font-weight:650;padding:0 4px}
      .rent-period-delete{position:absolute;top:-12px;right:8px;background:var(--nic-card,#fff)}
      .add-rent-period{justify-self:start;padding:6px 0;color:var(--nic-green);font-size:var(--nic-subtext-font-size);font-weight:650}
      @media(max-width:600px){
        .settlement-exit{padding-inline:10px}
        #tenantDetails .form-grid{grid-template-columns:minmax(0,1fr)}
      }
    `;

    if (!document.getElementById('settlement-print-style')) {
      const printStyle = document.createElement('style');
      printStyle.id = 'settlement-print-style';
      printStyle.textContent = `
        @media screen {
          #nicContentView:has(> [data-settlement]) {
            background: #fff;
            min-height: max(520px, calc(100dvh - 360px));
          }
        }
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
    const startManual = initialize(root, () => {
      document.body.classList.add('settlement-printing');
      window.addEventListener('afterprint', () => document.body.classList.remove('settlement-printing'), {once:true});
      window.print();
    });
    savedWorkspace = workspace;
    placeWorkspace(host, workspace);
    if (mode === 'manuell') {
      const layoutReady = window.NICInitialLayout?.ready;
      startManual(!layoutReady);
      // The shared shell is hidden until its settings and layout have been applied.
      layoutReady?.then(() => {
        if (workspace.isConnected && document.activeElement === document.body) startManual();
      });
    }
  }
  function boot() {
    mount();
    window.addEventListener('nic-route-changed', mount);
    new MutationObserver(mount).observe(document.body, {childList: true, subtree: true});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, {once: true});
  else boot();
})();
