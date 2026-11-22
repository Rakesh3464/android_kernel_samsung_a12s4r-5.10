#!/usr/bin/env bash
# Source-only inspection for the Samsung Galaxy A21s Linux 5.10 port.
# This is NOT a kernel port, and produces no boot.img.
set -euo pipefail
OUT="${1:-a21s-port-audit}"
mkdir -p "$OUT"
{
  printf 'SOURCE VERSION: '
  sed -n '1,6p' Makefile | tr '\n' ' '
  printf '\n\nTarget build variables:\n'
  grep -E '^export (TARGET_SOC|PLATFORM_VERSION|ANDROID_MAJOR_VERSION)=' Makefile || true
  printf '\nA21s and Exynos 850 defconfigs:\n'
  find arch/arm64/configs -type f \( -iname '*a21*' -o -iname '*850*' -o -iname '*3830*' \) 2>/dev/null | sort | head -100 || true
  printf '\nA21s / Exynos DTS and DTI candidates:\n'
  find arch/arm64/boot/dts -type f \( -iname '*a21*' -o -iname '*850*' -o -iname '*3830*' \) 2>/dev/null | sort | head -150 || true
  printf '\nBuild configs:\n'
  find . -maxdepth 4 -type f -name 'build.config*' | sort | head -80 || true
  printf '\nRequired work before any flashable image:\n'
  printf '1. Port/validate A21s DTS and drivers against the actual 5.10 API.\n'
  printf '2. Build tested A21s kernel and DTB; validate module ABI and vendor compatibility.\n'
  printf '3. Assemble a valid Android boot image and enforce 36 MiB partition limit.\n'
  printf '4. Boot-test with recovery path; do not flash a source-only artifact.\n'
} >"$OUT/report.txt"
cat "$OUT/report.txt"
