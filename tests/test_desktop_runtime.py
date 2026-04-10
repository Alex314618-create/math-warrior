import os
import unittest
from pathlib import Path

import desktop_runtime


class DesktopRuntimeTest(unittest.TestCase):
    def test_macos_candidates_use_application_support(self):
        fake_home = Path("/Users/xiaohe")
        candidates = desktop_runtime.app_data_base_candidates("darwin", fake_home)
        self.assertEqual(candidates[0], fake_home / "Library" / "Application Support")
        self.assertEqual(candidates[1], fake_home)

    def test_windows_candidates_start_with_localappdata(self):
        fake_home = Path("C:/Users/Xiaohe")
        candidates = desktop_runtime.app_data_base_candidates("win32", fake_home)
        self.assertEqual(candidates[0], Path(os.getenv("LOCALAPPDATA") or ""))
        self.assertEqual(candidates[1], Path(os.getenv("APPDATA") or ""))
        self.assertEqual(candidates[2], fake_home)


if __name__ == "__main__":
    unittest.main()
