import re
import sublime
from .consts import (
    CONFIG_OPTIONS,
    ENCODING_PATTERN,
    KEY_ERROR_MARKER,
    PACKAGE_NAME,
    SETTINGS_FILE_NAME,
    SETTINGS_NS_PREFIX,
)

import logging
import pathlib
import subprocess

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


def cache_path():
    return pathlib.Path(sublime.cache_path(), PACKAGE_NAME)


def windows_popen_prepare():
    # win32: hide console window
    if sublime.platform() == "windows":
        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags = (
            # subprocess.CREATE_NEW_CONSOLE #| subprocess.STARTF_USESHOWWINDOW
            # subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            subprocess.CREATE_NEW_PROCESS_GROUP
        )
        startup_info.wShowWindow = subprocess.SW_HIDE
    else:
        startup_info = None
        return startup_info
