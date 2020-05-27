#!/usr/bin/env python3

from . import hookimpl

@hookimpl
def tiden_get_applications_path():
    return ["tiden.apps.", "apps."]


@hookimpl
def tiden_get_plugins_path():
    from os.path import dirname, abspath, join
    from os import getcwd

    return [join(dirname(abspath(__file__)), "plugins"), join(abspath(getcwd()), "plugins")]

