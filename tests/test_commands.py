from unittest import TestCase, skip  # noqa
from unittest.mock import patch

import sublime
from fixtures import sublack, blacked, unblacked, diff
import requests
from pathlib import Path


TEST_BLACK_SETTINGS = {
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
    "black_use_blackd": False,
    "black_blackd_host": "localhost",
    "black_blackd_port": "",
}


# @patch.object(sublack.commands, "is_python", return_value=True)
# @patch.object(sublack.blacker, "get_settings", return_value=TEST_BLACK_SETTINGS)
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

#     def test_black_file(self, s, c):
#         self.setText(unblacked)
#         self.view.run_command("black_file")
#         self.assertEqual(blacked, self.all())

#     def test_black_file_nothing_todo(self, s, c):
#         self.setText(blacked)
#         self.view.run_command("black_file")
#         self.assertEqual(blacked, self.all())
#         self.assertEqual(
#             self.view.get_status(sublack.consts.STATUS_KEY),
#             sublack.consts.ALREADY_FORMATTED_MESSAGE,
#         )

#     def test_black_file_dirty_stay_dirty(self, s, c):
#         self.setText(blacked)
#         self.assertTrue(self.view.is_dirty())
#         self.view.run_command("black_file")
#         self.assertTrue(self.view.is_dirty())
#         self.assertEqual(blacked, self.all())

#     def test_black_diff(self, s, c):
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


# class TestBlackdServer(TestCase):
#     def setUp(self):
#         self.port = str(sublack.get_open_port())
#         SETTINGS = {"sublack.black_blackd_port": self.port}

#         self.view = sublime.active_window().new_file()
#         self.settings = self.view.settings()
#         # make sure we have a window to work with
#         [self.settings.set(k, v) for k, v in SETTINGS.items()]
#         self.settings.set("close_windows_when_empty", False)

#     def tearDown(self):
#         if self.view:
#             self.view.set_scratch(True)
#             self.view.window().focus_view(self.view)
#             self.view.window().run_command("close_file")
#         sublime.run_command("blackd_stop")

#     def test_startblackd(self):
#         # First normal Run
#         self.view.run_command("blackd_start")
#         self.assertTrue(
#             sublack.check_blackd_on_http(self.port), "should have been formatted"
#         )
#         self.assertEqual(
#             self.view.get_status(sublack.STATUS_KEY),
#             sublack.BLACKD_STARTED.format(self.port),
#             "sould tell it starts",
#         )

#         # already running aka port in use
#         with patch("sublime.message_dialog"):
#             self.view.run_command("blackd_start")
#         self.assertEqual(
#             self.view.get_status(sublack.STATUS_KEY),
#             sublack.BLACKD_ALREADY_RUNNING.format(self.port),
#             "sould tell it fails",
#         )

#     def test_stoplackd(self):
#         # set up
#         self.view.run_command("blackd_start")
#         self.assertTrue(
#             sublack.check_blackd_on_http(self.port),
#             "ensure blackd is running for the test",
#         )

#         # already running, normal way
#         sublime.run_command("blackd_stop")
#         self.assertRaises(
#             requests.ConnectionError,
#             lambda: requests.post(
#                 "http://localhost:" + self.port, "server should be down"
#             ),
#         )
#         self.assertEqual(
#             self.view.get_status(sublack.STATUS_KEY),
#             sublack.BLACKD_STOPPED,
#             "should tell it stops",
#         )

#         # already stopped
#         sublime.run_command("blackd_stop")
#         self.assertEqual(
#             self.view.get_status(sublack.STATUS_KEY),
#             sublack.BLACKD_STOP_FAILED,
#             "status tell stop failed",
#         )


class TestFormatAll(TestCase):
    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.view.set_scratch(True)
        self.window.focus_view(self.view)

    def tearDown(self):
        if hasattr(self, "wrong"):
            self.wrong.unlink()
        self.window.focus_view(self.view)
        self.window.run_command("close_file")

    # def test_black_all_success(self):

    #     # make sure we have a window to work with
    #     # s = sublime.load_settings("Preferences.sublime-settings")
    #     # s.set("close_windows_when_empty", False)
    #     # self.maxDiff = None

    #     self.window.run_command("black_format_all")
    #     self.assertEqual(
    #         self.window.active_view().get_status(sublack.STATUS_KEY),
    #         sublack.REFORMATTED_MESSAGE,
    #         "reformat should be ok",
    #     )

    def test_black_all_fail(self):

        folder = Path(__file__).parent
        self.wrong = folder / "wrong.py"
        with open(str(self.wrong), "w") as ww:
            ww.write("ab ac = 2")

        self.view.run_command("black_format_all")
        self.assertEqual(
            self.window.active_view().get_status(sublack.STATUS_KEY),
            sublack.REFORMAT_ERRORS,
            "reformat should be error",
        )
