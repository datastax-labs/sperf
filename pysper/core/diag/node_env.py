# Copyright 2020 DataStax, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""gets the node environment from the output log"""
import os
from pysper import diag, parser, util, env, humanize

def initialize_node_configs(diag_dir):
    """generates a list of empty configuration for each node directory"""
    matches = {}
    files = []
    node_dir = os.path.join(diag_dir, "nodes")
    try:
        files = os.listdir(node_dir)
    except Exception as ex:
        if env.DEBUG:
            print(ex)
        raise diag.UnableToReadDiagException(diag_dir, ex)
    for filename in files:
        matches[filename] = {}
    return matches

def _find_configuration_events(events):
    config = {}
    keys = ['version', 'cassandra_version', 'spark_version', 'dse_spark_version',
            'solr_version', 'spark_connector_version', 'cpu_cores', 'threads_per_core',
            'logged_disk_access_mode', 'logged_index_access_mode',
            'jvm_args', 'node_configuration',
            ]
    for event in events:
        for key in keys:
            if key in event:
                config[key] = event[key]
    cassandra_config = read_cassandra_config(config.get('node_configuration', {}))
    for key, value in cassandra_config.items():
        config[key] = value
        results = read_jvm_based_parameters(config.get('jvm_args', []))
        config['heap_size'] = results[0]
        config['gc'] = results[1]
        config['ram_in_mb'] = results[2]
    return config

def find_config_in_logs(node_configs, output_logs, system_logs):
    """read the output logs and extract the configuration from each file"""
    warnings = []
    node_logs = {}
    for system_log in system_logs:
        node = util.extract_node_name(system_log)
        if node not in node_logs:
            node_logs[node] = {"system": [], "output":""}
        node_logs[node]["system"].append(system_log)
    for output_log in output_logs:
        node = util.extract_node_name(output_log)
        if node not in node_logs:
            node_logs[node] = {"system": [], "output":""}
        node_logs[node]["output"] = output_log
    for node, logs in node_logs.items():
        output_log = logs.get("output")
        system_logs = logs.get("system")
        events = []
        with diag.FileWithProgress(output_log) as output_log_file:
            if output_log_file.file_desc:
                events = parser.read_output_log(output_log_file)
                node_configs[node] = _find_configuration_events(events)
                continue
            #try the system logs to find the last configuration found
            for system_log in system_logs:
                with diag.FileWithProgress(system_log) as system_log_file:
                    if system_log_file.error:
                        #skip files we can't read
                        continue
                    #yes I know this looks like I'm crazy but the output log parser is what I'm interested in
                    events.extend(parser.read_output_log(system_log_file))
            #I only one the most recent logs in the system log to be used
            events = sorted(events, key=lambda e: e["date"], reverse=False)
            node_configs[node] = _find_configuration_events(events)
    return warnings

def add_gc_to_configs(configs, system_logs):
    """read the system logs and extract the configuration from each file"""
    results = {}
    warnings = []
    for system_log in system_logs:
        with diag.FileWithProgress(system_log) as system_log_file:
            if system_log_file.error:
                warnings.append(system_log_file.error)
            events = parser.read_system_log(system_log_file)
            worst_gc = 0
            for event in events:
                if event.get('event_type') == 'pause' and event.get('event_category') == 'garbage_collection':
                    worst_gc = max(event.get('duration'), worst_gc)
            node = util.extract_node_name(system_log)
            results[node] = worst_gc
    for config in configs:
        worst_gc_per_config = 0
        worst_node = ""
        for node in config.get('nodes_list', []):
            node_worst_gc = results.get(node, 0)
            if node_worst_gc > worst_gc_per_config:
                worst_gc_per_config = node_worst_gc
                worst_node = node
        config['worst_gc'] = (worst_gc_per_config, worst_node)
    return warnings

def read_jvm_based_parameters(jvm_args):
    """finds the max heap, system ram and gc type from the jvm args.
    the last system ram argument is used as this tends to be duplicate frequently"""
    gc_type = None
    ram_in_mb = None
    heap_size = None
    for args in jvm_args:
        if args.startswith('-Ddse.system_memory_in_mb'):
            value = jvm_args[args]
            #note it's, very very common to have multiple of these in the configuration
            # we are only interested in the last one
            # diffs on jvm args will reveal configuration differences between nodes
            if value:
                ram_in_mb = humanize.format_bytes(int(value[-1])* 1024 ** 2, 0)
        if args == '-XX:+UseG1GC':
            if gc_type:
                #should never see this
                gc_type = "%s/G1Gc" % gc_type
            else:
                gc_type = "G1GC"
        elif args == "-XX:+UseConcMarkSweepGC":
            if gc_type:
                #should never see this
                gc_type = "CMS/%s" % gc_type
            else:
                gc_type = "CMS"
        elif args.startswith('-Xmx'):
            heap_size = "".join(args[4:])
    return (heap_size, gc_type, ram_in_mb)

def read_cassandra_config(cassandra_params):
    """splits out the cassandra parameters"""
    config = {}
    for key, value in cassandra_params.items():
        if value and key:
            if value == 'null':
                config[key] = 'default'
            else:
                config[key] = value
    return config
