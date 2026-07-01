import builtins
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

import bot
from bot import should_launch_gui


class GuiStartupTests(unittest.TestCase):
    def test_frozen_app_can_launch_gui_window(self):
        original_frozen = getattr(sys, "frozen", False)
        original_executable = getattr(sys, "executable", "")
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, ".edgarmute_gui.lock")
            try:
                sys.frozen = True
                sys.executable = os.path.join(tmpdir, "EdgarMute.exe")

                dummy_app = object()

                class DummyQApplication:
                    @staticmethod
                    def instance():
                        return None

                    def __new__(cls, *args, **kwargs):
                        return dummy_app

                with patch("bot.QtWidgets.QApplication", DummyQApplication), patch("bot.MainWindow", side_effect=lambda: type("DummyWindow", (), {"show": lambda self: None})()):
                    result = bot.launch_gui_subprocess(lock_path)
                    self.assertIs(result, dummy_app)
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

                class DummyQApplication:
                    @staticmethod
                    def instance():
                        return None

                    def __new__(cls, *args, **kwargs):
                        return object()

                with patch("builtins.print"), patch("bot.QtWidgets.QApplication", DummyQApplication), patch("bot.MainWindow", side_effect=lambda: type("DummyWindow", (), {"show": lambda self: None})()):
                    result = bot.launch_gui_subprocess(lock_path)
                    self.assertFalse(result)
            finally:
                sys.frozen = original_frozen
                sys.executable = original_executable


if __name__ == "__main__":
    unittest.main()
