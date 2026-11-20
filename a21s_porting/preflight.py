#!/usr/bin/env python3
"""Syntax-only preflight of staged Samsung A21s DTBO sources.

This does not integrate the overlays into the Linux 5.10 kernel and cannot
verify hardware compatibility. No compiled DTBO or boot image is published.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REVISIONS = ("r00", "r01", "r02", "r03", "r06")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("reports/a21s-dtbo-preflight"))
    args = parser.parse_args()
    root = args.root
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    dtc = shutil.which("dtc")
    if dtc is None:
        parser.error("dtc is not available; install device-tree-compiler")
    entries: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="a21s-dtc-") as tmp:
        for revision in REVISIONS:
            name = f"a21s_eur_open_w00_{revision}.dts"
            staged = root / "a21s_porting" / "dts_reference" / name
            original_partial = root / "arch/arm64/boot/dts/samsung/a12s" / name
            if not staged.is_file():
                entries.append({"name": name, "source_present": False, "dtc_exit_code": None,
                                "diagnostic": "Staged source missing"})
                continue
            content = staged.read_text(encoding="utf-8", errors="replace")
            output_blob = Path(tmp) / f"{revision}.dtbo"
            result = subprocess.run(
                [dtc, "-@", "-I", "dts", "-O", "dtb", "-o", str(output_blob), str(staged)],
                text=True, capture_output=True, check=False,
            )
            head = content[:300]
            rev_match = re.search(r"dtbo-hw_rev\s*=\s*<(0x[0-9a-fA-F]+)>", head)
            partial_size = original_partial.stat().st_size if original_partial.is_file() else None
            diagnostics = (result.stdout + result.stderr)[-12000:]
            entries.append({
                "name": name,
                "source_present": True,
                "source_bytes": staged.stat().st_size,
                "a12s_folder_partial_bytes": partial_size,
                "compatible_a21s": "A21S_EUR_OPEN" in head,
                "hw_rev": rev_match.group(1) if rev_match else None,
                "dtc_exit_code": result.returncode,
                "syntax_compiled": result.returncode == 0,
                "diagnostic": diagnostics,
                "note": "Standalone dtc syntax check only; not a Linux 5.10 boot test",
            })

    out_json = output / "a21s-dtbo-preflight.json"
    out_json.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Samsung A21s DTBO source preflight",
        "",
        "**NOT FLASHABLE.** Validating the DTS syntax does not prove that the "
        "DTBO matches Linux 5.10, the device revision, panel or modem.",
        "",
        "| Revision | Staged source bytes | Older partial source bytes | dtc syntax |",
        "|---|---:|---:|---|",
    ]
    for e in entries:
        check = "PASS" if e.get("syntax_compiled") else "FAIL"
        lines.append(
            f"| {e['name']} | {e.get('source_bytes','missing')} | "
            f"{e.get('a12s_folder_partial_bytes','n/a')} | {check} |"
        )
    lines.append("")
    lines.append("## Diagnostics")
    for e in entries:
        lines += [f"### {e['name']}", "", "```text",
                  e.get("diagnostic") or "(No dtc warnings or errors)", "```", ""]
    lines += [
        "## Next steps",
        "- If syntax fails, diagnose failures without adding DTBOs to the kernel Makefile.",
        "- Confirm target Linux 5.10 base DTB bindings and A21s board-specific drivers.",
        "- Reconcile overlay phandles, targets, regulator references, panel and touch nodes.",
        "- Validate compile in the target kernel, then actual device boot, before packaging boot.img.",
        "- SUSFS is not integrated or tested by this workflow.",
    ]
    (output / "A21S_DTBO_PREFLIGHT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    failures = [e["name"] for e in entries if not e.get("syntax_compiled")]
    print(f"Results: {len(entries)-len(failures)}/{len(entries)} DTBO files passed standalone dtc")
    print(f"Report: {output.resolve()}")
    if failures:
        print("Files requiring fixes:", ", ".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
