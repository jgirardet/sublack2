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

        try:
            os.getpgid(self.target)
        except ProcessLookupError:
            return False

        is_running = [
            line
            for line in subprocess.check_output(["ps", "x"]).split(b"\n")
            if self.watched in line
            and b"checker.py" not in line  # not look at checker args
        ]
        return bool(is_running)

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
        try:
            os.kill(self.target, signal.SIGTERM)
        except ProcessLookupError:
            print("Process {} already terminated".format(self.target))

    def run(self):
        self.watch()
        self.terminate_target()


if __name__ == "__main__":

    watched = sys.argv[1]
    proc = sys.argv[2]
    print("running checker", watched, proc)
    Checker(watched, int(proc)).run()
