#!/usr/bin/env python3
"""Compare A21s 4.19 vs A12s 5.10 defconfig options without changing either kernel."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SOURCE_DEFCONFIG = "arch/arm64/configs/exynos850-a21snsxx_defconfig"
TARGET_DEFCONFIG = "arch/arm64/configs/exynos850-a12snsxx_defconfig"

CATEGORIES = {
    "SoC and platform": r"(EXYNOS|SOC_|S5E3830|ARCH_EXYNOS)",
    "A21s display and touch": r"(DECON_LCD|TOUCHSCREEN|BACKLIGHT_LCD)",
    "Cameras and flash": r"(CAMERA_|CIS_|FLASH_)",
    "Charging and battery": r"(CHARGER_|BATTERY|S2MU106|SM5714)",
    "Sensors and fingerprint": r"(SENSORS_|FINGERPRINT|ET5XX|SSP)",
    "Audio": r"(SND_SOC|AUDIO)",
    "WiFi and modem": r"(WLAN|MODEM|SCSC)",
    "USB and storage": r"(USB_|MMC_|SCSI)",
    "Root framework settings": r"(KSU|SUSFS|SUS)",
}


def parse(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing defconfig: {path}")
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        enabled = re.fullmatch(r"(CONFIG_[A-Z0-9_]+)=(.+)", line)
        disabled = re.fullmatch(r"# (CONFIG_[A-Z0-9_]+) is not set", line)
        if enabled:
            result[enabled.group(1)] = enabled.group(2)
        elif disabled:
            result[disabled.group(1)] = "n"
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-419", type=Path, required=True)
    p.add_argument("--source-510", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    older = parse(a.source_419 / SOURCE_DEFCONFIG)
    newer = parse(a.source_510 / TARGET_DEFCONFIG)
    old_keys, new_keys = set(older), set(newer)
    only_old = sorted(k for k in old_keys - new_keys if older[k] != "n")
    only_new = sorted(k for k in new_keys - old_keys if newer[k] != "n")
    changed = sorted(k for k in old_keys & new_keys if older[k] != newer[k])

    groups = {}
    for title, pattern in CATEGORIES.items():
        regex = re.compile(pattern)
        groups[title] = {
            "enabled_only_in_A21s_4_19_defconfig": {k: older[k] for k in only_old if regex.search(k)},
            "enabled_only_in_A12s_5_10_defconfig": {k: newer[k] for k in only_new if regex.search(k)},
            "different_values": {k: {"A21s_4_19": older[k], "A12s_5_10": newer[k]}
                                 for k in changed if regex.search(k)}
        }

    report = {
        "source": SOURCE_DEFCONFIG,
        "target": TARGET_DEFCONFIG,
        "config_options_A21s_4_19": len(older),
        "config_options_A12s_5_10": len(newer),
        "enabled_only_in_A21s_4_19_defconfig_count": len(only_old),
        "enabled_only_in_A12s_5_10_defconfig_count": len(only_new),
        "changed_common_option_count": len(changed),
        "categories": groups,
        "warning": "Differences in defconfig do not prove drivers are missing in the source. "
                   "Do not apply 4.19 settings wholesale to 5.10.",
    }
    a.out_dir.mkdir(parents=True, exist_ok=True)
    (a.out_dir / "A21S_CONFIG_DIFF.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Samsung A21s Linux 4.19 vs A12s Linux 5.10 defconfig comparison",
        "",
        "**Config comparison only. Not a hardware port or flashable kernel.**",
        "",
        f"- Old A21s options recorded: **{len(older)}**",
        f"- Target A12s options recorded: **{len(newer)}**",
        f"- Enabled options in A21s config but absent from A12s config: **{len(only_old)}**",
        f"- Enabled options in A12s config but absent from A21s config: **{len(only_new)}**",
        f"- Same option name with different setting: **{len(changed)}**",
        "",
        "Configuration differences do **not** prove that a feature or driver is absent from "
        "the Linux 5.10 source. Board-specific modules and Kconfig need separate verification.",
    ]
    for title, group in groups.items():
        lines += ["", f"## {title}", ""]
        for subtitle, key in (
            ("A21s 4.19 only (enabled in old config)", "enabled_only_in_A21s_4_19_defconfig"),
            ("A12s 5.10 only (enabled in target config)", "enabled_only_in_A12s_5_10_defconfig"),
        ):
            lines.append(f"**{subtitle}**")
            values = group[key]
            lines.append(", ".join(f"`{k}={v}`" for k, v in list(values.items())[:60]) if values else "None in this category")
            lines.append("")
        changes = group["different_values"]
        if changes:
            lines.append("**Different values:**")
            lines.extend(f"- `{k}`: A21s={v['A21s_4_19']}, A12s={v['A12s_5_10']}"
                         for k, v in changes.items())
    lines += [
        "",
        "## Engineering requirements",
        "- Identify all actual A21s panel and touchscreen variants from known-working device data.",
        "- Map A21s camera, charging and fingerprint Kconfig to Linux 5.10 implementations.",
        "- Check Kconfig dependencies and Device Tree bindings before introducing A21s options.",
        "- Keep the 5.10 defconfig unchanged until the required drivers are verified.",
        "- SUSFS and KernelSU need a separate exact-revision compatibility audit.",
    ]
    (a.out_dir / "A21S_CONFIG_DIFF.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Compared {len(older)} A21s options to {len(newer)} A12s options; "
          f"{len(only_old)} old-only enabled; {len(only_new)} new-only enabled; "
          f"{len(changed)} different common values")


if __name__ == "__main__":
    main()
