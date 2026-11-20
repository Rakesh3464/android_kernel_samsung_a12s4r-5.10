# SM-A217F Linux 5.10 boot partition fit: measured blocking result

**Status: BLOCKED / NOT FLASH READY.** This is an analysis of a successful *experimental* 5.10 compilation, not an A21s device-validated image.

## Evidence

- [GitHub Actions build run #44680936353](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44680936353), commit `389f549bfec0dd96fadbe149c68a9e4f811ad0f3`.
- Retrieved artifact `A21S-510-DTBO-IMAGE-COMPILE-LOGS-NOT-FLASHABLE`:
  - `image-exit-code.txt` = `0`
  - `dtbs-exit-code.txt` = `0`
  - `image-size.txt` = **37,153,280 bytes**
  - `image-sha256.txt` = `155b1869111eda7705dfd38541797d44bc8f882f80d8976309e2c212801fd7b9`
  - The five experimental A21s DTBOs were compiled but not tested on hardware.
- Original user-uploaded SM-A217F boot image (not committed): `boot-a21s.img`, SHA-256 `af3c2406848c71639b420cf4f709a28550f7eae05caf65731db8fac50f897928`.
- Inspected Android boot v2 layout: page size 2048, old kernel 34,068,504 bytes, compressed ramdisk 1,462,536 bytes, DTB table 140,292 bytes, Samsung footer 16 bytes, original boot file 35,678,224 bytes.
- A21s boot partition size from prior device report: **37,748,736 bytes (36 MiB)**.

## Exact conditional size calculation

This calculation **assumes the existing stock ramdisk and original DTB-table byte counts**, and is only a **packing-size estimate** (they are not guaranteed compatible with Linux 5.10).

For Android boot image v2 with the observed Samsung footer, aligned to 2048-byte pages:

```text
align2048(n) = ceil(n / 2048) * 2048

packed_size = 2048 (header page)
            + align2048(kernel size)
            + align2048(ramdisk size)
            + align2048(DTB table size)
            + 16 (Samsung SEANDROIDENFORCE footer)
```

| Metric | Bytes |
| --- | ---: |
| Compiled 5.10 Image | 37,153,280 |
| Existing GZIP ramdisk | 1,462,536 |
| Existing DTB table | 140,292 |
| Estimated repacked image after page padding/footer | **38,762,512** |
| SM-A217F boot partition maximum | **37,748,736** |
| Estimated overflow (NOT FLASHABLE) | **1,013,776** |
| Conditional maximum kernel budget with old ramdisk/DTB | **36,141,040** |
| Minimum kernel reduction needed at current alignment | **1,012,240** |

Reproduction check: the same calculation using the **original** kernel size reproduces the exact input boot image length **35,678,224** bytes.

**This is a packing-size blocker even before hardware compatibility, modem, DTBO, vendor module ABI and SUSFS issues.** Do not overwrite/extend the physical boot partition or strip required ramdisk/DTB/AVB metadata to force a fit.

## SUSFS is separately blocked

- [SUSFS preflight #44681104818](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44681104818).
- Upstream `gki-android13-5.10` patch checkout commit `d480b312d650601888550529695706f4a112e29e` was used by this dry run.
- `fs/namespace.c`: first hunk failed at around line 30.
- `fs/proc/base.c`: first hunk failed at around line 99.
- `patch --dry-run` returned exit code **1**. The workflow itself showed green because its purpose was to **report compatibility**, not to require an applicable patch.
- No in-tree KernelSU source directory was found at the two common locations. This does not prove all KernelSU hooks are absent.
- **SUSFS is NOT installed by this workflow;** a clean patch plus full KernelSU integration and on-device verification would still be required.

## Safe next engineering milestones

1. Disable unused board drivers or select an A21s-specific config only after validating required panel, touch, camera, charger, modem, storage and Wi-Fi features; rebuild and re-measure.
2. Capture the *new* actual DTB/DTBO and ramdisk sizes. Recheck Android boot image header v2, 2048-page layout, board cmdline and Samsung bootloader requirements.
3. Rebase the two failed SUSFS hunks manually with explicit review and test the complete patch in a disposable checkout. Validate KernelSU/SUSFS Kconfig and symbols.
4. Confirm the candidate image fits **37,748,736 bytes**, bootloader accepts it, and the actual A21s device boots; maintain a stock restore method.

**No image produced or approved for flashing.**
