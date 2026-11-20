#!/usr/bin/env python3
"""Extract first SUSFS patch hunk + vendor context for manual triage.

Read-only. Does not apply patch or alter kernel files.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

FILES = ("fs/namespace.c", "fs/proc/base.c")


def first_hunk(patch: str, filename: str) -> tuple[str, list[str]] | None:
    current = False
    header = None
    body: list[str] = []
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            if current and header is not None:
                break
            current = line.endswith(" b/" + filename)
            header = None
            body = []
        elif current and line.startswith("@@ "):
            if header is not None:
                break
            header = line
        elif current and header is not None:
            body.append(line)
    if header is None:
        return None
    return header, body


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--patch", type=Path, required=True)
    p.add_argument("--kernel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    patch = a.patch.read_text(encoding="utf-8", errors="replace")
    lines = [
        "# A21s SUSFS patch hunk context",
        "",
        "Generated from upstream patch and the target Linux 5.10 source.",
        "No patches were applied to the repository by this helper.",
        "",
    ]
    for filename in FILES:
        lines += [f"## `{filename}`", ""]
        hunk = first_hunk(patch, filename)
        target = a.kernel / filename
        if hunk is None:
            lines += ["No matching diff hunk was found.", ""]
            continue
        header, changes = hunk
        lines += ["### First upstream hunk", "", "```diff", header, *changes[:120], "```", ""]
        m = re.search(r"@@ -(\d+)(?:,\d+)? \+", header)
        target_line = int(m.group(1)) if m else 1
        if not target.is_file():
            lines += [f"Target source not found: {target}", ""]
            continue
        source = target.read_text(encoding="utf-8", errors="replace").splitlines()
        lo = max(1, target_line - 25)
        hi = min(len(source), target_line + 60)
        lines += [f"### Vendor source lines {lo}–{hi}", "", "```c"]
        lines += [f"{n:5d}: {source[n-1]}" for n in range(lo, hi + 1)]
        lines += ["```", ""]
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote patch-context analysis: {a.output}")


if __name__ == "__main__":
    main()
