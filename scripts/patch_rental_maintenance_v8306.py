from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# Zusätzliche Instandhaltung: 1,50 €/m² in den Info-Kreis,
# automatisch als Standard berechnen, aber editierbar lassen.
old_info='''data-info="Monatliche Rücklage für Reparaturen und Instandhaltung zusätzlich zu bereits im Hausgeld enthaltenen Beträgen."'''
new_info='''data-info="Kalkulatorischer Vorschlag: 1,50 € pro m² Wohnfläche und Monat. Der Wert dient als Richtwert und kann individuell angepasst werden."'''
rep(old_info,new_info,"maintenance info")

old_hint='''            <div class="mini">pro Monat · zusätzlich zum nicht umlagefähigen Hausgeld</div>
            <div class="mini" id="rentMaintenanceSuggestion">Vorschlag: ca. 1,00 €/m² Wohnfläche/Monat</div>'''
new_hint='''            <div class="mini" id="rentMaintenanceStatus">pro Monat · kalkulatorischer Vorschlag</div>'''
rep(old_hint,new_hint,"maintenance field hint")

script=r'''
<script id="rental-ui-script-v8306">
(function(){
  const area=document.getElementById("rentArea");
  const maintenance=document.getElementById("rentMaintenance");
  const status=document.getElementById("rentMaintenanceStatus");
  if(!area || !maintenance || !status) return;

  const MANUAL_KEY="ff_rent_maintenance_manual";
  const VALUE_KEY="ff_rent_rentMaintenance";
  let syncing=false;

  const num=v=>{
    let x=String(v??"").trim().replace(/\s/g,"");
    if(x.includes(",")&&x.includes(".")){
      x=x.lastIndexOf(",")>x.lastIndexOf(".")
        ?x.replace(/\./g,"").replace(",",".")
        :x.replace(/,/g,"");
    }else{
      x=x.replace(",",".");
    }
    x=x.replace(/[^0-9.-]/g,"");
    const n=Number(x);
    return Number.isFinite(n)?n:0;
  };

  const isManual=()=>localStorage.getItem(MANUAL_KEY)==="1";

  const setStatus=()=>{
    status.textContent=isManual()
      ?"pro Monat · geänderter Vorschlag"
      :"pro Monat · kalkulatorischer Vorschlag";
  };

  const applyCalculated=()=>{
    if(isManual()) {
      setStatus();
      return;
    }
    const sqm=Math.max(0,num(area.value));
    const calculated=Math.round(sqm*1.5*100)/100;
    syncing=true;
    maintenance.value=String(calculated);
    localStorage.setItem(VALUE_KEY,String(calculated));
    maintenance.dispatchEvent(new Event("input",{bubbles:true}));
    maintenance.dispatchEvent(new Event("change",{bubbles:true}));
    syncing=false;
    setStatus();
  };

  area.addEventListener("input",applyCalculated);

  maintenance.addEventListener("input",()=>{
    if(syncing) return;
    localStorage.setItem(MANUAL_KEY,"1");
    localStorage.setItem(VALUE_KEY,String(num(maintenance.value)));
    setStatus();
  });

  // Bestehende Altwerte gelten nur dann als manuell, wenn der Nutzer sie ab jetzt ändert.
  // Ohne manuellen Marker wird der kalkulatorische Standard aus der Wohnfläche gesetzt.
  applyCalculated();
})();
</script>
'''
rep("</body>",script+"\n</body>","body script")

s=s.replace("V8.305","V8.306")
s=s.replace("service-worker.js?v=8.305","service-worker.js?v=8.306")

required=[
  'id="rental-ui-script-v8306"',
  'id="rentMaintenanceStatus"',
  'pro Monat · kalkulatorischer Vorschlag',
  'pro Monat · geänderter Vorschlag',
  '1,50 € pro m² Wohnfläche und Monat',
  'ff_rent_maintenance_manual',
  'sqm*1.5',
  "V8.306",
  "service-worker.js?v=8.306"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.306 missing: "+", ".join(missing))

if 'id="rentMaintenanceSuggestion"' in s:
    raise SystemExit("V8.306 old visible maintenance suggestion still present")
if 'zusätzlich zum nicht umlagefähigen Hausgeld' in s:
    raise SystemExit("V8.306 old maintenance wording still present")

p.write_text(s,encoding="utf-8")
print("V8.306 maintenance default and manual override applied")
