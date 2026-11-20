# Samsung Galaxy A21s (Exynos 850) — Linux 5.10 experimental source kit

**⚠️ SOURCE ONLY — NOT FLASHABLE. THIS IS NOT A BOOT.IMG.**

This development branch includes:
- 5 complete A21s reference DTBO DTS files (r00, r01, r02, r03, r06) in `a21s_porting/dts_reference/` from the Linux 4.19 atlas source.
- TD4150, HX83104, NT36575 panel driver family sources imported from atlas-new and registered behind **disabled-by-default** kernel config choices on this branch.
- Automated 4.19 versus 5.10 source/defconfig audits and standalone DTS compilation checks.
- Experimental CI panel-object compilation for the 5.10 source, which is **NOT** proof of actual phone compatibility.
- Hardware comparison report in `docs/A21S_419_TO_510_DIFF.md`.

## Required unresolved hardware work

1. Validate the actual A21s panel variant. Provided hardware logs previously identified `BOE_8A6220` but do not establish which of the panel driver choices applies.
2. Port and compile A21s-specific Synaptics touch support and applicable sensors, camera, PMIC and audio drivers; compare with current 5.10 vendor kernel interfaces.
3. Reconcile A21s DTBO fragment targets with Linux 5.10 `s5e3830.dts`, validate correct hardware revision and overlay application. Do not deploy standalone dtc outputs.
4. Build full kernel and dtbs successfully. Validate that kernel format/size + ramdisk + DTB fit the A21s **37,748,736-byte** boot partition.
5. Validate boot header v2, ramdisk and vendor ABI. Preserve known-working recovery path and OEM firmware.
6. KernelSU config fragment alone **does not** mean SUSFS is integrated; pin a compatible SUSFS + KernelSU revision and validate patch application and compile separately.
7. Perform a physical-device boot test; without it there is no flash-ready build.

## Source kit download

GitHub Actions workflow `.github/workflows/a21s-source-kit.yml` packages only the above development sources, documentation and tests as a ZIP artifact for inspection. **Do not use the ZIP in recovery or Odin.**

## One UI 9

One UI 9 Android compatibility is **not established** by Linux 5.10 kernel version alone. It requires ROM/vendor/kernel ABI testing, not just swapping `Image`.
