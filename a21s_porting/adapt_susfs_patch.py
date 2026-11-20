#!/usr/bin/env python3
"""Adapt two SUSFS upstream patch contexts to Samsung Exynos850 Linux 5.10.

This changes only a *copy of the .patch file*; no kernel sources are modified.
Strict source and patch anchors make unexpected upstream drift fail safely.
Actual KernelSU/SUSFS integration and compile are separate steps.
"""
from __future__ import annotations

import argparse
from pathlib import Path

VENDOR_EXEC = "#include <linux/io_uring.h>\n#include <linux/task_integrity.h>\n"
VENDOR_NAMESPACE = "#include <linux/shmem_fs.h>\n#include <linux/fslog.h>\n"
VENDOR_PROC = (
    "#include <linux/cpufreq_times.h>\n"
    "#include <linux/task_integrity.h>\n"
    "#include <linux/proca.h>\n"
)

REPLACEMENTS = {
    "fs/exec.c": (
        "@@ -64,6 +64,9 @@\n"
        " #include <linux/compat.h>\n"
        " #include <linux/vmalloc.h>\n"
        " #include <linux/io_uring.h>\n",
        "@@ -64,7 +64,10 @@\n"
        " #include <linux/compat.h>\n"
        " #include <linux/vmalloc.h>\n"
        " #include <linux/io_uring.h>\n"
        " #include <linux/task_integrity.h>\n",
    ),
    "fs/namespace.c": (
        "@@ -30,10 +30,21 @@\n"
        " #include <uapi/linux/mount.h>\n"
        " #include <linux/fs_context.h>\n"
        " #include <linux/shmem_fs.h>\n",
        "@@ -30,11 +30,22 @@\n"
        " #include <uapi/linux/mount.h>\n"
        " #include <linux/fs_context.h>\n"
        " #include <linux/shmem_fs.h>\n"
        " #include <linux/fslog.h>\n",
    ),
    "fs/proc/base.c": (
        "@@ -99,6 +99,9 @@\n"
        " #include <linux/time_namespace.h>\n"
        " #include <linux/resctrl.h>\n"
        " #include <linux/cpufreq_times.h>\n",
        "@@ -99,8 +99,11 @@\n"
        " #include <linux/time_namespace.h>\n"
        " #include <linux/resctrl.h>\n"
        " #include <linux/cpufreq_times.h>\n"
        " #include <linux/task_integrity.h>\n"
        " #include <linux/proca.h>\n",
    ),
}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--patch", type=Path, required=True, help="Original upstream patch")
    p.add_argument("--kernel", type=Path, required=True, help="Unmodified Linux 5.10 checkout")
    p.add_argument("--output", type=Path, required=True, help="Write adapted patch here")
    a = p.parse_args()
    source_exec = (a.kernel / "fs/exec.c").read_text(encoding="utf-8")
    source_namespace = (a.kernel / "fs/namespace.c").read_text(encoding="utf-8")
    source_proc = (a.kernel / "fs/proc/base.c").read_text(encoding="utf-8")
    if VENDOR_EXEC not in source_exec:
        p.error("Samsung fs/exec.c task_integrity.h context not found; manual review needed")
    if VENDOR_NAMESPACE not in source_namespace:
        p.error("Samsung fs/namespace.c fslog.h context not found; manual review needed")
    if VENDOR_PROC not in source_proc:
        p.error("Samsung fs/proc/base.c integrity/proca context not found; manual review needed")

    patched = a.patch.read_text(encoding="utf-8", errors="replace")
    for filename, (before, after) in REPLACEMENTS.items():
        if patched.count(before) != 1:
            p.error(f"Upstream patch changed: expected one original context in {filename}, "
                    f"found {patched.count(before)}")
        patched = patched.replace(before, after, 1)

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(patched, encoding="utf-8")
    print("Generated Samsung-specific patch context adaptation:")
    print(" - fs/exec.c: preserved additional #include <linux/task_integrity.h>")
    print(" - fs/namespace.c: preserved additional #include <linux/fslog.h>")
    print(" - fs/proc/base.c: preserved additional task_integrity.h / proca.h")
    print("No kernel source files were modified. This output still requires dry-run,")
    print("complete source integration, full compilation and actual device tests.")


if __name__ == "__main__":
    main()
