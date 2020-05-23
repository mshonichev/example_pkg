#!/usr/bin/env python3

from jinja2 import FileSystemLoader, Environment
from re import search

from .nodestatus import NodeStatus
from ..tidenexception import TidenException
from ..util import log_print


class AppException(TidenException):
    pass


class MissedRequirementException(AppException):
    pass


class App:
    config_builder = None
    nodes = {}
    config = None
    ssh = None
    name = ''
    app_type = ''
    artifact_name = ''

    def __init__(self, *args, **kwargs):
        # print('App.__init__')
        if len(args) == 1 and isinstance(args[0], self.__class__):
            self.__dict__ = args[0].__dict__
        else:
            name, config, ssh = args[0], args[1], args[2]
            self.config = config
            self.ssh = ssh
            self.nodes = {}
            self.app_type = None
            self.name = name
            if 'name' in kwargs and kwargs['name']:
                self.name = kwargs['name']
            self.artifact_name = self.name
            if 'artifact_name' in kwargs and kwargs['artifact_name']:
                self.artifact_name = kwargs['artifact_name']

    @classmethod
    def create_config_builder(cls, ssh, config):
        cls.config_builder = AppConfigBuilder(ssh, config, cls)

    @classmethod
    def get_config_types(cls):
        """
        Override in children App to declare which template config files your application provides.
        :return: dictionary: {
            <config_type>: <config template file name>
        }
        """
        return dict()

    def check_requirements(self):
        """
        Override in children App to perform check of environment/artifact requirements before running app.
        :return: None, raise MissedRequirementException when requirements are not fulfilled.
        """
        pass

    def setup(self):
        pass

    def teardown(self):
        pass

    def require_artifact(self, artifact_type):
        artf_found = False
        for artf_name in self.config['artifacts'].keys():
            if self.config['artifacts'][artf_name].get('type') == artifact_type \
                    and self.config['artifacts'][artf_name].get('path'):
                artf_found = True
                break
        if not artf_found:
            raise MissedRequirementException(
                "No suitable artifact '%s' found for application '%s' " % (artifact_type, self.__class__.__name__))

    def require_environment(self, name):
        if self.config['environment'].get('apps_use_global_hosts', False):
            if name not in self.config['environment']:
                self.config['environment'][name] = {}
            for key in ['server_hosts', 'client_hosts']:
                self.config['environment'][name][key] = self.config['environment'].get(key, [])
            for key in ['clients_per_host', 'servers_per_host']:
                self.config['environment'][name][key] = self.config['environment'].get(key, 1)
        else:
            if not self.config['environment'].get(name):
                raise MissedRequirementException("No environment section found for '%s' application" % name)
            app_env = False
            if self.config['environment'][name].get('server_hosts') or \
                    self.config['environment'][name].get('client_hosts'):
                app_env = True
            if not app_env:
                raise MissedRequirementException('No environment section found for %s application' % name)

    def _mark_scripts_executable(self, artifact_type, glob_mask='bin/*.sh'):
        for artf in self.config['artifacts'].keys():
            if self.config['artifacts'][artf].get('type') and self.config['artifacts'][artf]['type'] == artifact_type:
                self.ssh.exec(
                    ["chmod -v 0755 %s/%s" % (self.config['artifacts'][artf]['remote_path'], glob_mask)]
                )

    def grep_log(self, *args, **kwargs):
        """
        Find node attributes in log files in two phase:
          1 phase: cat/grep log files on remote hosts and collect lines matched <remote_regex>
          2 phase: apply <local_regex> to found lines to extract the value of attribute
        It is possible to use one <regex> instead of local and remote regex
        :param args:    the list of node ids
        :param kwargs:  the dictionary of looking attributes in format
                        <attr_name>={regex: <regex>, remote_regex: <regex>, local_regex: <regex>, type: '<data type name>'}}
        :return:
        """
        # Check passed arguments
        if len(args) == 0:
            raise AppException("At least one node id must pass to method")
        if len(kwargs) == 0:
            raise AppException("At least one attribute must pass to method")
        ids = []
        if isinstance(args[0], int):
            ids = args
        else:
            raise AppException("Wrong arguments type: the list of integers is expected")
        for attr_name in kwargs.keys():
            if kwargs[attr_name].get('regex') is not None:
                kwargs[attr_name]['local_regex'] = kwargs[attr_name].get('regex')
                kwargs[attr_name]['remote_regex'] = kwargs[attr_name].get('regex')
            for attr_param in ['local_regex', 'remote_regex']:
                if kwargs[attr_name].get(attr_param) is None:
                    raise AppException("Missed %s for attribute %s " % (attr_param, attr_name))
        cmd = {}
        seek_attrs = sorted(kwargs.keys())
        # Construct the dictionary with remote commands
        attrs = {}
        for id in ids:
            attrs[id] = {}
            host = self.nodes[id]['host']
            for attr_name in seek_attrs:
                cat_tmpl = "echo {}; echo {}; cat {}".format(id, attr_name, self.nodes[id]['log'])
                if cmd.get(host) is None:
                    cmd[host] = []

                cmd[host].append("{cat} | grep {options} '{condition}'".format(
                    cat=cat_tmpl,
                    options=kwargs[attr_name].get('remote_grep_options', ''),
                    condition=kwargs[attr_name]['remote_regex'])
                )
        result = self.ssh.exec(cmd)
        # Process the results
        for host in result.keys():
            cmd_outputs = list(result[host])
            for cmd_output_idx in range(0, len(cmd_outputs)):
                # Split command output to lines
                lines = cmd_outputs[cmd_output_idx].split('\n')
                # First line is node id
                id = int(str(lines[0]).rstrip())
                # Second line is attribute name
                attr_name = str(lines[1]).rstrip()
                # Set None for attribute
                attrs[id][attr_name] = None
                starting_point = len("{}\n{}".format(id, attr_name))
                if kwargs[attr_name].get('ignore_multiline', False):
                    sarched_str = cmd_outputs[cmd_output_idx][starting_point:].replace('\n', '')
                else:
                    sarched_str = cmd_outputs[cmd_output_idx][starting_point:]
                m = search(
                    kwargs[attr_name]['local_regex'],
                    sarched_str
                )
                if m:
                    if kwargs[attr_name].get('get_all_found', False):
                        val = m.groups()
                    else:
                        val = m.group(1)
                    attr_type = kwargs[attr_name].get('force_type', kwargs[attr_name].get('type'))
                    # Set type
                    if attr_type == 'int':
                        val = int(val)
                    attrs[id][attr_name] = val
        return attrs

    def kill_nodes(self, *args):
        """
        Kill nodes by pid
        :param args:    the list of nodes ids
        :return:        None
        """
        ids = []
        if len(args) == 0:
            ids = list(self.nodes.keys())
        else:
            ids = args
        cmd = {}
        for id in ids:
            if self.nodes.get(id):
                host = self.nodes[id]['host']
                if self.nodes[id].get('PID'):
                    self.nodes[id]['status'] = NodeStatus.KILLING
                    log_print(f'Kill node {id} at host {host}')
                    if not cmd.get(host):
                        cmd[host] = []
                    cmd[host].append('nohup kill -9 %s > /dev/null 2>&1' % self.nodes[id]['PID'])
                else:
                    log_print(f'There is no PID for node {id}: already killed')
            else:
                log_print(f'No node {id} in the grid to kill')
        return self.ssh.exec(cmd)

    def set_node_option(self, node_filter, opt_name, opt_value):
        """
        Set option for node or node group
        :param node_filter: node index(es) or '*' for all nodes
        :param opt_name:    option name
        :param opt_value:   option value
        :return:
        """
        for node_idx in sorted(self.nodes.keys()):
            if node_filter == '*' or node_idx in node_filter:
                self.nodes[node_idx].update({opt_name: opt_value})


