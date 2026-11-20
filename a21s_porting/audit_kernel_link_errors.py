#!/usr/bin/env python3
"""Read linker logs and classify missing KernelSU/SUSFS symbols. No kernel changes."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--build-log", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    lines = a.build_log.read_text(errors="replace").splitlines()
    undefined = sorted(set(re.findall(r"undefined symbol:\s*([^\s]+)", "\n".join(lines))))
    ksu = [x for x in undefined if x.startswith(("ksu_", "__ksu_", "susfs_")) or x in
           ("setup_selinux", "fake_status")]
    other = [x for x in undefined if x not in ksu]
    report = {
        "status": "BLOCKED_MISSING_KERNELSU_LINK" if ksu else
                  "BLOCKED_OTHER_UNDEFINED_SYMBOLS" if other else "NO_UNDEFINED_SYMBOLS_DETECTED",
        "undefined_symbols_visible": undefined,
        "susfs_or_kernelsu_symbols": ksu,
        "other_symbols": other,
        "note": "Compiler output may truncate errors; no claim of complete symbol coverage. NOT FLASHABLE."
    }
    (a.out_dir / "LINK_UNDEFINED_SYMBOLS.json").write_text(json.dumps(report, indent=2) + "\n")
    summary = ["# SM-A217F Linux 5.10 linker diagnosis", "",
               f"Status: **{report['status']}**", "",
               "KernelSU/SUSFS symbols reported missing by linker:"]
    summary.extend("- `" + x + "`" for x in ksu)
    summary.extend(["", "Other missing symbols:"])
    summary.extend("- `" + x + "`" for x in other)
    summary.extend(["", "The kernel must not be packaged or flashed until KernelSU source",
                    "and integration are correctly built and linked, and hardware verified."])
    (a.out_dir / "LINK_UNDEFINED_SYMBOLS.md").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))

if __name__ == "__main__":
    main()
