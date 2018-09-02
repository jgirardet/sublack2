import signal
import subprocess
import sublime
import socket
import requests
import time
import os
from pathlib import Path
import logging

LOG = logging.getLogger("sublack")

from .utils import cache_path


class BlackdServer:
    def __init__(self, host="localhost", port=None, deamon=False):
        if not port:
            self.port = str(self.get_open_port())
        else:
            self.port = port
        self.host = host
        self.proc = None
        self.platform = sublime.platform()
        self.deamon = deamon
        self.pid_path = cache_path() / "pid"

    def is_running(self):
        # check server running
        started = time.time()
        while time.time() - started < 5:  # timeout 5 s
            try:
                requests.post("http://" + self.host + ":" + self.port)
            except requests.ConnectionError:
                time.sleep(0.2)
            else:
                LOG.info(
                    "blackd running at {} on port {} with pid {}".format(
                        self.host, self.port, self.proc.pid
                    )
                )

                return True
        LOG.info(
            "failed to start blackd at {} on port {}}".format(self.host, self.port)
        )
        return False

    def write_cache(self, pid):
        LOG.debug("write cache  %s", pid)
        with self.pid_path.open("w") as f:
            f.write(str(pid))

    def get_cache(self):
        return int(self.pid_path.open().read())

    def run(self):

        cmd = ["blackd", "--bind-port", self.port]

        self.proc = subprocess.Popen(cmd)

        if self.deamon:
            watched = "plugin_host"
            cwd = os.path.dirname(os.path.abspath(__file__))
            LOG.debug(
                "Running checker watched = %s and proc = %s", watched, self.proc.pid
            )
            subprocess.Popen(
                ["python3", "checker.py", watched, str(self.proc.pid)], cwd=cwd
            )
            self.write_cache(self.proc.pid)

        return self.is_running()

    def stop(self):
        self.proc.terminate()
        LOG.info("blackd shutdown")

    def stop_from_cache(self):
        LOG.info("blackd halted from cache")
        try:
            os.kill(self.get_cache(), signal.SIGTERM)
        except ValueError:
            LOG.debug("No pid in cache")
        self.write_cache("")

    def get_open_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port
