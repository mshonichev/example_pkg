#!/usr/bin/env python3

import pluggy

hookspec = pluggy.HookspecMarker("tiden")


@hookspec
def tiden_get_applications_path():
    """
    Return list of applications packages search path (import prefixes).

    Default applications packages prefixes list is:
    ["tiden.apps.", "apps"]
    """


@hookspec
def tiden_get_plugins_path():
    """
    Return list of plugins search path (actual file system paths).

    Default list:
    [<tiden install path>/plugins, <current working directory>/plugins]
    """
