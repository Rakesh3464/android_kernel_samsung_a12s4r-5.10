#!/usr/bin/env python3
"""Read-only diagnostic of unresolved DTBO external labels in a base DTB.
Not a kernel port or safe flash artifact.
"""
import argparse, subprocess, pathlib, re, sys
p=argparse.ArgumentParser()
p.add_argument("base")
p.add_argument("overlays", nargs="+")
p.add_argument("--report", required=True)
a=p.parse_args()
def labels(dtbo, section):
    text=subprocess.check_output(["dtc","-I","dtb","-O","dts",dtbo],text=True,stderr=subprocess.DEVNULL)
    m=re.search(r'\b'+re.escape(section)+r'\s*\{(.*?)\n\s*\};',text,re.S)
    if not m: return set()
    return set(re.findall(r'^\s*([A-Za-z_][\w,.-]*)\s*=',m.group(1),re.M))
base=labels(a.base,"__symbols__")
out=[f"Base DTB exports {len(base)} symbols. Missing fixup symbols are an unresolved overlay ABI problem, NOT evidence of hardware boot readiness."]
for ov in a.overlays:
    needed=labels(ov,"__fixups__")
    missing=sorted(needed-base)
    out.extend([f"\n{pathlib.Path(ov).name}: needs={len(needed)}, missing={len(missing)}",
                "Missing: "+(", ".join(missing) if missing else "(none)")])
    print(out[-2]);print(out[-1])
path=pathlib.Path(a.report);path.parent.mkdir(parents=True,exist_ok=True);path.write_text("\n".join(out)+"\n")
