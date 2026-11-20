#!/usr/bin/env bash
# Disposable SUSFS *source compilation diagnostic* for Samsung Exynos850 5.10.
# DO NOT run in an actual device source checkout if you expect no changes:
# the caller MUST supply an ephemeral GitHub Actions checkout as $1.
set -euo pipefail
kernel_dir="${1:?temporary kernel source directory required}"
upstream_dir="${2:?susfs git checkout required}"
report_dir="${3:?report directory required}"
mkdir -p "$report_dir"
kernel_dir="$(realpath "$kernel_dir")"
upstream_dir="$(realpath "$upstream_dir")"
report_dir="$(realpath "$report_dir")"

# Fail closed if the upstream revision or its files move.
patchfile="$upstream_dir/kernel_patches/50_add_susfs_in_gki-android13-5.10.patch"
test -s "$patchfile"
test -s "$upstream_dir/kernel_patches/fs/susfs.c"
test -s "$upstream_dir/kernel_patches/include/linux/susfs.h"
echo 'EXPERIMENTAL ONLY - no kernel binaries or flash files will be exported.' > "$report_dir/DO_NOT_FLASH.txt"
git -C "$kernel_dir" rev-parse HEAD > "$report_dir/target-source-sha.txt"
git -C "$upstream_dir" rev-parse HEAD > "$report_dir/susfs-upstream-sha.txt"
python3 "$kernel_dir/a21s_porting/adapt_susfs_patch.py" \
  --patch "$patchfile" --kernel "$kernel_dir" --output "$report_dir/samsung-adapted.patch" \
  > "$report_dir/adapt.log" 2>&1

# Work exclusively inside Actions checkout; never commit to the real branch.
(cd "$kernel_dir" && patch --batch --forward --fuzz=0 -p1 < "$report_dir/samsung-adapted.patch") \
  > "$report_dir/patch-apply.log" 2>&1
cp "$upstream_dir/kernel_patches/fs/susfs.c" "$kernel_dir/fs/susfs.c"
for h in "$upstream_dir"/kernel_patches/include/linux/susfs*.h; do
  test -s "$h" || continue
  cp "$h" "$kernel_dir/include/linux/$(basename "$h")"
done
test -s "$kernel_dir/fs/susfs.c"
test -s "$kernel_dir/include/linux/susfs.h"

# Kconfig option is missing without a matching KernelSU integration; define
# it in the DISPOSABLE checkout so we can compile-TEST the SUSFS object.
if ! grep -rqE '^config KSU_SUSFS$' "$kernel_dir/fs/Kconfig" "$kernel_dir/drivers/Kconfig" "$kernel_dir/KernelSU" 2>/dev/null; then
  cat >> "$kernel_dir/fs/Kconfig" <<'EOF'

# TEMPORARY compilation-test-only symbol. Do NOT ship in production.
config KSU_SUSFS
    bool "SUSFS build-probe only - KernelSU NOT integrated"
    default n
EOF
fi

# Try to compile fs/susfs.o with SUSFS enabled, preserving original A12s
# configuration. This may expose unresolved KernelSU dependencies or KABI.
export PATH="/usr/lib/llvm-14/bin:$PATH"
export ARCH=arm64 LLVM=1 CROSS_COMPILE=aarch64-linux-gnu- CROSS_COMPILE_COMPAT=arm-linux-gnueabi-
make -C "$kernel_dir" O="$GITHUB_WORKSPACE/out" exynos850-a12snsxx_defconfig \
  > "$report_dir/configure.log" 2>&1
"$kernel_dir/scripts/config" --file "$GITHUB_WORKSPACE/out/.config" -e KSU_SUSFS
make -C "$kernel_dir" O="$GITHUB_WORKSPACE/out" olddefconfig \
  >> "$report_dir/configure.log" 2>&1
cp "$GITHUB_WORKSPACE/out/.config" "$report_dir/effective.config"
if ! grep -q '^CONFIG_KSU_SUSFS=y$' "$report_dir/effective.config"; then
  echo 'BLOCKED: SUSFS config did not resolve in temporary checkout' > "$report_dir/result.txt"
  exit 1
fi

set +e
timeout 30m make -C "$kernel_dir" -j2 O="$GITHUB_WORKSPACE/out" fs/susfs.o \
  > "$report_dir/susfs-object-build.log" 2>&1
result=$?
set -e
echo "$result" > "$report_dir/susfs-object-exit-code.txt"
tail -n 100 "$report_dir/susfs-object-build.log" > "$report_dir/susfs-build-tail.txt"
if [ "$result" -eq 0 ]; then
  echo 'SUSFS OBJECT COMPILED IN TEMP CHECKOUT; KernelSU hooks/linking/device boot NOT verified' \
    > "$report_dir/result.txt"
else
  echo 'SUSFS OBJECT COMPILE FAILED: resolve vendor KernelSU / SUSFS API incompatibilities before integration' \
    > "$report_dir/result.txt"
fi
cat "$report_dir/result.txt"
exit "$result"
