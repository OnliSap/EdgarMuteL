import os
import sys
import tempfile
import unittest
from unittest.mock import patch

import bot
from bot import should_launch_gui
from ini_parser import get_bot_config, get_config


class StartupBehaviorTests(unittest.TestCase):
    def test_frozen_app_can_launch_gui_window(self):
        original_frozen = getattr(sys, "frozen", False)
        original_executable = getattr(sys, "executable", "")
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, ".edgarmute_gui.lock")
            try:
                sys.frozen = True
                sys.executable = os.path.join(tmpdir, "EdgarMute.exe")

                dummy_app = object()
                with patch("bot.QtWidgets.QApplication.instance", return_value=None), patch("bot.QtWidgets.QApplication", return_value=dummy_app) as app_cls, patch("bot.MainWindow", side_effect=lambda: type("DummyWindow", (), {"show": lambda self: None})()):
                    result = bot.launch_gui_subprocess(lock_path)
                    self.assertIs(result, dummy_app)
                    self.assertEqual(app_cls.call_count, 1)
            finally:
                sys.frozen = original_frozen
                sys.executable = original_executable

    def test_source_run_can_launch_gui_window(self):
        original_frozen = getattr(sys, "frozen", False)
        sys.frozen = False
        try:
            self.assertTrue(should_launch_gui())
        finally:
            sys.frozen = original_frozen

    def test_frozen_app_does_not_launch_gui_subprocess_when_lockfile_points_to_running_pid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, ".edgarmute_gui.lock")
            with open(lock_path, "w", encoding="utf-8") as handle:
                handle.write(str(os.getpid()))

            original_frozen = getattr(sys, "frozen", False)
            original_executable = getattr(sys, "executable", "")
            try:
                sys.frozen = True
                sys.executable = os.path.join(tmpdir, "EdgarMute.exe")

                with patch("bot.QtWidgets.QApplication.instance", return_value=None), patch("bot.QtWidgets.QApplication", return_value=object()), patch("bot.MainWindow", side_effect=lambda: type("DummyWindow", (), {"show": lambda self: None})()):
                    bot.launch_gui_subprocess(lock_path)
            finally:
                sys.frozen = original_frozen
                sys.executable = original_executable

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
