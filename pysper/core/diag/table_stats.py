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

"""processing of the table/cf stats files"""
from pysper.parser import cfstats
from pysper import util, env

def _parse_cfstats(cfstats_files):
    node_parsed_map = {}
    warnings = []
    for cfstat_file in cfstats_files:
        node = util.extract_node_name(cfstat_file)
        try:
            parsed = cfstats.read_file(cfstat_file)
            node_parsed_map[node] = parsed
        except IOError as e:
            warnings.append(e)
            continue
    return node_parsed_map, warnings

def _add_busiest_table(config, node_parsed_map):
    total_writes = 0
    total_reads = 0
    table_read_count = {}
    table_write_count = {}
    for node in config.get("nodes_list", []):
        if node not in node_parsed_map:
            continue
        parsed = node_parsed_map[node]
        for keyspace, table_map in parsed.items():
            for table, cfstat in table_map.items():
                full_table = "%s.%s" % (keyspace, table)
                current_writes = cfstat.get('Local write count', 0)
                total_writes = total_writes + current_writes
                table_write_count[full_table] = table_write_count.get(full_table, 0) + current_writes
                current_read = cfstat.get('Local read count', 0)
                total_reads = total_reads + current_read
                table_read_count[full_table] = table_read_count.get(full_table, 0) + current_read
    _busiest(total_reads, table_read_count, 'busiest_table_reads', config)
    _busiest(total_writes, table_write_count, 'busiest_table_writes', config)

def _busiest(total, table_map, cat, config):
    for table, count in table_map.items():
        perc = (float(count)/float(total)) * 100
        if perc > config[cat][1]:
            config[cat] = (table, perc)

def _worst_per_config(config, node_parsed_map):
    for node in config.get("nodes_list", []):
        if node not in node_parsed_map:
            if env.DEBUG:
                print("node '%s' not found in node list '%s'" %(node, ", ".join(node_parsed_map.keys())))
            continue
        parsed = node_parsed_map[node]
        for keyspace, table_map in parsed.items():
            for table, cfstat in table_map.items():
                full_table = "%s.%s" % (keyspace, table)
                current_write_latency = float(cfstat.get('Local write latency', 0.0))
                if current_write_latency > config['worst_write_latency'][2]:
                    config['worst_write_latency'] = (node, full_table, current_write_latency)
                current_read_latency = float(cfstat.get('Local read latency', 0.0))
                if current_read_latency > config['worst_read_latency'][2]:
                    config['worst_read_latency'] = (node, full_table, current_read_latency)
                current_tombstone = cfstat.get('Maximum tombstones per slice (last five minutes)', 0)
                if current_tombstone > config['worst_tombstone'][2]:
                    config['worst_tombstone'] = (node, full_table, current_tombstone)
                current_live = cfstat.get('Maximum live cells per slice (last five minutes)', 0)
                if current_live > config['worst_live_cells'][2]:
                    config['worst_live_cells'] = (node, full_table, current_live)
                current_table_size = cfstat.get('Space used (live)', 0)
                if  current_table_size > config['largest_table'][2]:
                    config['largest_table'] = (node, full_table, current_table_size)
                _add_worst_part(config, cfstat, full_table, node)

def _add_worst_part(config, cfstat, full_table, node):
    current_worst_part = cfstat.get('Compacted partition maximum bytes', 0)
    if current_worst_part > config['worst_part_size'][2]:
        mean_part = cfstat.get('Compacted partition mean bytes')
        min_part = cfstat.get('Compacted partition minimum bytes')
        config['worst_part_size'] = (full_table, node, current_worst_part, mean_part, min_part)

def add_stats_to_config(configs, cfstats_files):
    """gets the worst cfstats for each configuration"""
    node_parsed_map, warnings = _parse_cfstats(cfstats_files)
    for config in configs:
        config['worst_read_latency'] = ("", "", 0.0)
        config['worst_write_latency'] = ("", "", 0.0)
        config['worst_tombstone'] = ("", "", 0)
        config['worst_live_cells'] = ("", "", 0)
        config['largest_table'] = ("", "", 0)
        config['busiest_table_reads'] = ('', 0.0)
        config['busiest_table_writes'] = ('', 0.0)
        config['worst_part_size'] = ('', '', 0, 0, 0)
        _worst_per_config(config, node_parsed_map)
        _add_busiest_table(config, node_parsed_map)
    return warnings
