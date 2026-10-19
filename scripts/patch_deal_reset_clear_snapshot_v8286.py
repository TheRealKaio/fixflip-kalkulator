from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old='''function resetDealCalculatorToDefaults(){
  const mode=currentDealType();'''
new='''function resetDealCalculatorToDefaults(){
  const mode=currentDealType();

  // V8.286: Auch den getrennten Modus-Snapshot löschen.
  // Sonst kann ein Browser-Reload nach dem Reset alte Nutzereingaben erneut herstellen.
  try{
    const modeSnapshotPrefix="ff_mode_snapshot_v8237_";
    localStorage.removeItem(modeSnapshotPrefix+mode);
  }catch(_err){}'''

if old not in s:
    raise SystemExit("V8.286 reset function anchor missing")
s=s.replace(old,new,1)

# After reset and render, persist a fresh snapshot of the reset state.
old_tail='''  render();
  initializeReferenceInterest();
}'''
new_tail='''  render();

  // Frischen Snapshot aus den gerade gesetzten Standardwerten schreiben.
  try{
    const modeSnapshotPrefix="ff_mode_snapshot_v8237_";
    const root=document.getElementById("dealCalculatorContent");
    if(root){
      const controls=Array.from(root.querySelectorAll("input,select,textarea"))
        .filter(el=>el.name!=="dealType");
      const payload={
        version:"v8237",
        mode,
        savedAt:Date.now(),
        controls:controls.map((el,index)=>({
          index,
          id:el.id || "",
          value:el.value,
          checked:!!el.checked,
          selectedIndex:typeof el.selectedIndex==="number" ? el.selectedIndex : null,
          type:(el.type || "").toLowerCase(),
          tag:el.tagName
        }))
      };
      localStorage.setItem(modeSnapshotPrefix+mode,JSON.stringify(payload));
    }
  }catch(_err){}

  initializeReferenceInterest();
}'''

if old_tail not in s:
    raise SystemExit("V8.286 reset function tail anchor missing")
s=s.replace(old_tail,new_tail,1)

s=s.replace("V8.285","V8.286")
s=s.replace("service-worker.js?v=8.285","service-worker.js?v=8.286")

required=[
    'localStorage.removeItem(modeSnapshotPrefix+mode);',
    'localStorage.setItem(modeSnapshotPrefix+mode,JSON.stringify(payload));',
    'version:"v8237"',
    'V8.286',
    'service-worker.js?v=8.286'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.286 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.286 deal reset clears and rebuilds active mode snapshot")
