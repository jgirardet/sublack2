from fixtures import sublack

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
        import time
        time.sleep(1)
        global test_port
        b = sublack.server.BlackdServer(port=test_port, timeout=0.001)
        self.assertTrue(b.is_running())
