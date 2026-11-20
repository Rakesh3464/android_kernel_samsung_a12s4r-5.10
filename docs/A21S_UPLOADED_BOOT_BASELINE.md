# Samsung A21s SM-A217F: uploaded boot image baseline

**Verified from the uploaded user's `boot-a21s.img` (20 Nov 2026).**
This file is a REFERENCE, not a Linux 5.10 kernel and not a new flashable boot image.
The original user-supplied binary has **not** been uploaded to the public repository.

## Integrity / exact device

- Original boot file: `boot-a21s.img`, **35,678,224 bytes**.
- Original SHA-256: `af3c2406848c71639b420cf4f709a28550f7eae05caf65731db8fac50f897928`.
- Boot ramdisk `system/etc/ramdisk/build.prop`: `ro.product.bootimage.model=SM-A217F`, `ro.product.bootimage.device=a21s`, `ro.product.bootimage.name=a21snsxx`.
- Ramdisk software baseline: Samsung Android 12, build `A217FXXSCDXE2` from May 2024. **This ramdisk metadata does not establish the currently installed custom ROM version.**
- Embedded ARM64 kernel version string: `Linux version 4.19.325-g4a2052095396`, build dated Oct 17, 2026. **This is not 5.10.**
- Kernel binary has a KernelSU log-format string. That is not evidence that an exact SUSFS patchset is integrated or working.

## Original Android boot image layout

| Property | Value |
| --- | --- |
| Android boot header | v2, header size 1660 bytes |
| Page size | 2048 |
| Board name | `SRPTA21C012` |
| Header OS version / patch level | `12.0.0` / `2024-05` |
| Kernel | 34,068,504 bytes at file offset 2048; ARM64 `ARMd` Image |
| Kernel load address | `0x10008000` |
| Ramdisk | 1,462,536 bytes at file offset 34,072,576; GZIP + CPIO |
| Ramdisk load address | `0x11000000` |
| DTB / DT table | 140,292 bytes at file offset 35,536,896 |
| DTB load address | `0x10000000` |
| Tags address | `0x10000100` |
| Header cmdline | `androidboot.hardware=exynos850 androidboot.selinux=enforce loop.max_part=7` |
| Samsung boot footer | `SEANDROIDENFORCE` (16 bytes) |

## Verified DTB and ramdisk

- DT table magic `0xd7b7ab1e`; **one DTB entry** containing an FDT of **140,228 bytes**, FDT v17.
- DTB root `compatible` includes `samsung,armv8`, `samsung,exynos850`.
- DTB includes `samsung,exynos3830-pinctrl` and mentions `td4150`; the latter does not by itself identify the display panel physically present in the phone.
- Compressed ramdisk decompresses to 3,242,496 bytes with 17 CPIO entries, including `init`, `fstab.exynos850` and `system/etc/ramdisk/build.prop`.
- `fstab.exynos850` uses EROFS+AVB for logical system/vendor/product/odm, F2FS for userdata and `fileencryption=ice`.

## Linux 5.10 comparison and release block

- Linux 5.10 source base DTS at `arch/arm64/boot/dts/exynos/s5e3830.dts` has root `samsung,exynos3830` and pinctrl `samsung,s5e3830-pinctrl`. This is not a byte-for-byte compatible replacement for the uploaded boot DTB.
- Five A21s reference overlays are staged at `a21s_porting/dts_reference/` and passed **standalone DTS syntax tests**, not hardware boot validation.
- Check **SM-A217F/A21s board-specific** driver, panel, camera, touch, modem and charger support against Linux 5.10 and selected vendor ROM ABI before activating DTBOs.
- Repack test images only when working 5.10 kernel + matching DTBs/DTBOs and vendor integration are available. Preserve Android boot v2 parameters, original ramdisk requirements and Samsung footer.
- SUSFS revision compatibility and a real A21s boot test are still **not completed**.

**DO NOT flash a purported Linux 5.10 boot.img on the basis of this report alone. No flash-ready image has been created.**
