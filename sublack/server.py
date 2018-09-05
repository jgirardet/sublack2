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

LOG = logging.getLogger("sublack")

from .utils import cache_path, windows_popen_prepare


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
        with self.pid_path.open("w") as f:
            f.write(str(pid))
        LOG.debug('write cache  "%s"', pid)

    def get_cached_pid(self):
        return int(self.pid_path.open().read())

    def _run_blackd(self, cmd):
        try:
            if self.platform == "windows":
                st = subprocess.STARTUPINFO()
                st.dwFlags = (
                    subprocess.STARTF_USESHOWWINDOW
                    | subprocess.CREATE_NEW_PROCESS_GROUP
                )
                st.wShowWindow = subprocess.SW_HIDE

            else:
                st = None
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=st,
                # creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
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
            watched = "plugin_host"
            cwd = os.path.dirname(os.path.abspath(__file__))
            LOG.debug(
                "Running checker watched = %s and proc = %s", watched, self.proc.pid
            )
            subprocess.Popen(
                [sys.executable, "checker.py", watched, str(self.proc.pid)], cwd=cwd
            )
            self.write_cache(self.proc.pid)

        return self.is_running()

    def stop(self, pid):
        if self.platform == "windows":
            # need to properly kill precess traa
            subprocess.call(["taskkill", "/F", "/T", "/PID", str(pid)])
        else:
            if self.proc:
                self.proc.terminate()
            else:
                os.kill(pid, signal.SIGTERM)
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

    def get_open_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port
