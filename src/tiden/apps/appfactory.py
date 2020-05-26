#!/usr/bin/env python3

from ..singleton import singleton
from ..tidenexception import TidenException
from ..tidenfabric import TidenFabric
from itertools import chain


@singleton
class ApplicationFactory:
    def __init__(self):
        hook_mgr = TidenFabric().get_hook_mgr()
        # [ "tiden.apps.", "tiden_gridgain.apps.", "" ]
        self.applications_paths = list(chain(*hook_mgr.hook.tiden_get_applications_path()))

    def get_app_package(self, app_class_package_name, app_class_name, app_name):
        for applications_path in self.applications_paths:
            try:
                application_package_path = applications_path + app_class_package_name
                app_pkg = __import__(application_package_path, globals(), locals(), [app_class_name], 0)
                return app_pkg
            except ImportError as e:
                pass
        raise TidenException(
            f"Can't import application class '{app_class_name}' for application '{app_name.title()}' "
            f"from package '{app_class_package_name}': package was not found in paths ({self.applications_paths})"
        )

