# SM-A217F (A21s) Linux 5.10 — DTBO ಹೊಂದಾಣಿಕೆ ತಿದ್ದುಪಡಿ

**ದಿನಾಂಕ: 20 ನವೆಂಬರ್ 2026. ಈ ಪ್ರಯೋಗ `a21s-susfs-port` branch ನಲ್ಲಿ ಮಾತ್ರ. Flash-ready ಅಲ್ಲ.**

## ಮೊದಲ ನಿಜವಾದ FDT overlay ಪರೀಕ್ಷೆ

[GitHub Actions #44731307145](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44731307145) ಯಲ್ಲಿ `dtc` ಮೂಲಕ ಐದು A21s overlays (`r00`, `r01`, `r02`, `r03`, `r06`) ಮತ್ತು `exynos/s5e3830.dtb` compile ಯಶಸ್ವಿಯಾಗಿದೆ. ಆದರೆ ಐದು overlay apply ಪರೀಕ್ಷೆಗಳೂ `FDT_ERR_NOTFOUND` ದೋಷದೊಂದಿಗೆ ವಿಫಲವಾದವು. **DTS compile pass ≠ overlay apply pass ≠ hardware boot pass.**

## ನಿಖರ source ಪರಿಶೀಲನೆ

- Linux 5.10 `arch/arm64/boot/dts/exynos/s5e3830.dts` ಯ `__symbols__` table ನಲ್ಲಿ ಒಟ್ಟು **355 symbols** ಕಂಡಿವೆ.
- A21s `__fixups__` table ನಲ್ಲಿ ಪ್ರತ್ಯೇಕ revisions ಗೆ **118–121 external symbols** ಬೇಕು. ಎಲ್ಲಾ revisions ಗಳಲ್ಲೂ ಇಲ್ಲದ **ಏಕೈಕ ಹೆಸರು `chosen`**.
- Linux 5.10 base DTS ಒಳಗೆ `/chosen` node ಈಗಾಗಲೇ ಇತ್ತು, ಆದರೆ `__symbols__` ಪಟ್ಟಿಯಲ್ಲಿ `chosen = "/chosen";` entry ಇರಲಿಲ್ಲ.
- Development branch ನಲ್ಲಿ base DTS ಗೆ ಕೇವಲ `chosen = "/chosen";` symbol ಸೇರಿಸಲಾಗಿದೆ (commit [218952a](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/commit/218952a1062344072df50b43c4bb14a419e20fcc)).
- [GitHub Actions ಮರುಪರೀಕ್ಷೆ #44731959612](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44731959612) ಇದರ ನಂತರ ಐದು overlays ಗಳನ್ನು *compiled Linux 5.10 base DTB* ಮೇಲೆಯೇ `fdtoverlay` ಮೂಲಕ apply ಮಾಡುತ್ತದೆ. **Action ಅಂತಿಮ ಫಲಿತಾಂಶ ಪರಿಶೀಲಿಸುವವರೆಗೆ PASS ಎಂದು ಹೇಳಬೇಡಿ.**

## ಮುಂದಿನ ನಿರ್ಬಂಧಗಳು

1. ಎಲ್ಲ ಐದು revisions ನ `fdtoverlay` ಯಶಸ್ವಿಯಾಗಬೇಕು. ವಿಫಲವಾದರೆ reports ನ specific missing references ಗುರುತಿಸಬೇಕು.
2. Apply ಯಶಸ್ಸು ಮಾತ್ರ A21s panel, charger, modem, touchscreen, camera ಮತ್ತು DTB bindings ಸರಿಯಾಗಿವೆ ಎಂದಲ್ಲ; ಇವುಗಳ ನೈಜ driver/hardware ಪರೀಕ್ಷೆ ಅನಿವಾರ್ಯ.
3. SUSFS + KernelSU functional source integration ಹಾಗೂ Linux 5.10 full image linking ಸ್ವತಂತ್ರವಾಗಿ ದೃಢಪಡಿಸಬೇಕು.
4. Original `boot.img` parameters, actual ramdisk/DTB sizes ಮತ್ತು **37,748,736-byte** boot partition ಮಿತಿ ಪಾಲಿಸಬೇಕು.
5. ಸುರಕ್ಷಿತ original restore ಮತ್ತು physical SM-A217F boot validation ಇಲ್ಲದೆ ಯಾವುದೇ image ಅನ್ನು **flash-ready** ಎಂದು ಗುರುತಿಸಬಾರದು.
