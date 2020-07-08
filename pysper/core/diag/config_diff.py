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

"""formats the output of the diag parsed data"""
import json
import operator
from collections import OrderedDict

IGNORE_LIST = ['nodes_list', 'nodes']

def _get_common_configs(node_configs):
    common_config = OrderedDict()
    for i, node in enumerate(node_configs.keys()):
        if i == 0:
            #first configuration sets the base config
            common_config = {k:v for (k, v) in node_configs[node].items() if k not in IGNORE_LIST}
            continue
        for key, value in node_configs[node].items():
            if key in IGNORE_LIST:
                continue
            if key == "jvm_args":
                common_jvm_args = common_config.get("jvm_args")
                if not common_jvm_args:
                    continue
                new_common_jvm_args = OrderedDict()
                for arg, jvm_value in value.items():
                    common_jvm_value = common_jvm_args.get(arg)
                    if common_jvm_value == jvm_value:
                        new_common_jvm_args[arg] = jvm_value
                common_config["jvm_args"] = new_common_jvm_args
                continue
            if key in common_config and common_config.get(key) != value:
                del common_config[key]
    return common_config

def filter_unique_jvm_flags(jvm_flags):
    """filters out the always unique jvm flags from configuration comparision"""
    always_unique_jvm_flags = [
        '-XX:HeapDumpPath', '-Djava.io.tmpdir', \
         '-Djdk.internal.lambda.dumpProxyClasses', \
         '-XX:ErrorFile', '-Ddse.system_memory_in_mb',\
    ]
    return OrderedDict([x for x in jvm_flags.items() if x[0] not in always_unique_jvm_flags])

def filter_unique_config_flags(node_config_params):
    """filters out the always unique config params from configuration comparision"""
    always_unique_conf = ['node_configuration', 'listen_address', \
            'rpc_address', 'broadcast_rpc_address', \
            'broadcast_address', \
            'native_transport_address', \
            'native_transport_broadcast_address', \
            'system_info_encryption', 'data_file_directories', \
            'audit_logging_options', 'transparent_data_encryption_options', \
            'initial_token', \
    ]
    return OrderedDict([x for x in node_config_params.items() if x[0] not in always_unique_conf])

def _add_diff_from_common(node_configs):
    common_config = _get_common_configs(node_configs)
    for node, config in node_configs.items():
        diff = []
        config = filter_unique_config_flags(config)
        for key, value in config.items():
            if key == "jvm_args":
                common_jvm_args = common_config.get("jvm_args")
                if not common_jvm_args:
                    continue
                jvm_args = filter_unique_jvm_flags(value)
                for jvm_arg, jvm_value in jvm_args.items():
                    common_jvm_value = common_jvm_args.get(jvm_arg)
                    if jvm_value != common_jvm_value:
                        diff.append("%s:%s" % (jvm_arg, jvm_value))
                continue
            if key not in common_config and key not in IGNORE_LIST:
                diff.append("%s:%s" % (key, value))
        config["diff"] = diff
        node_configs[node] = config

def group_configurations(node_configs):
    """compares common configurations"""
    configurations = OrderedDict()
    _add_diff_from_common(node_configs)
    for node, config in node_configs.items():
        key = json.dumps(config["diff"])
        if key in configurations:
            current_config = configurations.get(key)
            current_config["nodes_list"].append(node)
            current_config["nodes"] = current_config["nodes"] + 1
            configurations[key] = current_config
        else:
            config["nodes_list"] = [node]
            config["nodes"] = 1
            configurations[key] = config
    keys = [(key, configurations[key]['nodes']) for key in configurations if key]
    #for consistent sort order
    keys.sort(key=operator.itemgetter(1, 0), reverse=True)
    results = []
    for item in keys:
        results.append(configurations[item[0]])
    return results
