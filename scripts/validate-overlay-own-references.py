#!/usr/bin/env python3
"""Check integrity of a precompiled DTBO's own fixup references.
This is a read-only audit; outputs are NOT flashable.
"""
import argparse, pathlib, re, subprocess
p=argparse.ArgumentParser()
p.add_argument("overlay")
p.add_argument("--report",required=True)
a=p.parse_args()
def run(*args):
    return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
s=run("dtc","-I","dtb","-O","dts",a.overlay)
if s.returncode: raise SystemExit(s.stderr)
def section(name):
    m=re.search(r"\b"+name+r"\s*\{(.*?)\n\s*\};",s.stdout,re.S)
    if not m: return {}
    return dict(re.findall(r'^\s*([\w,.-]+)\s*=\s*"([^"]*)";',m.group(1),re.M))
errors=[]
nfix=0
for label,refs in section("__fixups__").items():
    for ref in refs.split(r"\0"):
        if not ref:continue
        nfix+=1
        try: node,prop,offset=ref.rsplit(":",2)
        except ValueError:
            errors.append("MALFORMED fixup "+label+" -> "+ref);continue
        if run("fdtget","-p",a.overlay,node).returncode:
            errors.append("MISSING fixup node "+label+" -> "+node)
        elif run("fdtget","-t","x",a.overlay,node,prop).returncode:
            errors.append("MISSING fixup property "+label+" -> "+node+":"+prop)
nsym=0
for label,path in section("__symbols__").items():
    nsym+=1
    if run("fdtget","-p",a.overlay,path).returncode:
        errors.append("MISSING overlay symbol path "+label+" -> "+path)
report=[f"Overlay: {pathlib.Path(a.overlay).name}",f"Fixup entries: {nfix}",f"Overlay symbols: {nsym}",f"Invalid own overlay references: {len(errors)}",*errors[:75]]
pathlib.Path(a.report).write_text("\n".join(report)+"\n")
print("\n".join(report))
