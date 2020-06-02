#!/usr/bin/env python3
#
# Copyright 2017-2020 GridGain Systems.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .tidenexception import *
from apps.zookeeper import Zookeeper as ZookeeperApp


class ZooException(TidenException):
    pass


class Zookeeper(ZookeeperApp):

    def __init__(self, config, ssh, **kwargs):
        zookeeper_name = kwargs.get('name', 'zookeeper')
        super().__init__(zookeeper_name, config, ssh, **kwargs)

    # def __init__(self, config, ssh):
    #     self.config = config
    #     self.ssh = ssh
    #     self.zoo_nodes = {}
    #     self.zookeeper_home = None
    #     self.logger = get_logger('[tiden]')

    # def deploy_zookeeper(self):
    #     if self.config['artifacts'].get('zookeeper') is not None:
    #         prepare_zoo = {}
    #         self.zookeeper_home = '%s/zookeeper' % self.config['rt']['remote']['test_module_dir']
    #
    #         if self.config['artifacts']['zookeeper'].get('remote_home'):
    #             self.zookeeper_home = self.config['artifacts']['zookeeper']['remote_home']
    #
    #         if len(self.config['environment'].get('zookeeper_hosts', [])) == 0:
    #             hosts = self.config['environment'].get('client_hosts')
    #         else:
    #             hosts = self.config['environment'].get('zookeeper_hosts')
    #
    #         zk_count = self.config['environment'].get('zookeeper_per_host', 1)
    #
    #         for node_idx in range(1, zk_count + 1):
    #             host = hosts[node_idx % len(hosts)]
    #             self.zoo_nodes[node_idx] = {
    #                 'host': host,
    #                 'home': self.zookeeper_home,
    #                 'state': NodeStatus.NEW,
    #                 'client_port': '218%s' % node_idx
    #             }
    #
    #         log_print("*** Deploying Zookeeper on hosts %s, nodes count=%s, zoo home=%s"
    #                   % (hosts, zk_count, self.zookeeper_home), color='green')
    #
    #         for host in hosts:
    #             artifact_name = self.config['artifacts']['zookeeper']['path'].split('/')[-1]
    #             remote_artifact = '%s/%s' % (self.config['remote']['artifacts_dir'], artifact_name)
    #             prepare_zoo[host] = [
    #                 'mkdir -p %s' % self.zookeeper_home,
    #                 'tar -zxf %s -C %s --strip 1' % (remote_artifact, self.zookeeper_home),
    #                 'mkdir -p %s/logs' % self.zookeeper_home
    #             ]
    #             self.logger.debug(prepare_zoo)
    #             self.ssh.exec(prepare_zoo)
    #     else:
    #         raise ZooException('Zookeeper module could not be configured. '
    #                            'Zookeeper artifacts are not set in config file.')
    #
    # def start_zookeeper(self):
    #     """
    #     Start Zookeeper server nodes
    #     :return: none
    #     """
    #     self._prepare_zk_configs()
    #     self._update_grid_configs()
    #
    #     for node_idx in self.zoo_nodes.keys():
    #         self.start_zookeeper_node(node_idx)
    #
    #     log_print('*** Zookeeper started! ***', color='green')
    #     self.logger.debug(self.zoo_nodes)
    #
    # def start_zookeeper_node(self, node_id):
    #     started = False
    #
    #     if node_id not in self.zoo_nodes:
    #         log_print('Node id {} is not found in nodes\n{}'.format(node_id, self.zoo_nodes), color='red')
    #         return
    #
    #     if self.zoo_nodes[node_id].get('state') in [NodeStatus.STARTED]:
    #         log_print('Node id {} is already started:\n{}'.format(node_id, self.zoo_nodes[node_id]), color='red')
    #         return
    #
    #     start_cmd = "export ZOOCFGDIR={config_dir};cd {zk_home};bin/zkServer.sh start {config_dir}/zoo.cfg". \
    #         format(config_dir=self._get_cfg_path(node_id), zk_home=self.zoo_nodes[node_id]['home'])
    #
    #     run_zookeeper = {
    #         self.zoo_nodes[node_id]['host']: [start_cmd]
    #     }
    #     log_print('Starting Zookeeper on host {}'.format(self.zoo_nodes[node_id]['host']))
    #     result = self.ssh.exec(run_zookeeper)
    #     self.logger.debug(result)
    #     for line in result[self.zoo_nodes[node_id]['host']][0].split('\n'):
    #         if 'STARTED' in line:
    #             started = True
    #     if started:
    #         self.zoo_nodes[node_id]['PID'] = self.get_pid(node_id)
    #         self.zoo_nodes[node_id]['state'] = NodeStatus.STARTED
    #     else:
    #         log_print('Zookeeper node was not started on host %s' % self.zoo_nodes[node_id]['host'], color='red')
    #
    # def stop_zookeeper(self):
    #     """
    #     Stop Zookeeper server nodes
    #     :return: none
    #     """
    #
    #     for node in self.zoo_nodes.keys():
    #         stop_cmd = "cd %s; bin/zkServer.sh stop %s/zoo.cfg" % \
    #                    (self.zoo_nodes[node]['home'], self._get_cfg_path(node))
    #         stop_zookeeper = {
    #             self.zoo_nodes[node]['host']: [stop_cmd]
    #         }
    #         log_print('*** Stopping Zookeeper on host %s ***' % self.zoo_nodes[node]['host'], color='green')
    #         out = self.ssh.exec(stop_zookeeper)
    #         self.logger.debug(out)
    #         self.zoo_nodes[node]['state'] = NodeStatus.KILLED
    #
    # def kill_zk_node(self, node_id):
    #     log_print('Kill zookeeper node %s' % node_id)
    #     kill_command = {
    #         self.zoo_nodes[node_id]['host']: ['nohup kill -9 %s > /dev/null 2>&1' % self.zoo_nodes[node_id]['PID']]
    #     }
    #     self.ssh.exec(kill_command)
    #     self.zoo_nodes[node_id]['state'] = NodeStatus.KILLED
    #
    # def _get_servers_cfg(self):
    #     tmp_server_hosts_cfg = []
    #     for node_idx in self.zoo_nodes.keys():
    #         tmp_server_hosts_cfg.append('server.%s=%s:288%s:388%s'
    #                                     % (node_idx, self.zoo_nodes[node_idx]['host'], node_idx, node_idx))
    #     return '\n'.join(tmp_server_hosts_cfg)
    #
    # def _get_cfg_path(self, node_id):
    #     return '%s/conf_%s' % (self.zoo_nodes[node_id]['home'], node_id)
    #
    # def _get_zkConnectionString(self):
    #     tmp_host_port = []
    #     for node_idx in self.zoo_nodes.keys():
    #         tmp_host_port.append('%s:%s' % (self.zoo_nodes[node_idx]['host'], self.zoo_nodes[node_idx]['client_port']))
    #     return ','.join(tmp_host_port)
    #
    # def set_grid_configs(self, grid_configs):
    #     self.grid_configs = grid_configs
    #
    # def _update_grid_configs(self, grid_configs=None):
    #     commands = {}
    #     config_files = self.grid_configs
    #     if grid_configs:
    #         config_files = grid_configs
    #     for host in self.config['environment'].get('server_hosts'):
    #         commands[host] = []
    #         for file_name in config_files:
    #             file_path = '%s/%s' % (self.config['rt']['remote']['test_module_dir'], file_name)
    #             commands[host].append(
    #                 'sed -i \'s#__ZK_CONNECTION__#%s#g\' %s' % (self._get_zkConnectionString(), file_path)
    #             )
    #     self.logger.debug(commands)
    #     self.ssh.exec(commands)
    #
    # def _prepare_zk_configs(self):
    #     commands = {}
    #     for node in self.zoo_nodes.keys():
    #
    #         host = self.zoo_nodes[node]['host']
    #         conf_path = self._get_cfg_path(node)
    #
    #         if commands.get(host) is None:
    #             commands[host] = []
    #
    #         # create folders data, logs in zookeeper home
    #         commands[host].append('mkdir -p {}'.format(conf_path))
    #         commands[host].append('mkdir -p {}/logs_{}'.format(self.zoo_nodes[node]['home'], node))
    #         commands[host].append('cp {}/log4j.properties -p {}/'.format(conf_path[:-2], conf_path))
    #
    #         # create zookeeper configs
    #         zoo_cfg = '%s/zoo.cfg' % conf_path
    #         env_cfg = '%s/java.env' % conf_path
    #
    #         commands[host] += [
    #             'echo -e "dataDir=%s\ninitLimit=5\nsyncLimit=2\nclientPort=%s\n%s\n" > %s'
    #             % (conf_path, self.zoo_nodes[node]['client_port'], self._get_servers_cfg(), zoo_cfg),
    #             'echo "ZOO_LOG_DIR=\"%s/logs_%s\"" > %s' % (self.zoo_nodes[node]['home'], node, env_cfg),
    #             'echo "ZOO_LOG4J_PROP=\"DEBUG,CONSOLE,ROLLINGFILE\"" >> %s' % env_cfg,
    #             'echo -e "%s" > %s/myid' % (node, conf_path)
    #         ]
    #
    #     self.logger.debug(commands)
    #     self.ssh.exec(commands)
    #
    # def get_pid(self, node_id):
    #     pid = None
    #     start_cmd = "cat %s/zookeeper_server.pid" % self._get_cfg_path(node_id)
    #     command = {
    #         self.zoo_nodes[node_id]['host']: [start_cmd]
    #     }
    #     result = self.ssh.exec(command)
    #     for line in result[self.zoo_nodes[node_id]['host']][0].split('\n'):
    #         m = search('(\d+)', line)
    #         if m:
    #             pid = m.group(1)
    #     return pid

