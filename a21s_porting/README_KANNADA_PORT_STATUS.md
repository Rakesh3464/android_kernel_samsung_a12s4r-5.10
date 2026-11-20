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

## ಏನು ಇನ್ನೂ ಬಾಕಿ?

- **SUSFS patch ಹೊಂದಾಣಿಕೆಯಾಗಿಲ್ಲ.** 5.10 patch dry-run ನಲ್ಲಿ ಕನಿಷ್ಠ ಎರಡು failed hunks ಇವೆ: `fs/namespace.c` ಮತ್ತು `fs/proc/base.c`. `KernelSU` ಮೂಲ source directory ನಿರೀಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿ ಇಲ್ಲ. Dry-run ಪರೀಕ್ಷೆಯ ಫಲಿತಾಂಶವು GitHub Actions [44681104818](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44681104818) ನಲ್ಲಿ ಇದೆ. SUSFS ಇನ್ನೂ integrate ಆಗಿಲ್ಲ.
- ಪೂರ್ಣ Linux 5.10 `Image` compilation ಮತ್ತು ಅದರ ಫಲಿತಾಂಶವನ್ನು ಖಚಿತಪಡಿಸುವುದು.
- A21s ನ camera, sensors, charging/PMIC, modem, storage, audio ಹಾಗೂ device-specific DTBO bindings ಪರಿಶೀಲನೆ.
- User ROM / One UI 9 vendor ABI, boot header v2, ramdisk, DTB ಮತ್ತು bootloader ಹೊಂದಾಣಿಕೆ.
- A21s boot partition ಗಾತ್ರ 37,748,736 bytes. ಹಿಂದಿನ A12s-5.10 + A21s hybrid ಕನಿಷ್ಠ 39,780,368 bytes ಎಂದು preflight ವರದಿ ತೋರಿಸಿತ್ತು. 36 MiB ಮಿತಿಗೆ ಹೊಂದುವ ಹೊಸ Image ಇನ್ನೂ ಸಿದ್ಧವಾಗಿಲ್ಲ.
- ಮೂಲ firmware backup ಮತ್ತು ವಿಶ್ವಾಸಾರ್ಹ recovery ವಿಧಾನ ಹೊಂದಿಸಿ, **ನಿಜವಾದ A21s device ಮೇಲೆ** ಯಶಸ್ವಿ boot ಪರೀಕ್ಷೆ.

## ZIP ಕುರಿತು

ಈ ZIP ನಲ್ಲಿ source, configuration fragments ಮತ್ತು ಪರೀಕ್ಷೆಗಳಿಗೆ ಬೇಕಾದ scripts/ವರದಿಗಳು ಮಾತ್ರ ಇವೆ. **Kernel Image, SUSFS-ready boot.img, ಅಥವಾ flash-ready ZIP ಇಲ್ಲ.**

**ಮುಂದಿನ ಸುರಕ್ಷಿತ ಹಂತ:** Full kernel build log ಮತ್ತು SUSFS failed hunks ಪರಿಹರಿಸಿ, ನಂತರ A21s ನ hardware ಮೇಲೆ ನಿಯಂತ್ರಿತ boot validation ನಡೆಸುವುದು.
