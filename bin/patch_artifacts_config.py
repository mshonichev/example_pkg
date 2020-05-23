#!/usr/bin/env python3

from optparse import OptionParser
from yaml import load, dump, YAMLError, FullLoader
from re import compile
import os
from copy import deepcopy

re_var = compile('\${?([A-Z\-_a-z0-9]+)}?')
ignite_list_var_name = 'PREV_IGNITE_VERSION'

def patch_string(input_string, env):
    output_string = input_string
    while '$' in output_string:
        var = re_var.search(output_string)
        if var is None:
            break
        var = var.group(1)
        val = env.get(var, '')
        if val == '':
            print('WARNING: environment variable %s referenced in config is empty' % var)
        output_string = re_var.sub(val, output_string)

    return output_string

def patch_section(input_data, env):
    if type(input_data) == type({}):
        output = {}
        for k, v in input_data.items():
            new_k = patch_string(k, env)
            output[new_k] = patch_section(v, env)
        return output

    if type(input_data) != type(''):
        return input_data

    return patch_string(input_data, env)

def patch_config(input_config):
    """
    Replace shell variables in the input config dictionary.

    If 2nd-level config section has $PREV_IGNITE_VERSION, generate multiple sections for each of the previous versions.

    :param input_config:
    :return: patched config
    """
    output_config = {}

    env = deepcopy(os.environ)

    list_var = env.get(ignite_list_var_name, '')
    list_var_values = list_var.split(',')
    if len(list_var_values) == 0:
        list_var_values = ['']

    for list_var_value in list_var_values:
        env[ignite_list_var_name] = list_var_value
        if 'IGNITE' in ignite_list_var_name:
            if list_var_value != '':
                ign_version = list_var_value.split('.')
                shift = 6 if int(ign_version[0]) < 8 else 0
                gg_version = '.'.join([str(int(ign_version[0]) + shift)] + ign_version[1:])
                env[ignite_list_var_name.replace('IGNITE', 'GRIDGAIN')] = gg_version
        for section_name, section_data in input_config.items():
            if type(section_data) != type({}):
                output_config[section_name] = patch_section(input_config[section_name], env)
                continue
            output_section = {}
            for section_name2, section_data2 in section_data.items():
                section_name2 = patch_string(section_name2, env)
                output_section[section_name2] = patch_section(section_data2, env)
            output_config[section_name] = deepcopy(output_section)

    return output_config


if __name__ == "__main__":
    # Parse command-line arguments
    parser = OptionParser()
    parser.add_option("--config", action='append', default=[])
    parser.add_option("--output-dir", action='store', default='')
    options, args = parser.parse_args()

    for config_file in options.config:
        output_path = options.output_dir
        if not output_path:
            output_path = os.path.dirname(os.path.abspath(config_file))

        output_config = None
        try:
            with open(config_file, 'r') as file:
                input_config = load(file, Loader=FullLoader)
                output_config = patch_config(input_config)
        except FileNotFoundError as e:
            print(str(e))
            print("Error: File '%s' not found" % config_file)
            exit(1)
        except YAMLError as e:
            print(str(e))
            print("Error: Can't read '%s' as YAML file" % config_file)
            exit(1)

        if output_config:
            os.makedirs(output_path, exist_ok=True)
            with open(os.path.join(output_path, os.path.basename(config_file)), 'w') as file:
                dump(output_config, file, line_break=True, default_flow_style=False)



