#!/usr/bin/env python3
"""Report *effective* DTBO fixup targets in an actual base DTB. Read-only."""
import argparse
import pathlib
import re
import subprocess
p=argparse.ArgumentParser()
p.add_argument("base")
p.add_argument("overlays",nargs="+")
p.add_argument("--report",required=True)
a=p.parse_args()
def run(*args):
    return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
def dtc_text(file):
    q=run("dtc","-I","dtb","-O","dts",file)
    if q.returncode: raise RuntimeError(q.stderr[:800])
    return q.stdout
def section(text, name):
    # Dtc output section key-value properties have one indentation level.
    m=re.search(r"\b"+re.escape(name)+r"\s*\{(.*?)\n\s*\};",text,re.S)
    return {} if not m else dict(re.findall(r'^\s*([\w,.-]+)\s*=\s*"([^"]*)";',m.group(1),re.M))
base=section(dtc_text(a.base),"__symbols__")
out=[f"Base symbols: {len(base)}"]
bad_total=0
for ov in a.overlays:
    req=section(dtc_text(ov),"__fixups__")
    missing=sorted(set(req)-set(base))
    dangling=[]
    no_phandle=[]
    phandle_read_error=[]
    for sym in sorted(set(req)&set(base)):
        path=base[sym]
        if run("fdtget","-p",a.base,path).returncode:
            dangling.append((sym,path))
            continue
        ph=run("fdtget","-t","x",a.base,path,"phandle")
        linux_ph=run("fdtget","-t","x",a.base,path,"linux,phandle")
        if ph.returncode and linux_ph.returncode:
            no_phandle.append((sym,path))
        elif ph.returncode == 0 and not ph.stdout.strip():
            phandle_read_error.append((sym,path))
    lines=[f"\n{pathlib.Path(ov).name}: fixup_labels={len(req)} missing_labels={len(missing)} dangling_base_paths={len(dangling)} missing_node_phandles={len(no_phandle)}",
           "MISSING: "+(", ".join(missing) if missing else "(none)")]
    lines += [f"DANGLING: {name} -> {target}" for name,target in dangling]
    lines += [f"NO_PHANDLE: {name} -> {target}" for name,target in no_phandle]
    lines += [f"EMPTY_PHANDLE: {name} -> {target}" for name,target in phandle_read_error]
    out.extend(lines)
    bad_total+=len(missing)+len(dangling)
pathlib.Path(a.report).write_text("\n".join(out)+"\n")
print("\n".join(out))
