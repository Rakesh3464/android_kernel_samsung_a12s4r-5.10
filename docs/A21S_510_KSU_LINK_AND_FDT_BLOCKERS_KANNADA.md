# SM-A217F Linux 5.10 — SUSFS Full Link & A21s DTBO Root-Cause Audit

**20 ನವೆಂಬರ್ 2026. Development-only. ಇದು flash-ready image ಅಲ್ಲ.**

## 1. Linux 5.10 + SUSFS full-link: ನಿರ್ಣಾಯಕ ದೋಷ

[GitHub Actions #44730715284](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44730715284) ನಲ್ಲಿ kernel source compile, `fs/susfs.o` build, BOE TD4150 configuration ಯಶಸ್ವಿಯಾಗಿ ಮುಗಿದಿವೆ; **full Image linking ವಿಫಲವಾಗಿದೆ**.

`ld.lld: error: undefined symbol` ಉದಾಹರಣೆಗಳು:

- `ksu_handle_setresuid`, `ksu_handle_sys_reboot`
- `__ksu_is_allow_uid_for_current`, `ksu_handle_faccessat`, `ksu_su_compat_enabled`
- `ksu_handle_sys_read`, `ksu_is_init_rc_hook_enabled`
- `ksu_handle_vfs_fstat`, `ksu_handle_stat`
- `ksu_preinit_handle_post_execveat`, `ksu_handle_post_execveat_sucompat`
- `ksu_handle_execveat_sucompat`, `ksu_setup_preinit_file`, `ksu_handle_execveat`
- `setup_selinux`, `susfs_is_current_ksu_domain`, `susfs_ksu_sid`, `susfs_priv_app_sid`, `ksu_selinux_hide_running`, `fake_status`.

**ಅರ್ಥ:** KernelSU ಅಗತ್ಯ implementation / SELinux SUSFS glue ಇಲ್ಲಿ link ಆಗುತ್ತಿಲ್ಲ. ಕೇವಲ `CONFIG_KSU_SUSFS=y` ಮತ್ತು `fs/susfs.o` compile ಸಾಕಾಗುವುದಿಲ್ಲ. Function ಹೆಸರುಗಳಿಗೆ ಖಾಲಿ stubs ಸೇರಿಸಿ link pass ಮಾಡುವುದು *ಸರಿಯಾದ ಪರಿಹಾರವಲ್ಲ*. ನಿಜವಾದ ಹೊಂದಾಣಿಕೆಯ KernelSU source ಸೇರಿಸಿ, SUSFS ಯ `10_enable_susfs_for_ksu.patch` version compatibility ಪರಿಶೀಲಿಸಬೇಕು. Original vendor hooks ಗೆ KernelSU variant/version ಹೊಂದಾಣಿಕೆ ಪರಿಶೀಲಿಸಬೇಕು.

**ಈ build ನ actual `Image` ಸೃಷ್ಟಿಯಾಗಿಲ್ಲ; ಅಂತಿಮ boot.img ಗಾತ್ರ ತಿಳಿದಿಲ್ಲ.**

## KernelSU source ಆಯ್ಕೆ — ನಿಜವಾದ API ಹೊಂದಾಣಿಕೆ ಪರಿಶೀಲನೆ

[GitHub Actions #44739798930](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44739798930) ನಲ್ಲಿ pinned upstream source ಅನ್ನು `undefined symbol` ಪಟ್ಟಿಯ **20 ಹೆಸರುಗಳಿಗೆ** ಹುಡುಕಲಾಗಿದೆ:

| Source | 20ರಲ್ಲಿ source occurrences ಪತ್ತೆಯಾದ ಹೆಸರುಗಳು |
|---|---:|
| KernelSU-Next `aa235b99574b` | 10 |
| tiann/KernelSU `ff70c90d6de4` | 8 |
| **LyraVoid/FinaSU `f96445f966a2`** | **20** |

`FinaSU` ಅತ್ಯಂತ ನಂಬಬಹುದಾದ *source candidate*. ಆದರೆ search ಫಲಿತಾಂಶದಿಂದ function definitions ಸರಿಯಾಗಿವೆ, signature ಹೊಂದಿದೆ, ಅಥವಾ compile/link success ಸಿಗುತ್ತದೆ ಎಂದು ಹೇಳಲಾಗುವುದಿಲ್ಲ.

[**FinaSU + SUSFS + BOE Linux 5.10 isolated full-build trial #44740301678**](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44740301678) ಪ್ರಾರಂಭಿಸಲಾಗಿದೆ. ಈ workflow actual kernel source checkout ನಲ್ಲಿ (GitHub runner ಒಳಗೆ ಮಾತ್ರ) `kernel/setup.sh --dir` ಮೂಲಕ driver integration, `CONFIG_KSU_HOOK_SUSFS_INLINE=y`, `CONFIG_KALLSYMS_ALL=y`, `CONFIG_KSU_SUSFS=y`, BOE TD4150 options ಮತ್ತು `-Oz` Image build ಪರೀಕ್ಷಿಸುತ್ತದೆ. No flashable binaries exported. ಫಲಿತಾಂಶ ಬರುವವರೆಗೆ trial ಯಶಸ್ವಿ ಎಂದು ಘೋಷಿಸಬಾರದು.

## 2. A21s 4.19 overlay → Linux 5.10 base DTB ಇನ್ನೂ ವಿಫಲ

- [Initial overlay test #44731307145](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44731307145): ಐದು revisions ಗೂ `FDT_ERR_NOTFOUND`.
- `chosen = "/chosen";` symbol ಸೇರಿಸಿದ ನಂತರವೂ [#44731959612](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44731959612) ಫಲಿತಾಂಶ **fail**.
- [Detailed audit #44733101076](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44733101076): ಎಲ್ಲಾ ಐದು revisions ನಲ್ಲಿ external symbol ಹೆಸರು, symbol destination path, fixup source property, overlay symbol path ಪರೀಕ್ಷೆಯಲ್ಲಿ **0 missing**. Overlay `/__symbols__` ತೆಗೆದ *test copy* ಗಳೂ apply ಆಗಲಿಲ್ಲ.
- [Fast local-fixup audit #44738306326](https://github.com/Rakesh3464/android_kernel_samsung_a12s4r-5.10/actions/runs/44738306326): **GitHub Actions SUCCESS** ಎಂದರೆ diagnostic process ಯಶಸ್ವಿಯಾಗಿದೆ, overlay apply ಯಶಸ್ಸಲ್ಲ. `r00` ನಲ್ಲಿ 193 local-fixup nodes / 119 properties; `r01/r02/r03/r06` ನಲ್ಲಿ ಪ್ರತಿ revision 201 nodes / 129 properties. ಎಲ್ಲಾ revisions ನಲ್ಲಿ **missing nodes 0, missing properties 0, offsets out of bounds 0**.
- Original, `__symbols__` ಇಲ್ಲದೆ, `__local_fixups__` ಇಲ್ಲದೆ, ಎರಡೂ metadata ಇಲ್ಲದೆ ಪರೀಕ್ಷಿಸಿದ *temporary DTBO copies* — **20/20 apply ಪ್ರಯತ್ನಗಳೂ ವಿಫಲ**.

**ಅರ್ಥ:** `FDT_ERR_NOTFOUND` ಇನ್ನುಳಿದಿದೆ; ಅದರ ಸಂಪೂರ್ಣ root cause ಕಂಡಿಲ್ಲ. External/local symbol fixups ಮುಗಿದಿವೆ ಎಂದು ತಪ್ಪಾಗಿ flash-ready ಎಂದು ಹೇಳಬಾರದು. ಪ್ರತಿ root overlay fragment target ಹಾಗೂ phandle resolution ನಿಜವಾಗಿ ಪರಿಶೀಲಿಸುವುದು ಮುಂದಿನ engineering task.

## 3. ಸುರಕ್ಷಿತ release gate

- BOE `-Oz` kernel size ಪ್ರಯೋಗದ `Image=34,714,112 bytes` ಎಂಬುದು **SUSFS ಪೂರ್ಣ link ಇಲ್ಲದ ಹಳೆಯ build**. ಅದು A21s actual flashed boot image ಅಲ್ಲ.
- Original boot image `Linux 4.19.325`, SM-A217F Android boot v2 reference.
- Actual Linux 5.10 + matching A21s DTB/DTBO + fully-linked KernelSU/SUSFS + ROM vendor ABI ಪರಿಶೀಲನೆ **ಇನ್ನೂ ಇಲ್ಲ**.
- Final image actual size `<= 37,748,736 bytes` ಮತ್ತು actual SM-A217F boot test ಅಗತ್ಯ.

**ಯಾವುದೇ `boot.img` ಅಥವಾ ಪರೀಕ್ಷಾ DTBOಗಳನ್ನು ಫೋನ್‌ಗೆ flash ಮಾಡಬೇಡಿ.**

