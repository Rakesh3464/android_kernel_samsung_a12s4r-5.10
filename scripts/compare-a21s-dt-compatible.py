#!/usr/bin/env python3
"""Compare source-level Device Tree compatible strings; never creates flashable images."""
from pathlib import Path
import re, sys

if len(sys.argv) != 4:
    sys.exit("usage: compare-dt-compatible.py A21S_DTS_DIR A12S_DTS_DIR REPORT_PATH")
a21s = Path(sys.argv[1]); a12s = Path(sys.argv[2]); output = Path(sys.argv[3])
pat = re.compile(r'\bcompatible\s*=\s*([^;]+);', re.MULTILINE | re.DOTALL)
strings = re.compile(r'"([^"]+)"')
def extract(path):
    data = path.read_text(errors="replace")
    return set(s for clause in pat.findall(data) for s in strings.findall(clause))
left = sorted(a21s.glob("a21s_*.dts"))
right = sorted(a12s.glob("a12s_*.dts"))
if not left or not right:
    sys.exit(f"missing DTS sources: A21s={len(left)}, A12s={len(right)}")
a12_compat = set().union(*(extract(p) for p in right))
lines = [
    "# A21s 4.19 vs A12s 5.10 DTS compatible-string audit",
    f"A21s reference DTS files: {len(left)}",
    f"A12s 5.10 DTS files: {len(right)}",
    "",
    "This is a text-level comparison ONLY, not kernel driver support validation.",
    "Numeric phandles, regulators, pinctrl, ABI and wiring still require a manual port.",
]
for src in left:
    a21_compat = extract(src)
    differences = sorted(a21_compat - a12_compat)
    lines += ["", f"## {src.name}", f"Unique A21s compatible strings ({len(differences)}):"]
    lines += [f"- {item}" for item in differences]
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text("\n".join(lines)+"\n")
print(f"Wrote {output}")
