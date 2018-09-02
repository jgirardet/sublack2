import sys

import logging
import sublime
import pathlib

from .sublack import *  # noqa

LOG = logging.getLogger("sublack")
handler = logging.StreamHandler()
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)


from . import sublack

sys.modules["sublack"] = sublack


def plugin_loaded():

    # set logLevel
    current_view = sublime.active_window().active_view()
    config = sublack.utils.get_settings(current_view)
    if config["black_debug_on"]:
        LOG.setLevel(logging.DEBUG)

    # # check cache_path
    from sublack.utils import cache_path

    cp = cache_path()
    if not cp.exists():
        cp.mkdir()

    # check blackd autostart
    if config["black_blackd_autostart"]:
        current_view.run_command("blackd_start")
