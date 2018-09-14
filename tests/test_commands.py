from unittest import TestCase, skip  # noqa
from unittest.mock import patch

import sublime
from fixtures import sublack, blacked, unblacked, diff
from sublack.utils import get_open_port
from sublack.server import BlackdServer
import time
import requests
from sublack.consts import (
    BLACKD_STARTED,
    STATUS_KEY,
    BLACKD_STOPPED,
    BLACKD_START_FAILED,
    BLACKD_STOP_FAILED,
)


# @skip("demonstrating skipping")
# @patch.object(sublack.commands, "is_python", return_value=True)
# class TestBlack(TestCase):
#     def setUp(self):
#         self.view = sublime.active_window().new_file()
#         # make sure we have a window to work with
#         s = sublime.load_settings("Preferences.sublime-settings")
#         s.set("close_windows_when_empty", False)
#         self.maxDiff = None

#     def tearDown(self):
#         if self.view:
#             self.view.set_scratch(True)
#             self.view.window().focus_view(self.view)
#             self.view.window().run_command("close_file")

#     def all(self):
#         all_file = sublime.Region(0, self.view.size())
#         return self.view.substr(all_file)

#     def setText(self, string):
#         self.view.run_command("append", {"characters": string})

#     def test_black_file(self, s):
#         self.setText(unblacked)
#         self.view.run_command("black_file")
#         self.assertEqual(blacked, self.all())

#     def test_black_file_nothing_todo(self, s):
#         self.setText(blacked)
#         self.view.run_command("black_file")
#         self.assertEqual(blacked, self.all())
#         self.assertEqual(
#             self.view.get_status(sublack.consts.STATUS_KEY),
#             sublack.consts.ALREADY_FORMATED_MESSAGE,
#         )

#     def test_black_file_dirty_stay_dirty(self, s):
#         self.setText(blacked)
#         self.assertTrue(self.view.is_dirty())
#         self.view.run_command("black_file")
#         self.assertTrue(self.view.is_dirty())
#         self.assertEqual(blacked, self.all())

#     def test_black_diff(self, s):
#         # setup in case of fail
#         # self.addCleanup(self.view.close)
#         # self.addCleanup(self.view.set_scratch, True)

#         self.setText(unblacked)
#         self.view.set_name("base")
#         backup = self.view
#         self.view.run_command("black_diff")

#         w = sublime.active_window()
#         v = w.active_view()
#         res = sublime.Region(0, v.size())
#         res = sublime.Region(v.lines(res)[2].begin(), v.size())
#         res = v.substr(res).strip()
#         self.assertEqual(res, diff)
#         self.assertEqual(
#             v.settings().get("syntax"), "Packages/Diff/Diff.sublime-syntax"
#         )
#         self.view = backup
#         v.set_scratch(True)
#         v.close()


# @patch.object(sublack.commands, "is_python", return_value=True)
# @patch.object(sublack.blacker, "get_settings", return_value=BLACKDSERVER_SETTINGS)
class TestBlackdServer(TestCase):
    def setUp(self):
        self.port = str(get_open_port())
        SETTINGS = {"sublack.black_blackd_port": self.port}

        self.view = sublime.active_window().new_file()
        self.settings = self.view.settings()
        # make sure we have a window to work with
        [self.settings.set(k, v) for k, v in SETTINGS.items()]
        self.settings.set("close_windows_when_empty", False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")
        sublime.run_command("blackd_stop")

    def test_startblackd(self):
        # First normal Run
        self.view.run_command("blackd_start")
        r = requests.post("http://localhost:" + self.port, data="a=1")
        self.assertEqual(r.content, b"a = 1\n", "should have been formatted")
        self.assertEqual(
            self.view.get_status(STATUS_KEY),
            BLACKD_STARTED.format(self.port),
            "sould tell it starts",
        )

        # already running aka port in use
        self.view.run_command("blackd_start")
        print(self.port, "popopopo")
        self.assertEqual(
            self.view.get_status(STATUS_KEY),
            BLACKD_START_FAILED.format(self.port),
            "sould tell it fails",
        )

    def test_stoplackd(self):
        # set up
        self.view.run_command("blackd_start")
        r = requests.post("http://localhost:" + self.port, data="a=1")
        self.assertEqual(r.content, b"a = 1\n", "should have been formatted")

        # already running, normal way
        sublime.run_command("blackd_stop")
        self.assertRaises(
            requests.ConnectionError,
            lambda: requests.post(
                "http://localhost:" + self.port, "server should be down"
            ),
        )
        self.assertEqual(
            self.view.get_status(STATUS_KEY), BLACKD_STOPPED, "should tell it stops"
        )

        # already stopped
        sublime.run_command("blackd_stop")
        self.assertEqual(
            self.view.get_status(STATUS_KEY),
            BLACKD_STOP_FAILED,
            "status tell stop failed",
        )
