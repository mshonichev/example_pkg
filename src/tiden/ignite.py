#!/usr/bin/env python3

from time import sleep, time

from .apps import NodeStatus
from .util import log_put, log_print, deprecated

from .apps.ignite.ignite import Ignite as BaseIgnite


class Ignite(BaseIgnite):
    ignite_home = 'build'

    def __init__(self, config, ssh, **kwargs):
        ignite_name = kwargs.get('name', 'ignite')
        super().__init__(ignite_name, config, ssh, **kwargs)

    @deprecated
    def set_ignite_home(self, home):
        self.logger.log("Set ignite home to %s" % home, 2)
        self.ignite_home = home

    # def set_addresses(self):
    #     """
    #     Add used addresses to TcpDiscoveryVmIpFinder for all XML files
    #     :return:
    #     """
    #     for file in glob("%s/*.xml" % self.config['rt']['test_resource_dir']):
    #         self.add_addresses_to_config(file)
    #
    # @staticmethod
    # def add_addresses_to_config(config, config_path):
    #     """
    #     Add to 'addresses' property of org.apache.ignite.spi.discovery.tcp.ipfinder.vm.TcpDiscoveryVmIpFinder class
    #      the list of available IP addresses from environment configuration
    #     :param config_path: path to Ignite Spring configuration file
    #     :return: none
    #     """
    #     output_lines = []
    #     bean_found = 0
    #     sp4 = '    '
    #     with open(config_path) as f:
    #         for line in f:
    #             line = line.rstrip()
    #             match_bean = search('^(.+)<bean.+class='
    #                                 '"org\.apache\.ignite\.spi\.discovery\.tcp\.ipfinder\.vm\.TcpDiscoveryVmIpFinder" *>',
    #                                 line)
    #             if match_bean and bean_found == 0:
    #                 tab = match_bean.group(1)
    #                 output_lines.append(line)
    #                 ptab = tab + sp4
    #                 output_lines.append("%s<property name=\"addresses\">" % ptab)
    #                 ptab = tab + sp4 + sp4
    #                 output_lines.append("%s<list>" % ptab)
    #                 for host in config['environment']['server_hosts']:
    #                     ptab = tab + sp4 + sp4 + sp4
    #                     output_lines.append("%s<value>%s:47500..47510</value>" % (ptab, host))
    #                 if config['environment'].get('client_hosts') is not None:
    #                     for host in config['environment']['client_hosts']:
    #                         if not host in config['environment']['server_hosts']:
    #                             ptab = tab + sp4 + sp4 + sp4
    #                             output_lines.append("%s<value>%s:47500..47510</value>" % (ptab, host))
    #                 ptab = tab + sp4 + sp4
    #                 output_lines.append("%s</list>" % ptab)
    #                 ptab = tab + sp4
    #                 output_lines.append("%s</property>" % ptab)
    #                 bean_found = 2
    #             if bean_found == 2:
    #                 if '</bean>' in line:
    #                     bean_found = 0
    #             if bean_found == 0:
    #                 output_lines.append(line)
    #     with open(config_path, 'w') as f:
    #         f.write('\n'.join(output_lines))

    # @deprecated
    # def bind_to_host(self, config_path):
    #     output_lines = []
    #     sp4 = '    '
    #     with open(config_path) as f:
    #         for line in f:
    #             line = line.rstrip()
    #             match_bean = search('^(.+)<bean.+class='
    #                                 '"org\.apache\.ignite\.configuration\.IgniteConfiguration".*>',
    #                                 line)
    #             if match_bean:
    #                 tab = match_bean.group(1)
    #                 output_lines.append(line)
    #                 ptab = tab + sp4
    #                 output_lines.append('%s<property name="localHost" value="${NODE_IP}"/>' % ptab)
    #             else:
    #                 match_local_host = search('^.*<property name="localHost" value=".+".*/>', line)
    #                 if not match_local_host:
    #                     output_lines.append(line)
    #     with open(config_path, 'w') as f:
    #         f.write('\n'.join(output_lines))
    #
    # @deprecated
    # def set_communication_port(self, config_path):
    #     output_lines = []
    #     sp4 = '    '
    #     in_comm_bean = False
    #     with open(config_path) as f:
    #         for line in f:
    #             line = line.rstrip()
    #             match_bean = search('^(.+)<bean.+class='
    #                                 '"org\.apache\.ignite\.spi\.communication\.tcp\.TcpCommunicationSpi".*>',
    #                                 line)
    #
    #             if not in_comm_bean:
    #                 if match_bean:
    #                     in_comm_bean = True
    #                     tab = match_bean.group(1)
    #                     output_lines.append(line)
    #                     ptab = tab + sp4
    #                     output_lines.append(
    #                        '%s<property name="localPort" value="${NODE_COMMUNICATION_PORT}"/>' % ptab)
    #                 else:
    #                     output_lines.append(line)
    #             else:
    #                 match_port = search('^.*<property name="localPort" value=".+".*/>', line)
    #                 if not match_port:
    #                     output_lines.append(line)
    #                 if '</bean>' in line:
    #                     in_comm_bean = False
    #
    #     with open(config_path, 'w') as f:
    #         f.write('\n'.join(output_lines))

    @deprecated
    def wait_for_finished_rebalance(self, node_idx, cache, timeout):
        """
        Wait for finished rebalancing message in the node log
        :param node_idx:        node index
        :param cache: cache name
        :param timeout:     timeout
        :return:            None if timeout reached or number of rebalanced caches
        """
        timeout_counter = 0
        rebalancing = False
        started = int(time())
        while timeout_counter < timeout and not rebalancing:
            host = self.nodes[node_idx]['host']
            log_put(
                "Waiting for final rebalancing on %s, timeout %s/%s sec" % (
                    host,
                    timeout_counter,
                    timeout
                )
            )
            commands = {host: []}
            # commands[host].append(
            #     'cat %s | grep -E "Completed rebalancing" | tail -1' % self.nodes[node]['log']
            # )
            commands[host].append(
                'cat %s | grep -E "Completed \(final\) rebalancing.+ cacheOrGroup=%s," | tail -1' % (
                    self.nodes[node_idx]['log'], cache
                )
            )
            res = self.ssh.exec(commands)
            lines = str(res[host][0]).split('\n')
            # print(lines[0])
            if 'Completed (final) rebalancing' in lines[0] and (" cacheOrGroup=%s," % cache) in lines[0]:
                log_print()
                rebalancing = True
                break
            log_put(
                "Waiting for final rebalancing on %s, timeout %s/%s sec" % (
                    host,
                    timeout_counter,
                    timeout
                )
            )
            sleep(5)
            timeout_counter = int(time()) - started
        return rebalancing

    @deprecated
    def start_simple_client(self, options, msg, **kwargs):
        # DEPRECATED: See pt/piclient/piclient.py
        # Get next client host
        host = self.get_and_inc_client_host()
        opt_line = ' '.join(options)
        node_index = self.CLIENT_NODE_START_ID + 1
        bg = True
        jvm_options_str = ''
        class_paths = []

        if kwargs.get('foreground'):
            bg = False

        if kwargs.get('jvm_options'):
            jvm_options_str = ' '.join(kwargs.get('jvm_options'))

        # Find client node index
        while self.nodes.get(node_index) is not None and \
                node_index < self.CLIENT_NODE_START_ID + self.MAX_NODE_START_ID:
            node_index += 1

        # Construct class path
        for lib_dir in self.get_libs():
            class_paths.append("%s/%s/*" % (self.client_ignite_home, lib_dir))
        class_paths.append(self.config['artifacts']['test_tools']['remote_path'])

        log_file = '%s/grid.%s.node.%s.0.log' % (self.config['rt']['remote']['test_dir'], self.grid_name, node_index)
        self.nodes[node_index] = {
            'host': host,
            'log': log_file
        }

        # Client command line
        cmd = "cd %s; " \
              "  nohup " \
              "    $JAVA_HOME/bin/java " \
              "      -cp %s %s " \
              "      -DCONSISTENT_ID=%s " \
              "      -DIGNITE_QUIET=false " \
              "      -DNODE_IP=%s " \
              "      -DNODE_COMMUNICATION_PORT=%d " \
              "    org.apache.ignite.testtools.SimpleIgniteTestClient %s" \
              " > %s 2>&1 %s" \
              % (
                  self.client_ignite_home,
                  ':'.join(class_paths),
                  jvm_options_str,
                  self.get_node_consistent_id(node_index),
                  host,
                  self.get_node_communication_port(node_index),
                  opt_line,
                  log_file,
                  ('&' if bg else '')
              )

        clients = {host: [cmd]}
        self.ssh.exec(clients)
        if bg:
            self.wait_for_topology_snapshot(
                None,
                self.get_nodes_num('client') + 1,
                '',
                **kwargs,
            )
            log_print("Simple client %s started on %s: %s" % (str(node_index), host, msg))

    @deprecated
    def update(self):
        commands = {}
        for host_group in ['server_hosts', 'client_hosts']:
            for host in self.config['environment'][host_group]:
                commands[host] = []
                for node_index in self.nodes.keys():
                    if host == self.nodes[node_index]['host']:
                        commands[host].append({
                            'command': "ps -p %s" % str(self.nodes[node_index]['PID']),
                            'id': node_index
                        })
        results = self.ssh.exec(commands)
        for result in results:
            print(str(result))

    @deprecated
    def get_rest_port(self, host_group):
        return self.get_data_from_log(
            host_group,
            'Command protocol successfully started \[.*REST.*, port=[0-9]\+]',
            'Command protocol successfully started \[.*REST.*, port=(\d+)\]',
            'rest_port',
            force_type='int'
        )

    @deprecated
    def get_node_ids(self, host_group):
        return self.get_data_from_log(
            host_group,
            ' locNodeId=[0-9a-f\-]{36}\]\n',
            'locNodeId=([0-9a-f\-]{36})\]\n',
            'node_id'
        )

    # def get_node_ids2(self, host_group):
    #     return self.get_data_from_log(
    #         host_group,
    #         'Local node [ID=',
    #         'Local node \[ID=([A-F0-9a-f\-]{36}), order=',
    #         'node_id'
    #     )

    @deprecated
    def get_node_binary_rest_ports(self, host_group):
        return self.get_data_from_log(
            host_group,
            '\[GridTcpRestProtocol\] Command protocol successfully started', 'port=([0-9]+)\]\n',
            'binary_rest_port',
            force_type='int'
        )
