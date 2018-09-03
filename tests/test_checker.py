from fixtures import sublack

from unittest.mock import patch, MagicMock
from unittest import TestCase, skipIf

from sublack.checker import Checker
import subprocess as s
import os
import platform
import pathlib

root_dir = pathlib.Path(__file__).parents[1]
sublack_dir = root_dir / "sublack"


class TestSetPlatform(TestCase):
    @patch("sublack.checker.platform.system", return_value="Linux")
    def test_setplatform_linux(self, plat):
        a = Checker("bla", 13246789)
        self.assertEqual(a.is_running_unix, a.is_running)

    @patch("sublack.checker.platform.system", return_value="Darwin")
    def test_setplatform_osx(self, plat):
        a = Checker("bla", 13246789)
        self.assertEqual(a.is_running_unix, a.is_running)

    @patch("sublack.checker.platform.system", return_value="Windows")
    def test_setplatform_windows(self, plat):
        a = Checker("bla", 13246789)
        self.assertEqual(a.is_running_windows, a.is_running)


@skipIf(platform.system() == "Windows", "unix tests")
class TestIsRunningUnix(TestCase):
    def test_target_alredy_terminated(self):
        p = s.Popen(["ls"])
        p.wait()
        c = Checker("a", p.pid)
        self.assertFalse(c.is_running())

    def test_watched_still_running(self):
        p = s.Popen(["head"])
        c = Checker("head", os.getpid())
        self.assertTrue(c.is_running())
        p.wait()

    def test_watched_not_running(self):
        p = s.Popen(["head"])
        c = Checker("head", os.getpid())
        p.terminate()
        p.wait()
        self.assertFalse(c.is_running())

    def test_do_not_take_checker_args_in_account(self):
        p = s.Popen(["python3", "checker.py", "head", "987654"], cwd=str(sublack_dir))
        c = Checker("head", os.getpid())
        self.assertFalse
        (c.is_running())
        p.wait()


@skipIf(platform.system() == "Windows", "unix tests")
class TestRunUnix(TestCase):
    def setUp(self):
        self.w = s.Popen(["head"])
        self.t = s.Popen(["tail"])
        self.p = s.Popen(
            ["python3", "checker.py", "head", str(self.t.pid)], cwd=str(sublack_dir)
        )

    def tearDown(self):
        try:
            self.w.terminate()
            self.t.terminate()
            self.p.terminate()
        except ProcessLookupError:
            pass

    @patch("sublack.checker.time")
    def test_good_run(self, sleep):

        self.assertIsNone(self.w.poll())  # is_running
