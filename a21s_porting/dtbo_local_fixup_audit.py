#!/usr/bin/env python3
"""Check local DTBO fixup paths and property byte offsets; no files modified."""
import argparse
import json
import subprocess
from pathlib import Path

def read(*cmd):
    p=subprocess.run(["fdtget",*map(str,cmd)],capture_output=True,text=True,check=False)
    return p.returncode == 0,(p.stdout.strip() if p.returncode == 0 else p.stderr.strip())

def audit(overlay):
    o={"overlay":Path(overlay).name,"nodes":0,"props":0,"missing_nodes":[],
       "missing_properties":[],"invalid_offsets":[],"errors":[]}
    root="/__local_fixups__"
    ok,_=read("-l",overlay,root)
    if not ok:return o
    q=[root]
    while q:
        path=q.pop(0)
        source=path[len(root):] or "/"
        o["nodes"]+=1
        found,e=read("-p",overlay,source)
        if not found:o["missing_nodes"].append({"node":source,"why":e[:150]})
        child_ok,children=read("-l",overlay,path)
        if child_ok:q.extend(path.rstrip("/")+"/"+x for x in children.splitlines() if x)
        ok,props=read("-p",overlay,path)
        if not ok:
            o["errors"].append({"node":path,"why":props[:150]})
            continue
        for prop in props.splitlines():
            o["props"]+=1
            ok,data=read("-t","bx",overlay,source,prop)
            if not ok:
                o["missing_properties"].append({"node":source,"property":prop})
                continue
            off_ok,offs=read("-t","x",overlay,path,prop)
            if not off_ok:
                o["errors"].append({"node":path,"property":prop,"why":offs[:150]})
                continue
            for token in offs.split():
                try:offset=int(token,16)
                except ValueError:
                    o["errors"].append({"node":path,"bad_offset":token})
                    continue
                if offset+4>len(data.split()):
                    o["invalid_offsets"].append({"node":source,"property":prop,
                                                 "offset":offset,"bytes":len(data.split())})
    return o

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--overlays",nargs="+",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
    results=[audit(x) for x in a.overlays]
    (a.out_dir/"LOCAL_FIXUPS.json").write_text(json.dumps(results,indent=2)+"\n")
    lines=["# SM-A217F A21s DTBO local relocation audit","",
           "Diagnostic only. NOT proof of hardware boot compatibility.",""]
    for d in results:
        lines.extend(["## "+d["overlay"],"Nodes: "+str(d["nodes"]),
                      "Properties: "+str(d["props"])])
        for k in ["missing_nodes","missing_properties","invalid_offsets","errors"]:
            lines.append(k+": "+str(len(d[k])))
            for row in d[k][:20]: lines.append("- "+json.dumps(row))
        lines.append("")
    output="\n".join(lines)+"\n"
    (a.out_dir/"LOCAL_FIXUPS.md").write_text(output)
    print(output)

if __name__=="__main__":main()
