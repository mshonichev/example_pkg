#!/usr/bin/env python3
from pprint import PrettyPrinter

from tiden.tidenplugin import TidenPlugin
from tiden.dockermanager import DockerManager

TIDEN_PLUGIN_VERSION = '1.0.0'


class DockerCleaner(TidenPlugin):
    pp = PrettyPrinter()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def before_hosts_setup(self, *args, **kwargs):
        self.dockermanager = DockerManager(self.config, self.ssh)
        force_setup = self.config.get('force_setup', False) or self.options.get('force_setup', False)
        containers_count = self.dockermanager.print_and_terminate_containers(force_setup)
        if containers_count == 0:
            self.log_print('all containers removed successfully', color='green')
        elif containers_count > 0:
            if self.options.get('force_setup', False):
                exit('some containers don\'t deleted.  The runner will be stopped')
            else:
                exit('WARNING: Found docker containers and flag force_setup for DockerCleaner isn\'t set. '
                     'The runner will be stopped')
        else:
            self.log_print('No running docker containers found on hosts', color='green')