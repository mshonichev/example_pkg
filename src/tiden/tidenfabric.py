#!/usr/bin/env python3

import pluggy

from .singleton import singleton
from .tidenconfig import TidenConfig
from .sshpool import SshPool
from .nasmanager import NasManager
from .result import ResultLinesCollector
from . import hookspecs
from . import tidenhooks

@singleton
class TidenFabric:
    config = None
    ssh_pool = None
    nas_manager = None
    result_lines_collector = None
    hook_mgr = None

    def getSshPool(self):
        if self.ssh_pool is None:
            self.ssh_pool = SshPool(self.getConfigDict()['ssh'])
        return self.ssh_pool

    def getConfig(self, obj={}):
        if self.config is None:
            # assert obj is not None, "First call to getConfig() must have a dictionary parameter with actual config"
            self.config = TidenConfig(obj)
        return self.config

    def getConfigDict(self):
        return self.getConfig().obj

    def setConfig(self, obj):
        if self.config is None:
            self.config = TidenConfig(obj)
        else:
            self.config.update(obj)
        return self.config

    def setSshPool(self, ssh_pool):
        self.ssh_pool = ssh_pool

    def getNasManager(self):
        if self.nas_manager is None:
            self.nas_manager = NasManager(self.getConfig().obj)
        return self.nas_manager

    def reset(self):
        self.config = None
        self.ssh_pool = None
        return self

    def getResultLinesCollector(self):
        if self.result_lines_collector is None:
            self.result_lines_collector = ResultLinesCollector(self.getConfig().obj)
        return self.result_lines_collector

    def get_hook_mgr(self):
        if self.hook_mgr is None:
            self.hook_mgr = pluggy.PluginManager("tiden")
            self.hook_mgr.add_hookspecs(hookspecs)
            self.hook_mgr.load_setuptools_entrypoints("tiden")
            self.hook_mgr.register(tidenhooks)
        return self.hook_mgr

