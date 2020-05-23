#!/usr/bin/env python3

from .singleton import singleton
from .tidenconfig import TidenConfig
from .sshpool import SshPool
from .nasmanager import NasManager
from .result import ResultLinesCollector

@singleton
class TidenFabric:
    config = None
    ssh_pool = None
    nas_manager = None
    result_lines_collector = None

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
