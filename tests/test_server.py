from fixtures import sublack
import time

from unittest import TestCase
from unittest.mock import patch
import subprocess

from sublack.server import BlackdServer
from sublack.utils import popen, kill_with_pid, get_open_port


test_proc = None
test_port = str(get_open_port())


def setUpModule():
    print("tup")
    global test_proc
    global test_port
    # test_proc = subprocess.Popen(["blackd", "--bind-port", test_port])
    test_proc = popen(["blackd", "--bind-port", test_port])
    print("tup fin", test_proc.poll())


def tearDownModule():
    print("td")
    global test_proc
    kill_with_pid(test_proc.pid)


class TestBlackdServer(TestCase):
    """
    Use self.serv as temp server in tests. automtically closed
    at tearDown
    """

    def tearDown(self):
        # if hasattr(self, "serv"):  # a blackdserver
        try:
            self.serv.stop()
        except AttributeError:
            pass
        except ProcessLookupError:
            pass

    def test_no_port_give_random_port(self):
        b = BlackdServer()
        c = BlackdServer()
        self.assertNotEqual(c.port, b.port)

    def test_is_running_blackd_not_running_return_False(self):
        with patch("sublack.server.time.sleep"):
            # b = sublack.server.BlackdServer(timeout=0)
            b = sublack.server.BlackdServer(timeout=0.001)
            self.assertFalse(b.is_running())

    def test_is_running_blackd_running_return_True(self):
        time.sleep(0.5)  # wait balckd on
        global test_port
        b = sublack.server.BlackdServer(port=test_port, timeout=0.001)
        self.assertTrue(b.is_running())

    def test_stop(self):
        self.serv = sublack.server.BlackdServer(timeout=0.001, checker_interval=0)
        self.serv.run()
        self.assertTrue(self.serv.is_running())
        self.serv.stop()
        self.assertEqual(self.serv.proc.wait(timeout=2), 0)

    def test_daemon(self):
        self.serv = sublack.server.BlackdServer(
            timeout=0.001, checker_interval=0, deamon=True
        )
        self.serv.run()
        self.assertTrue(self.serv.is_running(), msg="should wait blackd is running")
        self.assertEqual(
            self.serv.get_cached_pid(),
            self.serv.proc.pid,
            "cache should be written with pid",
        )

        BlackdServer().stop_deamon()
        self.assertEqual(
            self.serv.proc.wait(timeout=2),
            0,
            "blackd should be stopped with return code 0",
        )
        self.assertFalse(
            BlackdServer().get_cached_pid(), "should get a blank cached pid"
        )


#         # checker_ps = ("checker.py plugin_host %s" % b.proc.pid).encode()

#         #         self.assertTrue(checker_ps in s.check_output('ps x'.split())
#         # Out[21]: True
