# Samsung Galaxy A21s — Linux 5.10 / SUSFS Port ಸ್ಥಿತಿ

**ಮುಖ್ಯ ಸೂಚನೆ: ಇದು SOURCE KIT ಮಾತ್ರ. `boot.img` ಅಲ್ಲ. Recovery ಅಥವಾ Odin ಮೂಲಕ flash ಮಾಡಬೇಡಿ.**

## GitHub ನಲ್ಲಿ ಈಗಿನ ಕೆಲಸ

- ಮೂಲ Kernel 5.10.274 branch ಬದಲಾಯಿಸದೆ, `a21s-susfs-port` ಎಂಬ ಪ್ರತ್ಯೇಕ development branch ಬಳಸಲಾಗಿದೆ.
- A21s ನ ಐದು DTBO revisions (`r00`, `r01`, `r02`, `r03`, `r06`) ಸಂಪೂರ್ಣ DTS sourceಗಳನ್ನು `arch/arm64/boot/dts/samsung/a21s/` ಗೆ ಸೇರಿಸಲಾಗಿದೆ. `CONFIG_A21S_EXPERIMENTAL_DTBO` default OFF ಆಗಿದೆ.
- `atlas-new` ನಿಂದ TD4150, HX83104, NT36575 panel source families ಗಳ ಒಟ್ಟು 22 ಫೈಲ್‌ಗಳನ್ನು ಸೇರಿಸಲಾಗಿದೆ. ಸಂಬಂಧಿಸಿದ Kconfig/Makefile entries default OFF.
- ಮೂರು A21s panel objects `td4150.o`, `hx83104.o`, `nt36575.o` Linux 5.10 ವಿರುದ್ಧ ಯಶಸ್ವಿಯಾಗಿ compile ಆಗಿವೆ: GitHub Actions run [44679433718](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44679433718).
- A21s ನ ಐದು DTBO revisions ಅನ್ನು 5.10 build system ನಲ್ಲಿ compile ಮಾಡುವ GitHub Actions ಹಂತ ಯಶಸ್ವಿಯಾಗಿದೆ: [44680936353](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44680936353). **ಇದು phone boot ಪರೀಕ್ಷೆಯಲ್ಲ.**
- ಹಳೆಯ A21s hardware log ನಲ್ಲಿ `/sys/class/lcd/panel/lcd_type` = `BOE_8A6220`. ಸೇರಿಸಿದ `td4150_a21s_panel.h` ನಲ್ಲಿ `.id = 0x8A6220` ಹೊಂದಿದೆ. ಆದ್ದರಿಂದ ನಿರ್ದಿಷ್ಟ panel ಆಯ್ಕೆಯಾಗಿ TD4150 ಬಳಸುವ experimental fragment `configs/a21s-boe-8a6220-experimental.fragment` ಸಿದ್ಧವಾಗಿದೆ. ಆ log ನಲ್ಲಿ Synaptics TCM SPI touchscreen ಕೂಡ ಗುರುತಾಗಿದೆ.
- Config ಮತ್ತು Device Tree audit ವರದಿಗಳು `docs/A21S_419_TO_510_DIFF.md` ಮತ್ತು `a21s_porting/` ನಲ್ಲಿ ಇವೆ.

## ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ A21s boot.img — ನಿಖರ ಮಾಹಿತಿ

