import os
import sys
import tempfile
import unittest

from bot import should_launch_gui
from ini_parser import get_bot_config, get_config


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

    def test_config_files_are_created_next_to_executable_when_frozen(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = os.path.join(tmpdir, "app")
            work_dir = os.path.join(tmpdir, "work")
            os.makedirs(app_dir)
            os.makedirs(work_dir)
            executable_path = os.path.join(app_dir, "EdgarMute.exe")
            with open(executable_path, "w", encoding="utf-8") as handle:
                handle.write("stub")

            original_cwd = os.getcwd()
            original_frozen = getattr(sys, "frozen", False)
            original_argv0 = sys.argv[0]
            original_executable = getattr(sys, "executable", "")
            try:
                os.chdir(work_dir)
                sys.frozen = True
                sys.argv[0] = executable_path
                sys.executable = executable_path

                get_config()
                get_bot_config()
            finally:
                os.chdir(original_cwd)
                sys.frozen = original_frozen
                sys.argv[0] = original_argv0
                sys.executable = original_executable

            self.assertTrue(os.path.exists(os.path.join(app_dir, "settings.ini")))
            self.assertTrue(os.path.exists(os.path.join(app_dir, "bot_settings.ini")))


if __name__ == "__main__":
    unittest.main()
