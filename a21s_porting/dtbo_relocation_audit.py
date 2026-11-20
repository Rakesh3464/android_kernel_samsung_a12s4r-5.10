#!/usr/bin/env python3
"""Diagnose exact compiled FDT external fixup failures. Never writes DTBs.

Checks both symbol existence AND the symbol's target node existence in the
compiled base DTB. Also checks each fixup's source property in the overlay.
This is not proof of hardware compatibility, even if all checks pass.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def fdtget(*args: str) -> tuple[bool, str]:
    p = subprocess.run(["fdtget", *map(str, args)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       encoding="utf-8", errors="replace", check=False)
    return p.returncode == 0, p.stdout.strip() if p.returncode == 0 else p.stderr.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--overlays", type=Path, nargs="+", required=True)
    parser.add_argument("--out-dir", required=True, type=Path)
    a = parser.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for overlay in a.overlays:
        data = {"overlay": overlay.name, "checked": 0, "missing_base_symbols": [],
                "broken_base_symbol_paths": [], "broken_fixup_sources": [],
                "bad_overlay_symbol_paths": [], "overlay_symbols_checked": 0,
                "fixups_error": "", "warning": "NOT BOOT VALIDATED"}
        ok, names = fdtget("-p", overlay, "/__fixups__")
        if not ok:
            data["fixups_error"] = names
            results.append(data)
            continue
        labels = names.splitlines()
        symbols_ok, overlay_symbol_names = fdtget("-p", overlay, "/__symbols__")
        if symbols_ok:
            for overlay_symbol in overlay_symbol_names.splitlines():
                overlay_symbol = overlay_symbol.strip()
                if not overlay_symbol:
                    continue
                data["overlay_symbols_checked"] += 1
                path_ok, symbol_path = fdtget(
                    "-t", "s", overlay, "/__symbols__", overlay_symbol)
                if not path_ok:
                    data["bad_overlay_symbol_paths"].append(
                        {"symbol": overlay_symbol, "error": symbol_path[:150]})
                    continue
                node_path = symbol_path.split()[0]
                good, error = fdtget("-p", overlay, node_path)
                if not good:
                    data["bad_overlay_symbol_paths"].append(
                        {"symbol": overlay_symbol, "path": node_path,
                         "error": error[:150]})
        else:
            data["bad_overlay_symbol_paths"].append(
                {"symbol": "__symbols__", "error": overlay_symbol_names[:150]})
        for label in labels:
            label = label.strip()
            if not label:
                continue
            data["checked"] += 1
            exists, destination = fdtget("-t", "s", a.base, "/__symbols__", label)
            if not exists:
                data["missing_base_symbols"].append(label)
                continue
            destination = destination.split()[0]
            path_ok, path_result = fdtget("-p", a.base, destination)
            if not path_ok:
                data["broken_base_symbol_paths"].append(
                    {"symbol": label, "path": destination, "error": path_result[:160]})
            refs_ok, refs = fdtget("-t", "s", overlay, "/__fixups__", label)
            if not refs_ok:
                data["broken_fixup_sources"].append(
                    {"symbol": label, "error": refs[:160]})
                continue
            for ref in refs.split():
                parts = ref.rsplit(":", 2)
                if len(parts) != 3:
                    data["broken_fixup_sources"].append(
                        {"symbol": label, "reference": ref, "error": "Invalid relocation format"})
                    continue
                path, prop, offset = parts
                good, properties = fdtget("-p", overlay, path)
                if not good or prop not in properties.splitlines():
                    data["broken_fixup_sources"].append(
                        {"symbol": label, "reference": ref,
                         "error": "Source node/property not present"})
        results.append(data)
    summary = ["# SM-A217F compiled Linux 5.10 DTBO relocation analysis",
               "", "No images are generated. Even a clean diagnostic is NOT a boot validation.", ""]
    for d in results:
        failures = (len(d["missing_base_symbols"]) + len(d["broken_base_symbol_paths"])
                    + len(d["broken_fixup_sources"]) + len(d["bad_overlay_symbol_paths"])
                    + bool(d["fixups_error"]))
        summary.extend([f"## {d['overlay']}",
                        f"- Fixup symbols checked: {d['checked']}",
                        f"- Missing base symbols: {len(d['missing_base_symbols'])}",
                        f"- Base symbols pointing to absent nodes: {len(d['broken_base_symbol_paths'])}",
                        f"- Fixup references absent in overlay: {len(d['broken_fixup_sources'])}",
                        f"- Overlay-defined symbols checked: {d['overlay_symbols_checked']}",
                        f"- Overlay-defined symbols pointing to absent nodes: {len(d['bad_overlay_symbol_paths'])}",
                        f"- Diagnostic: {'RELOCATION ERRORS FOUND' if failures else 'FIXUPS RESOLVED (not board validated)'}"])
        if d["missing_base_symbols"]:
            summary.append("- Missing: " + ", ".join(d["missing_base_symbols"]))
        for row in d["broken_base_symbol_paths"][:12]:
            summary.append(f"- Missing node: {row['symbol']} -> {row['path']}")
        for row in d["broken_fixup_sources"][:12]:
            summary.append(f"- Missing relocation property: {row}")
        for row in d["bad_overlay_symbol_paths"][:15]:
            summary.append(f"- Broken overlay symbol: {row}")
        if d["fixups_error"]:
            summary.append("- Error: " + d["fixups_error"])
        summary.append("")
    (a.out_dir / "RELOCATION_AUDIT.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (a.out_dir / "RELOCATION_AUDIT.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
