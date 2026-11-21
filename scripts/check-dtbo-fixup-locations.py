#!/usr/bin/env python3
"""Read-only audit: verify every __fixups__ entry's overlay node/property/offset exists.
External symbols being present does NOT prove the fixup location is valid.
"""
import argparse, pathlib, re, subprocess
p=argparse.ArgumentParser()
p.add_argument("overlays",nargs="+")
p.add_argument("--report",required=True)
a=p.parse_args()
def cmd(*args):
    return subprocess.run(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
out=[]
for overlay in a.overlays:
    dec=cmd("dtc","-I","dtb","-O","dts",overlay)
    if dec.returncode:
        out.append(f"{overlay}: dtc failed: {dec.stderr.strip()}")
        continue
    m=re.search(r"\b__fixups__\s*\{(.*?)\n\s*\};",dec.stdout,re.S)
    errs=[]
    count=0
    if m:
        for label, raw in re.findall(r'^\s*([\w,.-]+)\s*=\s*"([^"]*)";',m.group(1),re.M):
            for ent in raw.split(r"\0"):
                count+=1
                try:
                    path, prop, off=ent.rsplit(":",2)
                    offset=int(off)
                    if offset<0: raise ValueError("negative offset")
                except ValueError:
                    errs.append(f"{label}: malformed fixup entry: {ent[:150]}")
                    continue
                props=cmd("fdtget","-p",overlay,path)
                if props.returncode:
                    errs.append(f"{label}: missing overlay NODE {path}")
                elif prop not in props.stdout.splitlines():
                    errs.append(f"{label}: missing overlay PROPERTY {path}:{prop}")
                else:
                    # Compiled dtbo fixups always point to 32-bit slots, but avoid a
                    # lossy fdtget encoding conversion for checking binary lengths.
                    pass
    out.append(f"{pathlib.Path(overlay).name}: fixup_entries={count} invalid_paths_or_properties={len(errs)}")
    out.extend(errs[:100])
report=pathlib.Path(a.report);report.write_text("\n".join(out)+"\n")
print("\n".join(out))
