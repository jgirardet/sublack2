from fixtures import sublack
import time

from unittest import TestCase
from unittest.mock import patch
import subprocess

from sublack.server import BlackdServer

test_proc = None
test_port = str(BlackdServer.get_open_port())


def setUpModule():
    global test_proc
    global test_port
    test_proc = subprocess.Popen(["blackd", "--bind-port", test_port])


def tearDownModule():
    global test_proc
    test_proc.terminate()
    test_proc.wait()


class TestBlackdServer(TestCase):
    def test_no_port_give_random_port(self):
        b = BlackdServer()
        c = BlackdServer()
        self.assertNotEqual(c.port, b.port)

    def test_is_running_blackd_not_running_return_False(self):
        with patch("sublack.server.time.sleep"):
            b = sublack.server.BlackdServer(timeout=0.001)
            self.assertFalse(b.is_running())

    def test_is_running_blackd_running_return_True(self):
        time.sleep(0.5)  # wait balckd on
        global test_port
        b = sublack.server.BlackdServer(port=test_port, timeout=0.001)
        self.assertTrue(b.is_running())

    def test_write_path_if_daemon(self):
        b = sublack.server.BlackdServer(
            timeout=0.001, deamon=True, checker_interval=0.001
        )
        b.run()

        self.assertEqual(
            b.proc.pid,
            b.get_cached_pid(),
            msg="cache should be written with the server pid",
        )

        self.assertTrue(b"checker.py plugin_host %s" % b.proc.pid)
        a in s.check_output('ps x'.split())                                                  
Out[21]: True 

        b.stop()
