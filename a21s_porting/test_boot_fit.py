#!/usr/bin/env python3
"""SM-A217F boot packing arithmetic regression tests; no flashing or binaries."""
from __future__ import annotations
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name("boot_fit.py")
spec = importlib.util.spec_from_file_location("a21s_boot_fit", MODULE)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class BootFitTests(unittest.TestCase):
    def test_stock_reproduces_original_image(self):
        self.assertEqual(mod.pack_size(mod.STOCK_KERNEL_BYTES), 35_678_224)

    def test_previous_boe_overflows(self):
        self.assertEqual(mod.pack_size(36_870_656), 38_479_888)
        self.assertEqual(mod.pack_size(36_870_656) - mod.PARTITION_BYTES, 731_152)

    def test_compact_boe_fits_size_only(self):
        self.assertEqual(mod.pack_size(34_714_112), 36_323_344)
        self.assertEqual(mod.PARTITION_BYTES - mod.pack_size(34_714_112), 1_425_392)

    def test_require_fit_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            p = subprocess.run([sys.executable, str(MODULE), "--image-size", "36870656",
                                "--require-fit", "--out-dir", directory],
                               capture_output=True, text=True, check=False)
            self.assertEqual(p.returncode, 2)
            self.assertTrue((Path(directory) / "A21S_BOOT_FIT.json").is_file())

    def test_require_fit_does_not_claim_hardware_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            p = subprocess.run([sys.executable, str(MODULE), "--image-size", "34714112",
                                "--require-fit", "--out-dir", directory],
                               capture_output=True, text=True, check=False)
            self.assertEqual(p.returncode, 0)
            self.assertIn("NOT FLASHABLE", p.stdout)
            self.assertIn("FITS_SIZE_ONLY_NOT_BOOT_VALIDATED", p.stdout)


if __name__ == "__main__":
    unittest.main()
