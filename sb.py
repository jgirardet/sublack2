import sys
# import logging
# import sublime

# from .sublack.commands import *  # noqa
# from .sublack.utils import get_settings
# from .sublack import rien
# from .sublack import blacker
# LOG = logging.getLogger("sublack")
# handler = logging.StreamHandler()
# LOG.addHandler(handler)
# LOG.setLevel(logging.INFO)


from . import sublack
sys.modules['sublack'] = sublack

print("dans sb", dir(sublack))

# def plugin_loaded():

#     # set logLevel
#     current_view = sublime.active_window().active_view()
#     config = get_settings(current_view)
#     if config["black_debug_on"]:
#         LOG.setLevel(logging.DEBUG)
