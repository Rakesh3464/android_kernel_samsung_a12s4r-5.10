#!/usr/bin/env python3
"""Compare A21s Linux 4.19 and A12s-derived Linux 5.10 sources without modifying kernels.

Output is an inventory, NOT a compiled kernel or flashable image.
Requires Python 3.9+ and local checkouts of both repositories.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def read(root: Path, relpath: str) -> str:
    path = root / relpath
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def kernel_version(root: Path) -> str:
    make = read(root, "Makefile")
    values = []
    for key in ("VERSION", "PATCHLEVEL", "SUBLEVEL"):
        match = re.search(rf"(?m)^{key}\s*=\s*(\d+)\s*$", make)
        values.append(match.group(1) if match else "?")
    return ".".join(values)


def first_compatible(dts: str) -> str:
    match = re.search(r"\bcompatible\s*=\s*([^;]+);", dts)
    return " ".join(match.group(1).split()) if match else "(not found)"


def get_dtbo_refs(root: Path) -> list[str]:
    mk = read(root, "arch/arm64/boot/dts/Makefile")
    return sorted(set(re.findall(r"samsung/(?:a21s|a12s)/[^\s\\]+\.dtbo", mk)))


def overlays(root: Path, device: str) -> list[str]:
    folder = root / "arch/arm64/boot/dts/samsung" / device
    return sorted(p.name for p in folder.glob("*.dts")) if folder.is_dir() else []


def relevant_configs(root: Path) -> list[str]:
    base = root / "arch/arm64/configs"
    if not base.exists():
        return []
    found = []
    for p in base.rglob("*defconfig"):
        if p.is_file() and any(t in p.name.lower() for t in ("a21", "a12", "3830", "850", "smdk")):
            found.append(str(p.relative_to(root)))
    return sorted(found)


def observe(root: Path) -> dict:
    oldbase = "arch/arm64/boot/dts/exynos/exynos3830.dts"
    newbase = "arch/arm64/boot/dts/exynos/s5e3830.dts"
    soc_kconfig = read(root, "drivers/soc/samsung/Kconfig")
    return {
        "kernel_version": kernel_version(root),
        "base_dts": {
            rel: {"present": bool(read(root, rel)), "compatible": first_compatible(read(root, rel))}
            for rel in (oldbase, newbase)
        },
        "a21s_dts_files": overlays(root, "a21s"),
        "a12s_dts_files": overlays(root, "a12s"),
        "referenced_dtbo": get_dtbo_refs(root),
        "s5e3830_soc_kconfig": bool(re.search(r"(?m)^config SOC_S5E3830\b", soc_kconfig)),
        "relevant_defconfigs_found": relevant_configs(root),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-419", type=Path, required=True)
    p.add_argument("--source-510", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    src419, src510 = args.source_419, args.source_510
    for source in (src419, src510):
        if not (source / "Makefile").is_file():
            p.error(f"Not a kernel root (missing Makefile): {source}")

    a, b = observe(src419), observe(src510)
    data = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "atlas_419": {"path": str(src419), **a},
            "target_510": {"path": str(src510), **b},
        },
        "warning": "Source inventory only. No cross-kernel port, SUSFS merge, compile, or flash validation performed.",
    }
    (out / "a21s-source-inventory.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    old_refs = [x for x in a["referenced_dtbo"] if "/a21s/" in x]
    new_refs = [x for x in b["referenced_dtbo"] if "/a21s/" in x]
    a12_refs = [x for x in b["referenced_dtbo"] if "/a12s/" in x]
    lines = [
        "# Automated Samsung A21s kernel source comparison",
        "",
        "**This is a source audit, NOT a flashable boot.img.**",
        "",
        "| Check | atlas-new / 4.19 | target / 5.10 |",
        "|---|---|---|",
        f"| Kernel Makefile version | `{a['kernel_version']}` | `{b['kernel_version']}` |",
        f"| A21s overlay DTS files | {len(a['a21s_dts_files'])} | {len(b['a21s_dts_files'])} |",
        f"| A21s DTBO entries in Makefile | {len(old_refs)} | {len(new_refs)} |",
        f"| A12s DTBO entries in Makefile | {len([x for x in a['referenced_dtbo'] if '/a12s/' in x])} | {len(a12_refs)} |",
        f"| SOC_S5E3830 in Samsung Kconfig | {a['s5e3830_soc_kconfig']} | {b['s5e3830_soc_kconfig']} |",
        "",
        "## A21s DTBO targets in reference tree",
        *([f"- `{x}`" for x in old_refs] or ["(No matching entries found in sparse checkout)"]),
        "",
        "## Device Tree base compatibility",
    ]
    for label, observation in (("4.19 / exynos3830.dts", a["base_dts"]["arch/arm64/boot/dts/exynos/exynos3830.dts"]),
                               ("5.10 / s5e3830.dts", b["base_dts"]["arch/arm64/boot/dts/exynos/s5e3830.dts"])):
        lines.append(f"- **{label}:** present={observation['present']}; first compatible={observation['compatible']}")
    lines += [
        "",
        "## Important constraints",
        "- The 5.10 source may support S5E3830/A12s but still lack A21s-specific board overlays or peripherals.",
        "- Compare DTS labels, bindings, symbols, pinctrl, clocks, regulators, panel and modem before attempting overlay migration.",
        "- Review any decompiled DTBO fragments: placeholder phandles and raw byte-string paths may need reconstruction.",
        "- Do not copy a 4.19 kernel defconfig or overlay blindly into Linux 5.10.",
        "- KernelSU/SUSFS is NOT included by this audit; verify exact compatibility separately.",
        "- Do not produce or flash a boot.img until the device-specific kernel, DTB/DTBO and boot header are proven.",
        "",
        "## Config candidates found",
        "**4.19:** " + (", ".join(a["relevant_defconfigs_found"]) or "(none found in checked paths)"),
        "",
        "**5.10:** " + (", ".join(b["relevant_defconfigs_found"]) or "(none found in checked paths)"),
        "",
    ]
    (out / "A21S_SOURCE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved audit to {out.resolve()}")
    print(f"Reference: Linux {a['kernel_version']} -> target Linux {b['kernel_version']}")
    print(f"A21s DTBO references: {len(old_refs)} -> {len(new_refs)}")


if __name__ == "__main__":
    main()
