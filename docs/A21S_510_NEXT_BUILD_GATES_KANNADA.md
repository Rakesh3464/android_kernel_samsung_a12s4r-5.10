# Samsung A21s SM-A217F — Linux 5.10 Next Build Gates (20 Nov 2026)

> **ಯಾವುದೇ `boot.img` flash ಮಾಡುವುದಿಲ್ಲ.** ಈ ಹಂತ GitHub Actions ನ ತಾತ್ಕಾಲಿಕ checkout ಗಳಲ್ಲಿ ನಡೆಯುವ compiler ಪರೀಕ್ಷೆ ಮಾತ್ರ.

## 1. ಗಾತ್ರದ ಗುರಿ

- ಹಿಂದೆ ಪೂರ್ಣ compile ಆದ BOE TD4150 / Synaptics ARM64 Linux 5.10 `Image`: **36,870,656 bytes**.
- ನಿಮ್ಮ SM-A217F ಮೂಲ `boot.img` v2, 2048-byte page alignment, ಮೂಲ ramdisk/DTB ಗಾತ್ರಗಳ ಆಧಾರದಲ್ಲಿ ಅಂದಾಜು boot image: **38,479,888 bytes**.
- A21s boot partition ಗಾತ್ರ **37,748,736 bytes**; **731,152 bytes** ಹೆಚ್ಚು.
- ಹಿಂದಿನ ramdisk/DTB ಗಾತ್ರಗಳು ಅಷ್ಟೇ ಉಳಿದರೆ, ARM64 `Image` ಗರಿಷ್ಠ **36,139,008 bytes** ಆಗಬೇಕು. SUSFS ಸೇರಿಸಿದ ನಂತರ ಈ ಲೆಕ್ಕ ಮತ್ತೆ ಮಾಡಬೇಕು.
- [BOE + Clang `-Oz` Size Probe](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44720986985) ಮೊದಲ ಪ್ರಯತ್ನ **fail**: `mm/mremap.c:419` ಯ `BUILD_BUG` assertion trigger ಆಗಿದೆ. Assertion ತೆಗೆದಿಲ್ಲ.
- [Selective `mremap.c -O2` Optimization Probe](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44721849406): ಆ ಒಂದು source file ಗೆ `-O2`, ಉಳಿದಂತೆ `-Oz` compiler ಪ್ರಯೋಗ. ಇದು experimental ಮಾತ್ರ. Outcome ಅನ್ನು CI ನಲ್ಲಿ ಪರಿಶೀಲಿಸಬೇಕು.

## 2. SUSFS integration ಪರಿಶೀಲನೆ

- [SUSFS vendor patch dry-run](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44685770287): **pass**, ಆದರೆ ಕೆಲವು hunks `fuzz 1/2` ಮೇಲೆ ಅವಲಂಬಿತ. ಕೇವಲ dry-run.
- [Strict patch apply probe](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44721235538): **fail**; `--fuzz=0` ನಲ್ಲಿ vendor source contexts ಹೊಂದಲಿಲ್ಲ.
- [Disposable patch+SUSFS source compile probe](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44721648493): patch ಅನ್ವಯಿಸಲ್ಪಟ್ಟರೂ `fs/susfs.o` **compile fail** — `SUSFS_LOGI_RL` macro/function declarations missing. ಇದು kernel integration ಪೂರ್ಣಗೊಂಡಿಲ್ಲದಿರುವುದಕ್ಕೆ ಸ್ಪಷ್ಟ ಸಾಕ್ಷಿ.
- [SUSFS macro definition diagnostic](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44722244307): upstream source/Kconfig diagnostics ಸಂಗ್ರಹಿಸುವ ಹೊಸ ಪರೀಕ್ಷೆ; CI run ಫಲಿತಾಂಶ ಪರಿಶೀಲಿಸಬೇಕು.
- In-tree KernelSU source `KernelSU` ಅಥವಾ `drivers/kernelsu` ಸಾಮಾನ್ಯ ಸ್ಥಳಗಳಲ್ಲಿ ಸಿಕ್ಕಿಲ್ಲ; `arch/arm64/configs/ksu.config` ಇರುವುದರಿಂದ ಮಾತ್ರ functional KernelSU ಇರುವುದಿಲ್ಲ.
- **SUSFS + KernelSU ಪೂರ್ಣ compile/link/run ಇನ್ನೂ ಪೂರ್ತಿಯಾಗಿಲ್ಲ.**

## 3. ಸುರಕ್ಷಿತ release gate

1. BOE/TD4150, Synaptics, storage, modem, audio, camera, charging, fingerprints ಮತ್ತು device DTBO bindings ಸಾಮರ್ಥ್ಯ ದೃಢಪಡಿಸಬೇಕು.
2. KernelSU/SUSFS header+Kconfig+source ಪ್ರತ್ಯೇಕ ಪರಿಸರದಲ್ಲಿ compiler ಮತ್ತು linker ಮಟ್ಟದಲ್ಲಿ ಸಾಬೀತಾಗಬೇಕು; patch hunks ಕೈಯಾರೆ review ಆಗಬೇಕು.
3. Android boot v2 `boot.img` actual ramdisk + DTB ಜೊತೆಗೆ **37,748,736 bytes ಅಥವಾ ಕಡಿಮೆ** ಆಗಬೇಕು.
4. Original boot backup SHA-256: `af3c2406848c71639b420cf4f709a28550f7eae05caf65731db8fac50f897928`. Restore ವಿಧಾನ ಸ್ಪಷ್ಟವಾಗಿರಬೇಕು.
5. SM-A217F ಸಾಧನದಲ್ಲಿ ನಿಯಂತ್ರಿತ boot test ಮತ್ತು ಅಗತ್ಯವಾದ vendor/ROM compatibility ಪರಿಶೀಲನೆ ಇಲ್ಲದೆ **flash-ready** ಎಂದು ಗುರುತಿಸಬಾರದು.

ಎಲ್ಲ ಬದಲಾವಣೆಗಳು `a21s-susfs-port` development branch ಮತ್ತು GitHub Actions disposable checkout ಗೆ ಮಾತ್ರ. ಮೂಲ `android13-5.10-lts` branch ಮತ್ತು ಫೋನ್‌ನ boot partition ಅನ್ನು ಈ ಪರೀಕ್ಷೆಗಳು ಬದಲಾಯಿಸುವುದಿಲ್ಲ.
