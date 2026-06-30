import sys
import unittest

from bot import should_launch_gui


class StartupBehaviorTests(unittest.TestCase):
    def test_frozen_app_does_not_launch_gui_subprocess(self):
        original_frozen = getattr(sys, "frozen", False)
        sys.frozen = True
        try:
            self.assertFalse(should_launch_gui())
        finally:
            sys.frozen = original_frozen

    def test_source_run_can_launch_gui_subprocess(self):
        original_frozen = getattr(sys, "frozen", False)
        sys.frozen = False
        try:
            self.assertTrue(should_launch_gui())
        finally:
            sys.frozen = original_frozen


if __name__ == "__main__":
    unittest.main()
