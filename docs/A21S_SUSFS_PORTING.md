# Samsung Galaxy A21s (Exynos 850) — Experimental Linux 5.10 / SUSFS port

> Status: **SOURCE-AUDIT ONLY. NOT FLASH READY.** Do not flash images built from this branch until all compatibility and boot tests are complete.

## Source references

- New development branch: `Rakesh3464/android_kernel_samsung_a12s4r-5.10`, branch `a21s-susfs-port`.
- Base branch: `android13-5.10-lts`; its top-level Makefile reports Linux **5.10.274**, `TARGET_SOC=s5e3830`.
- Device reference: `Rakesh3464/atlas-new`, branch `master`; its top-level Makefile reports Linux **4.19.325**.
- The reference source's `build.config.smdk3830` sets `DEFCONFIG=smdk3830_defconfig` and names `exynos3830.dtb` and `dtbo.img` outputs.
- These are different kernel major/minor series. Files, DTBs, drivers and configs cannot simply be copied across without porting and validation.

## Pre-build compatibility checklist

- [ ] Confirm exact A21s model/board revision and obtain known-working boot.img, vendor_boot (if applicable), DTB/DTBO and kernel config as reference.
- [ ] Determine the original boot image's Android boot header version, page size, base/offsets, cmdline, compression and ramdisk layout.
- [ ] Inventory Exynos 850 board DTS/DTSI, reserved memory, regulators, clocks, pinctrl, MMC/UFS, USB, display/panel, touchscreen, camera, audio, sensors, modem, Wi-Fi/Bluetooth and security features.
- [ ] Locate and validate an A21s-specific defconfig suitable for Linux 5.10; compare required `CONFIG_*` options to the 4.19 reference.
- [ ] Inspect vendor-specific 4.19 drivers for 5.10 kernel API / Kconfig / Device Tree binding incompatibilities.
- [ ] Verify the kernel toolchain and needed external components; run a clean **compile-only** build first.
- [ ] Verify the 5.10 kernel can produce a compatible Image and board-matched DTB/DTBO, with no build errors.
- [ ] Choose a SUSFS patchset that explicitly supports the targeted 5.10 revision and supported KernelSU variant, review changes and dependencies, then compile-test separately.
- [ ] Confirm the existing Android 15 / One UI build's boot/vendor ABI, vendor modules, fstab, SELinux requirements and userspace compatibility.
- [ ] Repack test boot.img with the stock boot image's proven header and device-specific parameters, preserving vendor components as required.
- [ ] Keep recoverable stock firmware/images, capture UART or other early-boot logs if available, and only then perform a device-specific boot test.

## Release gate

Do **not** describe this branch as a flash-ready Samsung A21s kernel. A successful compilation is not proof of hardware compatibility or boot success. Only publish a flashable image after device-specific checks, a recovery plan and successful actual-device boot tests.

## Current outcome

- [x] Isolated development branch created from the default 5.10 branch.
- [x] Source mismatch documented (4.19.325 versus 5.10.274).
- [ ] A21s Linux 5.10 platform support demonstrated.
- [ ] SUSFS patched and compile-verified.
- [ ] Device-validated boot.img produced.

This file is a planning and audit record only; it does not implement a kernel port or SUSFS.
