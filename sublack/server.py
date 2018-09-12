import signal
import subprocess
import sublime
import socket
import requests
import time
import os
import sys
from pathlib import Path
import logging
from .utils import cache_path, startup_info, kill_with_pid, popen

LOG = logging.getLogger("sublack")


class BlackdServer:
    def __init__(
        self,
        host="localhost",
        port=None,
        deamon=False,
        timeout=5,
        watched="plugin_host",
        checker_interval=None,
    ):
        if not port:
            self.port = str(self.get_open_port())
        else:
            self.port = port
        self.host = host
        self.proc = None
        self.platform = sublime.platform()
        self.deamon = deamon
        self.pid_path = cache_path() / "pid"
        self.timeout = timeout
        self.watched = watched
        self.checker_interval = checker_interval

    def is_running(self):
        # check server running
        started = time.time()
        print(started, self.timeout)
        while time.time() - started < self.timeout:  # timeout 5 s
            print(time.time(), "debut boucle")

            try:
                requests.post("http://" + self.host + ":" + self.port)
                print(time.time(), "fin try")
            except requests.ConnectionError:
                print(time.time(), "debut sleep")
                time.sleep(0.2)
                print(time.time(), "fin sleep")
            else:
                LOG.info(
                    "blackd running at {} on port {} with pid {}".format(
                        self.host, self.port, getattr(self.proc, "pid", None)
                    )
                )

                return True
        print(time.time())
        LOG.info("failed to start blackd at {} on port {}".format(self.host, self.port))
        return False

    def write_cache(self, pid):
        with self.pid_path.open("w") as f:
            f.write(str(pid))
        LOG.debug('write cache  "%s"', pid)

    def get_cached_pid(self):
        return int(self.pid_path.open().read())

    def _run_blackd(self, cmd):
        try:
            proc = popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            out, err = proc.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            LOG.info("BlackdServer démarré sur le port {}".format(cmd[2]))
            out, err = True, None
        else:
            LOG.info("Erreur du démmmarrage {}".format(err.decode()))  # show stderr

        return proc, out, err

    def run(self):

        cmd = ["blackd", "--bind-port", self.port]

        self.proc, out, err = self._run_blackd(cmd)

        if err:
            return False

        if self.deamon:
            cwd = os.path.dirname(os.path.abspath(__file__))
            checker_cmd = [
                sys.executable,
                "checker.py",
                self.watched,
                str(self.proc.pid),
            ]
            print("checker cmd", checker_cmd)
            checker_cmd = (
                checker_cmd
                if not self.checker_interval
                else checker_cmd + [str(self.checker_interval)]
            )
            print("checker cmd", checker_cmd)
            LOG.debug("Running checker {}".format(checker_cmd))
            self.checker = popen(checker_cmd, cwd=cwd)
            LOG.debug("checker running with pid %s", self.checker.pid)

            self.write_cache(self.proc.pid)

        return self.is_running()

    def stop(self, pid = None):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=10)
        else:
            kill_with_pid(pid)

        LOG.info("blackd shutdown")

    def stop_from_cache(self):
        try:
            pid = self.get_cached_pid()
        except ValueError:
            LOG.debug("No pid in cache")
        except FileNotFoundError:
            LOG.debug("Cache file not found")
        else:
            self.stop(pid)
            LOG.info("blackd halted from cache")
        self.write_cache("")

    @staticmethod
    def get_open_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port
