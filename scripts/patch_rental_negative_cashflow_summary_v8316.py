from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

old="""    const recommendation=(()=>{
      if(!(m.purchase>0&&m.coldRent>0)){
        return 'Trage Kaufpreis, Nettokaltmiete, laufende Kosten und Finanzierung vollständig ein. Erst dann lassen sich Cashflow, Rendite und Kaufpreisfaktor sinnvoll einordnen.';
      }
      const cashRatio=m.coldRent>0?m.cashflow/m.coldRent:0;
      if(m.cashflow>=0 && m.factor!=null && m.factor<=25){
        return 'Die Vermietung wirkt auf Basis deiner Eingaben solide: Der laufende Cashflow ist positiv und der Kaufpreisfaktor liegt in einem attraktiven bis soliden Bereich. Prüfe trotzdem Mietansatz, Hausgeld, Instandhaltungsbedarf und Finanzierung anhand der Objektunterlagen.';
      }
      if(cashRatio>=-.10 && m.factor!=null && m.factor<=30){
        return 'Die Kalkulation liegt im prüfenswerten Bereich. Cashflow beziehungsweise Kaufpreisfaktor bieten noch keinen großen Sicherheitspuffer. Prüfe insbesondere nicht umlagefähige Kosten, Instandhaltung, realistische Miete und mögliche Zinsänderungen.';
      }
      return 'Die Vermietung wirkt mit den aktuellen Annahmen eher angespannt. Ein hoher Kaufpreisfaktor oder negativer Cashflow kann den laufenden Ertrag deutlich belasten. Prüfe Kaufpreis, Finanzierung, Miete und Eigentümerkosten erneut, bevor du die Immobilie wirtschaftlich bewertest.';
    })();
"""

new="""    const recommendation=(()=>{
      if(!(m.purchase>0&&m.coldRent>0)){
        return 'Trage Kaufpreis, Nettokaltmiete, laufende Kosten und Finanzierung vollständig ein. Erst dann lassen sich Cashflow, Rendite und Kaufpreisfaktor sinnvoll einordnen.';
      }

      const cashRatio=m.coldRent>0?m.cashflow/m.coldRent:0;
      let base='';

      if(m.cashflow>=0 && m.factor!=null && m.factor<=25){
        base='Die Vermietung wirkt auf Basis deiner Eingaben solide: Der laufende Cashflow ist positiv und der Kaufpreisfaktor liegt in einem attraktiven bis soliden Bereich. Prüfe trotzdem Mietansatz, Hausgeld, Instandhaltungsbedarf und Finanzierung anhand der Objektunterlagen.';
      }else if(cashRatio>=-.10 && m.factor!=null && m.factor<=30){
        base='Die Kalkulation liegt im prüfenswerten Bereich. Cashflow beziehungsweise Kaufpreisfaktor bieten noch keinen großen Sicherheitspuffer. Prüfe insbesondere nicht umlagefähige Kosten, Instandhaltung, realistische Miete und mögliche Zinsänderungen.';
      }else{
        base='Die Vermietung wirkt mit den aktuellen Annahmen eher angespannt. Ein hoher Kaufpreisfaktor oder negativer Cashflow kann den laufenden Ertrag deutlich belasten. Prüfe Kaufpreis, Finanzierung, Miete und Eigentümerkosten erneut, bevor du die Immobilie wirtschaftlich bewertest.';
      }

      if(m.cashflow<0){
        let actual='';
        if(cashRatio>=-.05){
          actual='Dein aktueller Wert liegt im Bereich leicht negativ bis etwa -5 % der Nettokaltmiete.';
        }else if(cashRatio>=-.10){
          actual='Dein aktueller Wert liegt im angespannten Bereich von etwa -5 bis -10 % der Nettokaltmiete.';
        }else{
          actual='Dein aktueller Wert liegt mehr als -10 % unter der Nettokaltmiete und ist aus Cashflow-Sicht kritisch.';
        }

        const guide=
          ' Ein negativer Cashflow bei Vermietung ist nicht automatisch ein Ausschlusskriterium, aber er bedeutet ganz schlicht: Die Immobilie trägt sich aus der laufenden Vermietung nicht selbst. Du musst jeden Monat eigenes Geld zuschießen. '
          +actual
          +' Einordnung: 0 € oder positiv: laufend solide, sofern Rücklagen und Kosten realistisch angesetzt sind. '
          +'Leicht negativ, bis etwa -5 % der Nettokaltmiete: oft noch vertretbar, wenn Tilgung, AfA, Mietsteigerungspotenzial oder eine sehr gute Lage dagegenstehen. '
          +'Ca. -5 bis -10 % der Nettokaltmiete: angespannt; hier sollte es einen klaren Grund geben, warum du den Zuschuss akzeptierst. '
          +'Mehr als -10 % der Nettokaltmiete: für einen normalen Kapitalanleger aus Cashflow-Sicht kritisch. '
          +'Dauerhaft deutlich negativ ist besonders problematisch, wenn gleichzeitig Kaufpreisfaktor und Instandhaltung hoch sowie das Mietsteigerungspotenzial gering sind.';
        return base+guide;
      }

      return base;
    })();
"""

if old not in s:
    raise SystemExit("rental recommendation anchor missing")
s=s.replace(old,new,1)

old_box="""    drawInfoBox('',recommendation,{fill:[239,246,255],stroke:[191,219,254],bodySize:8.4,fixedHeight:34,padding:4});"""
new_box="""    drawInfoBox('',recommendation,{
      fill:[239,246,255],
      stroke:[191,219,254],
      bodySize:m.cashflow<0?7.4:8.4,
      fixedHeight:m.cashflow<0?64:34,
      padding:4
    });"""
if old_box not in s:
    raise SystemExit("rental summary box anchor missing")
s=s.replace(old_box,new_box,1)

s=s.replace("V8.315","V8.316")
s=s.replace("service-worker.js?v=8.315","service-worker.js?v=8.316")

required=[
  "Ein negativer Cashflow bei Vermietung ist nicht automatisch ein Ausschlusskriterium",
  "Du musst jeden Monat eigenes Geld zuschießen.",
  "bis etwa -5 % der Nettokaltmiete",
  "etwa -5 bis -10 % der Nettokaltmiete",
  "Mehr als -10 % der Nettokaltmiete",
  "Tilgung, AfA, Mietsteigerungspotenzial",
  "m.cashflow<0?64:34",
  "V8.316",
  "service-worker.js?v=8.316"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.316 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.316 negative rental cashflow summary guidance applied")
