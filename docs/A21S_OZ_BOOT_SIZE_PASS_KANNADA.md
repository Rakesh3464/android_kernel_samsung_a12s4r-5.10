# Samsung Galaxy A21s SM-A217F — Linux 5.10 size fit measured, SUSFS integration pending

**ಪರಿಶೀಲನೆ: 20 ನವೆಂಬರ್ 2026. ಇದು flash-ready boot.img ಅಲ್ಲ.**

## 1) Clang `-Oz` BOE 8A6220/TD4150 ಪ್ರಯೋಗ: ಯಶಸ್ವಿ

- GitHub Actions [#44721849406](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44721849406) **SUCCESS**.
- `Image`: **34,714,112 bytes** (Linux 5.10, BOE TD4150 ಮತ್ತು Synaptics touchscreen experimental config).
- ಹಿಂದಿನ BOE `Image` ಗಾತ್ರ: **36,870,656 bytes**. ಕಡಿತ: **2,156,544 bytes**.
- Original SM-A217F Android boot v2 ನ ramdisk **1,462,536 bytes**, DTB **140,292 bytes**, page size **2048**, Samsung footer **16 bytes** ಎಂಬ ಗಾತ್ರಗಳನ್ನೇ ಬಳಸಿದರೆ:
  - ಅಂದಾಜು boot image: **36,323,344 bytes**.
  - Phone boot partition ಮಿತಿ: **37,748,736 bytes**.
  - ಉಳಿದಿರುವ ಗಾತ್ರ: **1,425,392 bytes**.
- ಇದು *packing-size-only* pass. ಹಳೆಯ ramdisk/DTB ಗಳು ಹೊಸ 5.10 Kernel ಜೊತೆ boot ಆಗುತ್ತವೆ ಎಂಬ ಸಾಕ್ಷಿಯಲ್ಲ.
- `mm/mremap.c` ಯ `BUILD_BUG()` check ತೆಗೆದುಹಾಕಿಲ್ಲ; ಆ ಒಂದು object `-O2` ನಲ್ಲಿ ಉಳಿದಿದೆ; ಉಳಿದ build `-Oz`.

## 2) SUSFS Object compile: ಯಶಸ್ವಿ, ಆದರೆ final Image ಗೆ ಸೇರಿರುವುದಿಲ್ಲ

- GitHub Actions [#44724199462](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44724199462) **SUCCESS**; `fs/susfs.o` compile exit code `0`.
- `CONFIG_KSU_SUSFS=y` ಮತ್ತು `CONFIG_KSU_SUSFS_ENABLE_LOG=y` **temporary compile config**.
- Samsung-specific patch ಕೆಲವು hunks `fuzz` ಬಳಸುತ್ತವೆ; production code review ಬಾಕಿ.
- KernelSU in-tree source standard location ಗಳಲ್ಲಿ ಲಭ್ಯವಿಲ್ಲ; SUSFS support ಕೆಲಸ ಮಾಡುತ್ತದೆ ಅಥವಾ modules link ಆಗುತ್ತವೆ ಎಂದು ಹೇಳಲಾಗುವುದಿಲ್ಲ.

## 3) SUSFS + BOE `-Oz` full Image linker proof: ಪರೀಕ್ಷೆ

- [New Github Actions full-link + `-Oz` #44730026430](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44730026430)
- Disposable checkout ನಲ್ಲಿ `fs/Makefile` ಗೆ `obj-$(CONFIG_KSU_SUSFS) += susfs.o` ಸೇರಿಸಿ, archive ಸದಸ್ಯರಲ್ಲಿಯೂ `susfs.o` ಇರುವುದನ್ನು ಪರೀಕ್ಷಿಸುತ್ತದೆ.
- Final `Image` ಗಾತ್ರವನ್ನು ಮತ್ತೆ ಮಿತಿಗೆ ಹೋಲಿಸುತ್ತದೆ; Image / `boot.img` binaries GitHub artifact ಗೆ upload ಮಾಡುವುದಿಲ್ಲ.
- **ಈ build ಫಲಿತಾಂಶ ಖಚಿತವಾಗುವವರೆಗೆ SUSFS full-link success ಎಂದು ಹೇಳಬೇಡಿ.**

## 4) Flash safety gate

- Correct A21s DTB/DTBO board revision/panel drivers, modem, battery, charging, touch, sensors, audio ಮತ್ತು ROM vendor ABI ಪರಿಶೀಲಿಸಬೇಕು.
- Actual final Image + DTB + ramdisk byte counts ಬಳಸಿಕೊಂಡು boot v2 re-packing ಮತ್ತು partition-size gate ಮತ್ತೆ ಮಾಡಬೇಕು.
- KernelSU/SUSFS full compile, linking, runtime hooks ಮತ್ತು boot behavior ಪರಿಶೀಲಿಸಬೇಕು.
- User boot reference SHA-256: `af3c2406848c71639b420cf4f709a28550f7eae05caf65731db8fac50f897928` (stock / reference image, not 5.10).
- Original boot restore ಮತ್ತು controlled hardware test ಸಿದ್ಧವಿರುವುದನ್ನು ಖಚಿತಪಡಿಸಬೇಕು.

**ಇನ್ನೂ flash-ready boot.img ಉತ್ಪಾದಿಸಿಲ್ಲ ಅಥವಾ phone ಗೆ flash ಮಾಡಿಲ್ಲ.** ಮೂಲ kernel branch `android13-5.10-lts` ಬದಲಾಗಿಲ್ಲ.