class AppConfigBuilder:
    """
    Holds a dictionary of configuration sets for given application.
    Each configuration set holds a set of config files of different type (e.g. server config, client config).
    """
    current_config_set = None

    def __init__(self, tiden_ssh, tiden_config, app):
        self.tiden_ssh = tiden_ssh
        self.tiden_config = tiden_config

        self.app = app

        self.config_sets = {}

    def register_config_set(self, config_set_name):
        """
        Register new config set

        Context name:
        * common variables - variables for all configs in this context
        * exclusive variables - variables for particular node
        * common configs - result of config + common variables
        * exclusive configs - result of exclusive config + (common + exclusive variables)

        :param config_set_name: configuration set name
        :return:
        """
        if config_set_name in self.config_sets:
            log_print("Config set with name '%s' is already registered. Creating new config set." % config_set_name,
                      color='yellow')

        self.config_sets[config_set_name] = {}

        if self.current_config_set is None:
            self.current_config_set = config_set_name

        self.config_sets[config_set_name]['common_variables'] = {}
        self.config_sets[config_set_name]['exclusive_variables'] = {}
        self.config_sets[config_set_name]['common_configs'] = {}
        self.config_sets[config_set_name]['exclusive_configs'] = {}
        self.config_sets[config_set_name]['additional_config_types'] = {}
        return self.config_sets[config_set_name]

    def cleanup_exclusive_configs(self):
        for config in self.config_sets.keys():
            self.config_sets[config]['exclusive_variables'] = {}
            self.config_sets[config]['exclusive_configs'] = {}

    def unregister_config_set(self, config_set_name):
        if config_set_name not in self.config_sets:
            log_print("Unknown config set '%s' to remove" % config_set_name)
            return

        del self.config_sets[config_set_name]

    def add_template_variables(self, config_set_name=None, node_id=None, **values):
        if config_set_name is None:
            insert_config_list = [self.current_config_set]
        else:
            if config_set_name not in ['*', 'all']:
                if config_set_name not in self.config_sets:
                    raise TidenException('Unknown config set name! Currently created configs: %s' %
                                         str(self.config_sets.keys()))

                insert_config_list = [config_set_name]
            else:
                insert_config_list = self.config_sets.keys()

        for cfg_set_name in insert_config_list:
            if node_id:
                # insert exclusive config variables
                if node_id not in self.config_sets[cfg_set_name]['exclusive_variables']:
                    self.config_sets[cfg_set_name]['exclusive_variables'][node_id] = values
                else:
                    self.config_sets[cfg_set_name]['exclusive_variables'][node_id] = \
                        {**self.config_sets[cfg_set_name]['exclusive_variables'][node_id], **values}
            else:
                # insert common variables
                self.config_sets[cfg_set_name]['common_variables'] = {**self.config_sets[config_set_name]['common_variables'], **values}

    def get_template_variables(self, node_id=None, config_set_name=None):
        cfg_set_name = self.__get_config_set_name(config_set_name)

        if node_id:
            # get exclusive config
            # there is no such node - return common variables
            if node_id not in self.config_sets[cfg_set_name]['exclusive_variables']:
                return self.config_sets[cfg_set_name]['common_variables']
            else:
                # otherwise get merged common and exclusive variables
                return {**self.config_sets[cfg_set_name]['exclusive_variables'][node_id],
                        **self.config_sets[cfg_set_name]['common_variables']}
        else:
            # get common config
            return self.config_sets[cfg_set_name]['common_variables']

    def __get_config_set_name(self, config_set_name):
        cfg_set_name = config_set_name if config_set_name else self.current_config_set
        if cfg_set_name is None or cfg_set_name not in self.config_sets:
            raise TidenException(f'Unknown configuration set name: {cfg_set_name}! '
                                 f'Currently created config sets: {self.config_sets.keys()}')
        return cfg_set_name

    def get_config(self, config_type, config_set_name=None, node_id=None):
        """
        Get actual config file name for given config type
        :param config_type:
        :param config_set_name:
        :param node_id:
        :return:
        """
        cfg_set_name = self.__get_config_set_name(config_set_name)

        if node_id:
            # get exclusive config
            if node_id not in self.config_sets[cfg_set_name]['exclusive_configs']:
                raise TidenException("Unknown node_id '%s' in exclusive config set '%s'" % (node_id, config_set_name))

            if config_type not in self.config_sets[cfg_set_name]['exclusive_configs'][node_id]:
                raise TidenException("Unknown config_type '%s' in exclusive config set '%s' for node %s" %
                                     (config_type, cfg_set_name, node_id))

            return self.config_sets[cfg_set_name]['exclusive_configs'][node_id][config_type]
        else:
            # get common config
            if config_type not in self.config_sets[cfg_set_name]['common_configs']:
                raise TidenException("Unknown config type '%s', maybe per_node_config used." % config_type)

            return self.config_sets[cfg_set_name]['common_configs'][config_type]

    def add_config_type(self, config_type, config_name, config_set_name=None):
        # for all registered configs generate files
        for cfg_set_name, cfg_set in self.config_sets.items():
            # skip generating configs not in filter
            if config_set_name and cfg_set_name != config_set_name:
                continue

            cfg_set['additional_config_types'][config_type] = config_name

    def build_config(self, config_type=None, config_set_name=None, node_id=None):
        """
        Build config files, either for all configuration sets or specific one.
        :param config_type: (optional) build specific configuration file instead of all set
        :param config_set_name: (optional) configuration set to build config files
        :param node_id: (optional) build configuration files exclusive for that node id
        :return:
        """
        # for all registered configs generate files
        for cfg_set_name, cfg_set in self.config_sets.items():
            # skip generating configs not in filter
            if config_set_name and cfg_set_name != config_set_name:
                continue

            dict_configs = {}
            config_types = {}
            config_types.update(self.app.get_config_types())
            config_types.update(cfg_set['additional_config_types'])

            # for each item in app.get_config() define generated config name (client, server in Ignite e.g.)
            for cfg_type, original_config in config_types.items():
                # skip generating configs not in filter
                if config_type and cfg_type != config_type:
                    continue

                if not node_id:
                    # generate common config
                    generated_config_name = original_config.replace('.tmpl', '_%s' % cfg_set_name)

                    # generate mapping {template: result} file name for XMLConfigBuilder
                    dict_configs[original_config] = generated_config_name

                    # remember result file name
                    cfg_set['common_configs'][cfg_type] = generated_config_name
                else:
                    # generate exclusive config
                    generated_config_name = original_config.replace('.tmpl', '_%s_%s' % (cfg_set_name, node_id))

                    # generate mapping {template: result} file name for XMLConfigBuilder
                    dict_configs[original_config] = generated_config_name

                    # remember result file name
                    if node_id not in cfg_set['exclusive_configs']:
                        cfg_set['exclusive_configs'][node_id] = {}

                    cfg_set['exclusive_configs'][node_id][cfg_type] = generated_config_name

            # define variables for configs
            if node_id and node_id in cfg_set['exclusive_variables']:
                variables = {**cfg_set['common_variables'],
                             **cfg_set['exclusive_variables'][node_id]}
            else:
                variables = cfg_set['common_variables']

            # render template
            for template, config in dict_configs.items():
                rendered_string = Environment(loader=FileSystemLoader(self.tiden_config['rt']['test_resource_dir']),
                                              trim_blocks=True) \
                    .get_template(template) \
                    .render({**variables, **self.tiden_config})

                with open("%s/%s" % (self.tiden_config['rt']['test_resource_dir'], config), "w+") as config_file:
                    config_file.write(rendered_string)

    def build_config_and_deploy(self, config_type=None, config_set_name=None, node_id=None):
        from glob import glob
        from os import path
        from tiden.util import unix_path

        if isinstance(config_type, (list, tuple)):
            for type in config_type:
                self.build_config(type, config_set_name, node_id)
        else:
            self.build_config(config_type, config_set_name, node_id)
        files = []
        test_resource_dir = self.tiden_config['rt']['test_resource_dir']
        for file in glob(f"{test_resource_dir}/*"):
            if path.isfile(file):
                files.append(unix_path(file))
        self.tiden_ssh.upload(files, self.tiden_config['rt']['remote']['test_module_dir'])

    def __str__(self):
        res = ['\nApplication config for app %s:\n' % str(self.app.__name__),
               '\n  Current config set: %s\n' % self.current_config_set,
               '\n  Original configs: %s\n' % self.app.get_config_types()]

        for config_set_name in self.config_sets:
            res.append('\n  Config set: %s\n' % config_set_name)
            res.append('    Common template variables: %s\n' % self.config_sets[config_set_name]['common_variables'])
            res.append('    Exclusive template variables: %s\n' % self.config_sets[config_set_name]['exclusive_variables'])
            res.append('    Common generated configs: %s\n' % self.config_sets[config_set_name]['common_configs'])
            res.append('    Exclusive generated configs: %s\n' % self.config_sets[config_set_name]['exclusive_configs'])

        return ''.join(res)
