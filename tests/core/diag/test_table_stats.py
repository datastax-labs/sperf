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

"""tests table_stats module"""
import os
from pysper.core.diag import table_stats
from tests import test_dse_tarball

def test_add_stats_to_config():
    """happy path"""
    configs = [{"nodes_list":["10.101.33.205"]}, {"node_list":["10.101.35.102"]}]
    cfstats_files = []
    for node_name in ["10.101.33.205", "10.101.35.102", "10.101.35.71"]:
        cfstat_file = os.path.join(test_dse_tarball(), "nodes", node_name, "nodetool", "cfstats")
        cfstats_files.append(cfstat_file)
    table_stats.add_stats_to_config(configs, cfstats_files)
    first_config = configs[0]
    assert first_config['worst_read_latency'] == ('10.101.33.205', 'OpsCenter.rollup_state', 1.704)
    assert first_config['worst_write_latency'] == ('10.101.33.205', 'system_schema.dropped_columns', 4.009)
    assert first_config['worst_tombstone'] == ('10.101.33.205', 'OpsCenter.events', 7)
    assert first_config['worst_live_cells'] == ('10.101.33.205', 'system_schema.columns', 447)
    assert first_config['largest_table'] == ('10.101.33.205', 'my_solr.my_table', 113553687)
    assert first_config['busiest_table_reads'][0] == 'my_solr.my_table'
    assert "%.2f" % first_config['busiest_table_reads'][1] == '99.75'
    assert first_config['busiest_table_writes'][0] == 'my_solr.my_table'
    assert "%.2f" % first_config['busiest_table_writes'][1] == '96.76'
    assert first_config['worst_part_size'][0] == 'system.size_estimates'
    assert first_config['worst_part_size'][1] == '10.101.33.205'
    assert first_config['worst_part_size'][2] == 17084
    assert first_config['worst_part_size'][3] == 6924
    assert first_config['worst_part_size'][4] == 2760