- ಮೂಲ `boot-a21s.img` ಪರಿಶೀಲನೆಯ ಪ್ರಕಾರ model **SM-A217F**, device `a21s`, kernel `4.19.325-g4a2052095396` (5.10 ಅಲ್ಲ).
- Samsung `ANDROID!` boot header **v2**, page size **2048**, kernel size **34,068,504 bytes**, ramdisk GZIP size **1,462,536 bytes**, DTB table size **140,292 bytes**.
- Samsung `SEANDROIDENFORCE` footer ಇದೆ. KernelSU log string ಸಿಕ್ಕಿದೆ, ಆದರೆ SUSFS ಇರುವುದನ್ನು ದೃಢಪಡಿಸಿಲ್ಲ.
- Ramdisk `build.prop` ಯಲ್ಲಿ Android 12 build `A217FXXSCDXE2` ಇದೆ. ಇದು **ಪ್ರಸ್ತುತ custom ROM ಆವೃತ್ತಿಯ ಸಾಕ್ಷಿ ಅಲ್ಲ**.
- Kernel DTB compatible `samsung,exynos850` ಮತ್ತು pinctrl `samsung,exynos3830-pinctrl`. 5.10 source DTB compatible `samsung,exynos3830`/ `samsung,s5e3830-pinctrl` ಇರುವುದರಿಂದ Device Tree ಹೊಂದಾಣಿಕೆ ವಿಶೇಷವಾಗಿ ಪರಿಶೀಲಿಸಬೇಕು.
- Original boot SHA-256: `af3c2406848c71639b420cf4f709a28550f7eae05caf65731db8fac50f897928`.
- ಹೆಚ್ಚಿನ ಮಾಹಿತಿ: [docs/A21S_UPLOADED_BOOT_BASELINE.md](../docs/A21S_UPLOADED_BOOT_BASELINE.md). ಮೂಲ boot binary GitHub ಗೆ upload ಮಾಡಿಲ್ಲ.

## ಏನು ಇನ್ನೂ ಬಾಕಿ?

- **SUSFS patch ಹೊಂದಾಣಿಕೆಯಾಗಿಲ್ಲ.** 5.10 patch dry-run ನಲ್ಲಿ ಕನಿಷ್ಠ ಎರಡು failed hunks ಇವೆ: `fs/namespace.c` ಮತ್ತು `fs/proc/base.c`. `KernelSU` ಮೂಲ source directory ನಿರೀಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿ ಇಲ್ಲ. Dry-run ಪರೀಕ್ಷೆಯ ಫಲಿತಾಂಶವು GitHub Actions [44681104818](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44681104818) ನಲ್ಲಿ ಇದೆ. SUSFS ಇನ್ನೂ integrate ಆಗಿಲ್ಲ.
- Linux 5.10 `Image` ಈಗಾಗಲೇ GitHub Actions run [44680936353](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44680936353) ನಲ್ಲಿ **compile ಯಶಸ್ವಿಯಾಗಿದೆ**, ಆದರೆ ಅದು A12s ಆಧಾರಿತ experimental configuration; **A21s boot-test / ABI verification ಅಥವಾ partition-fit approval ಅಲ್ಲ**.
- A21s ನ camera, sensors, charging/PMIC, modem, storage, audio ಹಾಗೂ device-specific DTBO bindings ಪರಿಶೀಲನೆ.
- User ROM / One UI 9 vendor ABI, boot header v2, ramdisk, DTB ಮತ್ತು bootloader ಹೊಂದಾಣಿಕೆ.
- A21s boot partition ಗಾತ್ರ 37,748,736 bytes. ಹಿಂದಿನ A12s-5.10 + A21s hybrid ಕನಿಷ್ಠ 39,780,368 bytes ಎಂದು preflight ವರದಿ ತೋರಿಸಿತ್ತು. 36 MiB ಮಿತಿಗೆ ಹೊಂದುವ ಹೊಸ Image ಇನ್ನೂ ಸಿದ್ಧವಾಗಿಲ್ಲ.
- ಮೂಲ firmware backup ಮತ್ತು ವಿಶ್ವಾಸಾರ್ಹ recovery ವಿಧಾನ ಹೊಂದಿಸಿ, **ನಿಜವಾದ A21s device ಮೇಲೆ** ಯಶಸ್ವಿ boot ಪರೀಕ್ಷೆ.

## ZIP ಕುರಿತು

ಈ ZIP ನಲ್ಲಿ source, configuration fragments ಮತ್ತು ಪರೀಕ್ಷೆಗಳಿಗೆ ಬೇಕಾದ scripts/ವರದಿಗಳು ಮಾತ್ರ ಇವೆ. **Kernel Image, SUSFS-ready boot.img, ಅಥವಾ flash-ready ZIP ಇಲ್ಲ.**

**ಮುಂದಿನ ಸುರಕ್ಷಿತ ಹಂತ:** Full kernel build log ಮತ್ತು SUSFS failed hunks ಪರಿಹರಿಸಿ, ನಂತರ A21s ನ hardware ಮೇಲೆ ನಿಯಂತ್ರಿತ boot validation ನಡೆಸುವುದು.
