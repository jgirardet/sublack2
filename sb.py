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

    # check cache_path
    from sublack.consts import CACHE_PATH

    cache_path = pathlib.Path(CACHE_PATH)
    if not cache_path.exists():
        cache_path.mkdir()
