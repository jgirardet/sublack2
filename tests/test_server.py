from fixtures import sublack
import time

from unittest import TestCase
from unittest.mock import patch
import subprocess

from sublack.server import BlackdServer
from sublack.utils import kill_with_pid, popen


test_proc = None
test_port = str(BlackdServer.get_open_port())


def setUpModule():
    print("tup")
    global test_proc
    global test_port
    test_proc = subprocess.Popen(["blackd", "--bind-port", test_port])
    # test_proc = popen(["blackd", "--bind-port", test_port])
    print("tup fin", test_proc.poll())


def tearDownModule():
    print("td")
    global test_proc
    kill_with_pid(test_proc.pid)


class TestBlackdServer(TestCase):
    def setUp(self):
        print('test steup')
        if hasattr(self, "serv"):  # a blackdserver
            self.stop()

    def test_no_port_give_random_port(self):
        print("test1")
        b = BlackdServer()
        c = BlackdServer()
        self.assertNotEqual(c.port, b.port)

    def test_is_running_blackd_not_running_return_False(self):
        print("test2")
        with patch("sublack.server.time.sleep"):
            # b = sublack.server.BlackdServer(timeout=0)
            b = sublack.server.BlackdServer(timeout=0.001)
            self.assertFalse(b.is_running())

    # def test_is_running_blackd_running_return_True(self):
    #     time.sleep(0.5)  # wait balckd on
    #     global test_port
    #     b = sublack.server.BlackdServer(port=test_port, timeout=0.001)
    #     self.assertTrue(b.is_running())

    # def test_write_path_if_daemon(self):
    #     self.serv = sublack.server.BlackdServer(
    #         timeout=0.001, deamon=True, checker_interval=0
    #     )
    #     self.serv.run()

    #     self.assertEqual(
    #         self.serv.proc.pid,
    #         self.serv.get_cached_pid(),
    #         msg="cache should be written with the server pid",
    #     )


#         # checker_ps = ("checker.py plugin_host %s" % b.proc.pid).encode()

#         #         self.assertTrue(checker_ps in s.check_output('ps x'.split())
#         # Out[21]: True
