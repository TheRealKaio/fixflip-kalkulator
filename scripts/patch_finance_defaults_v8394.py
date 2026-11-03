"""V8.394: financing defaults, blank renovation buffers and reset parity."""
from pathlib import Path
import re,sys
path=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=path.read_text(encoding="utf-8")
replacements={
 'savedOwn !== null ? savedOwn : "60"':'savedOwn !== null ? savedOwn : "120"',
 'months:"60"':'months:"120"',
 'localStorage.setItem("ff_own_months","60");':'localStorage.setItem("ff_own_months","120");',
 'buffer:"5"':'buffer:""',
 'const currentBuffer="0";':'const currentBuffer="";',
 'String(currentBuffer||"0")':'String(currentBuffer)',
 'String(bufferInput.value||"0")':'String(bufferInput.value)',
 '$("buffer").value="0";':'$("buffer").value="";',
 'stateKey(currentMode,"buffer"),"0"':'stateKey(currentMode,"buffer"),""',
 'b===null?"0.00":b':'b===null?"":b',
 "$r('rentRenoBuffer').value='0.00'":"$r('rentRenoBuffer').value=''",
}
for old,new in replacements.items():
 if old not in s:raise SystemExit("Finance default anchor missing: "+old)
 s=s.replace(old,new)
s,n=re.subn(r'(<input\b[^>]*\bid="(?:buffer|rentRenoBuffer)"[^>]*\bvalue=")[^"]*(")',r'\1\2',s)
if n!=2:raise SystemExit("Expected both renovation buffer inputs")
old='function formatPercentInputField(el){\n  if(!el) return;'
new=old+'\n  if(["buffer","rentRenoBuffer"].includes(el.id)&&parseLocalizedNumber(el.value,true)===0){el.value="";return;}'
if old not in s:raise SystemExit("Percentage formatter anchor missing")
s=s.replace(old,new,1)
s=s.replace("</head>","<script id=\"nic-finance-defaults-v8394\">\n(function(){\n const key=\"ff_finance_defaults_v8394\";\n if(localStorage.getItem(key)===\"1\")return;\n const months=localStorage.getItem(\"ff_own_months\");\n if(months===null||Number(months)===60)localStorage.setItem(\"ff_own_months\",\"120\");\n for(const name of [\"ff_buffer\",\"ff_own_reno_buffer\",\"ff_flip_reno_buffer\",\"ff_rent_reno_buffer\"]){\n  const value=localStorage.getItem(name);\n  if(value===null||Number(value)===0||Number(value)===5)localStorage.setItem(name,\"\");\n }\n for(const mode of [\"own\",\"flip\"]){\n  const name=\"ff_mode_snapshot_v8237_\"+mode;\n  try{\n   const snapshot=JSON.parse(localStorage.getItem(name)||\"null\");\n   if(snapshot?.controls){\n    for(const item of snapshot.controls){\n     if(mode===\"own\"&&item.id===\"months\"&&Number(item.value)===60)item.value=\"120\";\n     if(item.id===\"buffer\"&&[0,5].includes(Number(item.value)))item.value=\"\";\n    }\n    localStorage.setItem(name,JSON.stringify(snapshot));\n   }\n  }catch(_){}\n }\n localStorage.setItem(key,\"1\");\n})();\n</script>"+"</head>",1)
path.write_text(s,encoding="utf-8")
print("V8.394 financing defaults and resets: 120 months, empty buffers")
