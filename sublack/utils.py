import re
import subprocess
import sublime
import socket
import requests
import time
from .consts import (
    CONFIG_OPTIONS,
    ENCODING_PATTERN,
    KEY_ERROR_MARKER,
    PACKAGE_NAME,
    SETTINGS_FILE_NAME,
    SETTINGS_NS_PREFIX,
)

import logging

LOG = logging.getLogger("sublack")


def get_settings(view):
    flat_settings = view.settings()
    nested_settings = flat_settings.get(PACKAGE_NAME, {})
    global_settings = sublime.load_settings(SETTINGS_FILE_NAME)
    settings = {}

    for k in CONFIG_OPTIONS:
        # 1. check sublime "flat settings"
        value = flat_settings.get(SETTINGS_NS_PREFIX + k, KEY_ERROR_MARKER)
        if value != KEY_ERROR_MARKER:
            settings[k] = value
            continue

        # 2. check sublieme "nested settings" for compatibility reason
        value = nested_settings.get(k, KEY_ERROR_MARKER)
        if value != KEY_ERROR_MARKER:
            settings[k] = value
            continue

        # 3. check plugin/user settings
        settings[k] = global_settings.get(k)

    return settings


def get_encoding_from_region(region, view):
    """
    ENCODING_PATTERN is given by PEP 263
    """

    ligne = view.substr(region)
    encoding = re.findall(ENCODING_PATTERN, ligne)

    return encoding[0] if encoding else None


def get_encoding_from_file(view):
    """
    get from 2nd line only If failed from 1st line.
    """
    region = view.line(sublime.Region(0))
    encoding = get_encoding_from_region(region, view)
    if encoding:
        return encoding
    else:
        encoding = get_encoding_from_region(view.line(region.end() + 1), view)
        return encoding
    return None


class BlackdServer:
    def __init__(self, host="localhost", port=None):
        if not port:
            self.port = str(45484)
            # self.port = str(self.get_open_port())
            print(self.port)
        self.host = host
        self.proc = None
        self.platform = sublime.platform()

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

    def run(self):
        # use this complexity to properly terminate blackd

        cmd = ["blackd", "--bind-port", self.port]

        self.proc = subprocess.Popen(cmd)

        return self.is_running()

    def stop(self):
        self.proc.terminate()

    def get_open_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("après socket")
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port
