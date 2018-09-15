import time
import subprocess
import platform
import os
import signal
import re
import argparse

DEFAULT_INTERVAL = 5


class Checker:
    def __init__(self, watched: str, target: str, interval: int = DEFAULT_INTERVAL):

        self.watched = watched.encode()
        self.target = int(target)
        self.interval = interval

        self.is_running = self._set_platform()

    def is_running_windows(self):
        tasklist = subprocess.check_output(["tasklist", "/FO", "CSV"]).splitlines()

        r_watched = re.compile(rb'"%b\.exe"' % self.watched)
        r_target = re.compile(rb'".+","%b"' % str(self.target).encode())

        watched_found = False
        target_found = False

        for task in tasklist:

            if r_watched.match(task):
                watched_found = True

            if r_target.match(task):
                target_found = True

            if watched_found and target_found:
                return True
        return False

    def is_running_unix(self):

        tasklist = subprocess.check_output(["ps", "xo", "pid,stat,cmd"]).splitlines()

        watched_found = False
        target_found = False

        for task in tasklist:

            splitted = task.split(maxsplit=2)

            if (
                self.watched in splitted[2]
                and b"checker.py" not in splitted[2]
                and splitted[1] != b"Z"
            ):
                watched_found = True

            if str(self.target).encode() == splitted[0] and splitted[1] != b"Z":
                target_found = True

            if watched_found and target_found:
                return True
        return False

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
            time.sleep(self.interval)
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

    parser = argparse.ArgumentParser(description="checker")
    parser.add_argument("watched", type=str, help="Watched program's name")
    parser.add_argument("target", type=int, help="target's pid")
    parser.add_argument(
        "interval",
        nargs="?",
        type=int,
        default=DEFAULT_INTERVAL,
        help="interval between each check, default is 5",
    )

    args = parser.parse_args()

    print("running checker", vars(args))
    Checker(**vars(args)).run()
