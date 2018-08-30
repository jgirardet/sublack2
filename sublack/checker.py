import time
import subprocess
import platform
import sys
import os
import signal


class Checker:
    def __init__(self, watched: str, target: int):

        self.watched = watched.encode()
        self.target = target

        self.is_running = self._set_platform()

    def is_running_windows(self):
        if self.watched + b".exe" in subprocess.check_output(["tasklist"]):
            return True

    def is_running_unix(self):
        if self.watched in subprocess.check_output(["ps", "x"]):
            return True

    def _set_platform(self):
        plat = platform.system()

        if plat in ["Linux", "Darwin"]:
            return self.is_running_unix

        elif plat in ["Windows"]:
            return self.is_running_windows
        else:
            raise EnvironmentError("environnement {} is not supported", plat)

    def watch(self):

        while True:
            time.sleep(5)
            if not self.is_running():
                return

    def terminate_target(self):
        os.kill(self.target, signal.SIGTERM)

    def run(self):
        self.watch()
        self.terminate_target()


if __name__ == "__main__":

    watched = sys.argv[1]
    proc = sys.argv[2]
    Checker(watched, int(proc)).run()
