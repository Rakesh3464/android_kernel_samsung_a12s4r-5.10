#!/usr/bin/env python3
"""Compute Android boot v2 page-aligned size. Never generates a boot.img."""
import argparse
import json
from pathlib import Path

# Verified SM-A217F baseline from original user boot image and prior device report
PARTITION_BYTES = 37_748_736
STOCK_KERNEL_BYTES = 34_068_504
STOCK_RAMDISK_BYTES = 1_462_536
STOCK_DTB_BYTES = 140_292
STOCK_BOOT_BYTES = 35_678_224
PAGE_BYTES = 2048
SAMSUNG_FOOTER_BYTES = 16


def align(n):
    return (n + PAGE_BYTES - 1) // PAGE_BYTES * PAGE_BYTES


def pack_size(kernel, ramdisk=STOCK_RAMDISK_BYTES, dtb=STOCK_DTB_BYTES):
    return PAGE_BYTES + align(kernel) + align(ramdisk) + align(dtb) + SAMSUNG_FOOTER_BYTES


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sources = p.add_mutually_exclusive_group(required=True)
    sources.add_argument("--image", type=Path, help="Compiled arm64 Image path")
    sources.add_argument("--image-size", type=int, help="Compiled Image length in bytes")
    sources.add_argument("--size-report", type=Path, help="wc -c report e.g. image-size.txt")
    p.add_argument("--out-dir", type=Path, default=Path("reports/boot-fit"))
    args = p.parse_args()
    if args.image:
        kernel = args.image.stat().st_size
    elif args.size_report:
        kernel = int(args.size_report.read_text().split()[0])
    else:
        kernel = args.image_size
    if kernel < 0:
        p.error("kernel size cannot be negative")
    assert pack_size(STOCK_KERNEL_BYTES) == STOCK_BOOT_BYTES, "Stock image layout does not reproduce"
    candidate = pack_size(kernel)
    fixed = pack_size(0)
    raw_budget = max(0, PARTITION_BYTES - fixed)
    aligned_max_kernel = raw_budget // PAGE_BYTES * PAGE_BYTES
    excess = max(0, candidate - PARTITION_BYTES)
    report = {
        "status": "OVERFLOW_BLOCKED" if excess else "FITS_SIZE_ONLY_NOT_BOOT_VALIDATED",
        "compiled_Image_bytes": kernel,
        "reference_ramdisk_bytes": STOCK_RAMDISK_BYTES,
        "reference_dtb_table_bytes": STOCK_DTB_BYTES,
        "estimated_boot_v2_bytes": candidate,
        "boot_partition_max_bytes": PARTITION_BYTES,
        "overflow_bytes": excess,
        "maximum_kernel_bytes_page_aligned": aligned_max_kernel,
        "needed_kernel_shrink_bytes": max(0, kernel - aligned_max_kernel),
        "stock_image_reproduction_bytes": pack_size(STOCK_KERNEL_BYTES),
        "warning": "ONLY a packing-size estimate using old ramdisk and DTB sizes. NEVER FLASH based on this result.",
    }
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "A21S_BOOT_FIT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown = "\n".join([
        "# A21s SM-A217F Android boot v2 conditional size budget",
        "",
        "**" + report["status"] + "** — NOT FLASHABLE.",
        "",
        f"- ARM64 Image: **{kernel:,} bytes**",
        f"- Existing GZIP ramdisk (assumption): **{STOCK_RAMDISK_BYTES:,} bytes**",
        f"- Existing DTB table (assumption): **{STOCK_DTB_BYTES:,} bytes**",
        f"- Page-aligned boot v2 estimate: **{candidate:,} bytes**",
        f"- Boot partition maximum: **{PARTITION_BYTES:,} bytes**",
        f"- Overflow: **{excess:,} bytes**",
        f"- Maximum Image after page alignment: **{aligned_max_kernel:,} bytes**",
        f"- Required shrink: **{report['needed_kernel_shrink_bytes']:,} bytes**",
        "",
        "Original stock boot image layout reproduced: "
        + f"{report['stock_image_reproduction_bytes']:,} bytes.",
        "",
        "This estimate does NOT validate the new 5.10 DTB, ramdisk, hardware, "
        "vendor ABI, KernelSU, SUSFS, bootloader, or actual device boot.",
        "Do not flash these components or treat this report as boot approval.",
        "",
    ])
    (out / "A21S_BOOT_FIT.md").write_text(markdown + "\n", encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
