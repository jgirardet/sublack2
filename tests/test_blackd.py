from unittest import TestCase
from unittest.mock import patch
import time
import os

import sublime
from fixtures import sublack, blacked, unblacked, diff

blackd_proc = sublack.utils.BlackdServer()


def setUpModule():
    global blackd_proc
    if not blackd_proc.run():
        raise IOError('blackd server not running')
    
    # ci = os.environ.get("CI", None)
    # if ci:
    #     print("waiting Blackserver Up")
    #     time.sleep(2)


def tearDownModule():
    global blackd_proc
    blackd_proc.stop()


BASE_SETTINGS = {
    "black_command": "black",
    "black_on_save": True,
    "black_line_length": None,
    "black_fast": False,
    "black_debug_on": True,
    "black_default_encoding": "utf-8",
    "black_skip_string_normalization": False,
    "black_include": None,
    "black_py36": None,
    "black_exclude": None,
    "black_use_blackd": True,
    "black_blackd_host": "localhost",
    # "black_blackd_port": blackd_proc.port,
    "black_blackd_port": "45484",
}


@patch.object(sublack.commands, "is_python", return_value=True)
@patch.object(sublack.blacker, "get_settings", return_value=BASE_SETTINGS)
class TestBlackdServer(TestCase):
    def setUp(self):
        self.view = sublime.active_window().new_file()
        # make sure we have a window to work with
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def all(self):
        all_file = sublime.Region(0, self.view.size())
        return self.view.substr(all_file)

    def setText(self, string):
        self.view.run_command("append", {"characters": string})

    # def test_fail(self, s):
    #     self.assertEqual(True, self.view.settings().get("black_use_blackd"))

    def test_blacked(self, s, c):
        self.setText(unblacked)
        self.view.run_command("black_file")
        self.assertEqual(blacked, self.all())

    # def test_syntax_error(self, s, c):
    #     self.setText("print(1")
    #     self.view.run_command("black_file")
    #     self.view.window().status_message()
    #     self.assertEqual(blacked, self.all())

    def test_nothing_todo(self, s, c):
        self.setText(blacked)
        self.view.run_command("black_file")
        self.assertEqual(blacked, self.all())
        self.assertEqual(
            self.view.get_status(sublack.consts.STATUS_KEY),
            sublack.consts.ALREADY_FORMATED_MESSAGE,
        )

    def test_do_diff(self, s, c):
        """"black should be called even blacked"""

        self.setText(unblacked)
        self.view.set_name("base")
        backup = self.view
        self.view.run_command("black_diff")
        w = sublime.active_window()
        v = w.active_view()
        res = sublime.Region(0, v.size())
        res = sublime.Region(v.lines(res)[2].begin(), v.size())
        res = v.substr(res).strip()
        self.assertEqual(res, diff)
        self.assertEqual(
            v.settings().get("syntax"), "Packages/Diff/Diff.sublime-syntax"
        )
        self.view = backup
        v.set_scratch(True)
        v.close()
