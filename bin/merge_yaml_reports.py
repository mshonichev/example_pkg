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

from yaml import load, dump, FullLoader
import sys
from re import search


def load_yaml(yaml_path):
    data = {}
    with open(yaml_path, 'r') as f:
        data = load(f, Loader=FullLoader)
    return data


def save_yaml(yaml_path, data):
    with open(yaml_path, 'w') as w:
        dump(data, stream=w, line_break=True, default_flow_style=False)


def get_similarity_hash(run):
    configuration = ''
    options = run.get('test_configuration_options', [])
    if options:
        configuration = '(' + ', '.join([option + '=' + str(run.get(option, '')) for option in options]) + ')'
    return run.get('module', '') + '.' + run.get('function', '') + configuration


def build_similarity_hash(report):
    report_hash = {}
    for run_id, run in report.items():
        run_hash = get_similarity_hash(run)
        if run_hash in report_hash:
            print("ERROR: report has two runs with similar tests: '{}' and '{}', can't decide what to pick".format(
                run_id,
                report_hash[run_hash]
            ))
            sys.exit(4)

        report_hash[run_hash] = run_id
    return report_hash


def find_similar_run(report_hash, run):
    run_hash = get_similarity_hash(run)
    if run_hash in report_hash:
        return report_hash[run_hash]
    return None


def get_run_timestamp(run_id):
    m = search(r'\-([0-9]+\.[0-9]+)', run_id)
    if m:
        return float(m.group(1))


def add_to_result(result, run_id, run, ignites):
    if 'ignite_properties' in run:
        found = False
        for ignite in ignites:
            if run['ignite_properties'] == ignite:
                run['ignite_properties'] = ignite
                found = True
                break
        if not found:
            ignites.append(run['ignite_properties'].copy())
            run['ignite_properties'] = ignites[-1]
    result[run_id] = run


def main():
    previous_report = sys.argv[1]
    current_report = sys.argv[2]
    current = {}
    previous = {}
    try:
        previous = load_yaml(previous_report)
        current = load_yaml(current_report)
        assert type({}) == type(current)
        assert type({}) == type(previous)
    except Exception as e:
        print("ERROR: Can't load reports: %s" % str(e))
        sys.exit(1)

    result = {}
    ignites = []

    previous_index = build_similarity_hash(previous)

    for run_id, run in current.items():
        if type({}) != type(run):
            print("ERROR: key '{}' in current report '{}' must refer to dictionary".format(run_id, current_report))
            sys.exit(2)
        if 'last_status' in run:
            if run['last_status'] == 'not started':
                print("INFO: skipping run {} from current report due to test was not started".format(run_id))
                continue
            else:
                previous_run_id = find_similar_run(previous_index, run)
                if previous_run_id:
                    current_run_time = get_run_timestamp(run_id)
                    previous_run_time = get_run_timestamp(previous_run_id)
                    if current_run_time > previous_run_time or \
                            'not started' == previous[previous_run_id].get('last_status', ''):
                        print("INFO: excluding run {} from previous report, status: '{}', test: {}".format(
                            previous_run_id,
                            previous[previous_run_id].get('last_status'),
                            previous[previous_run_id].get('function'),
                        ))
                        del previous[previous_run_id]

                        print("INFO: copying run {} from current report to result, new status: '{}'".format(
                            run_id,
                            run['last_status']
                        ))
                        add_to_result(result, run_id, run, ignites)
                    else:
                        print("INFO: excluding run {} from current report".format(run_id))
                else:
                    print("INFO: copying run {} from current report to result".format(run_id))
                    add_to_result(result, run_id, run, ignites)

        else:
            print("ERROR: There is no 'last_status' in run '{}' in current report '{}'".format(run_id, current_report))
            sys.exit(3)

    for run_id, run in previous.items():
        print("INFO: copying run {} from previous report to result".format(run_id))
        add_to_result(result, run_id, run, ignites)

    save_yaml(sys.argv[3], result)


if __name__ == "__main__":
    main()
