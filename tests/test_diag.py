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

"""'cass diag' parsing and report writing tests"""
import os
import types
import pytest
from tests import current_dir, steal_output, make_67_diag_args
from pysper import env
from pysper.core.diag import parse_diag
from pysper.diag import find_files
from pysper.commands.core import diag as diag_cmd

def test_find_files_by_diag_dir():
    """find logs by diag dir"""
    config = types.SimpleNamespace()
    test_dir = os.path.join(current_dir(__file__), "testdata", "diag", "findfiles")
    config.diag_dir = test_dir
    config.files = ""
    files = find_files(config, "my.log")
    assert len(files) == 4
    assert os.path.join(test_dir, "nodes", "node1", "my.log") in files
    assert os.path.join(test_dir, "nodes", "node1", "my.log.1") in files
    assert os.path.join(test_dir, "nodes", "node1", "my.log.2") in files
    assert os.path.join(test_dir, "nodes", "node1", "debug.log") not in files
    assert os.path.join(test_dir, "nodes", "node2", "my.log") in files
    assert os.path.join(test_dir, "nodes", "node2", "debug.log") not in files


def test_find_files_by_files_param():
    """find logs by file name and not just looking in a diag for all matches"""
    config = types.SimpleNamespace()
    test_dir = os.path.join(current_dir(__file__), "testdata", "diag", "findfiles")
    config.diag_dir = ""
    config.files = os.path.join(test_dir, "nodes", "node1", "my.log") + "," + \
                    os.path.join(test_dir, "nodes", "node2", "my.log")
    files = find_files(config, "my.log")
    assert len(files) == 2
    assert os.path.join(test_dir, "nodes", "node1", "my.log") in files
    assert os.path.join(test_dir, "nodes", "node1", "my.log.1") not in files
    assert os.path.join(test_dir, "nodes", "node1", "my.log.2") not in files
    assert os.path.join(test_dir, "nodes", "node1", "debug.log") not in files
    assert os.path.join(test_dir, "nodes", "node2", "my.log") in files
    assert os.path.join(test_dir, "nodes", "node2", "debug.log") not in files

def test_parse_diag():
    """happy path test for parsing a diag tarball"""
    config = types.SimpleNamespace()
    test_dir = os.path.join(current_dir(__file__), "testdata", "diag", "DSE_CLUSTER")
    config.diag_dir = test_dir
    config.node_info_prefix = "node_info.json"
    config.system_log_prefix = "system.log"
    config.output_log_prefix = "output.log"
    config.cfstats_prefix = "cfstats"
    config.block_dev_prefix = "blockdev_report"
    env.DEBUG = True
    parsed = {}
    try:
        parsed = parse_diag(config)
    finally:
        env.DEBUG = False
    assert not parsed.get("warnings")
    first = parsed.get("configs")[0]
    assert first['busiest_table_writes']
    assert first['busiest_table_writes'][0] == 'my_solr.my_table'
    assert "%.2f" % first['busiest_table_writes'][1] == '96.18'
    assert first['busiest_table_reads'][0] == 'my_solr.my_table'
    assert "%.2f" % first['busiest_table_reads'][1] == '99.76'
    assert first['threads_per_core'] == 1

def test_parse_diag_reports_no_files_found():
    """should see missing files in the warning list"""
    config = types.SimpleNamespace()
    test_dir = os.path.join(current_dir(__file__), "testdata", "diag", "empty")
    config.diag_dir = test_dir
    config.node_info_prefix = "node_info.json"
    config.system_log_prefix = "system.log"
    config.output_log_prefix = "output.log"
    config.cfstats_prefix = "cfstats"
    config.block_dev_prefix = "blockdev_report"
    parsed = parse_diag(config)
    warnings = parsed.get("warnings")
    assert len(warnings) == 4
    assert "missing output logs: all nodes" in warnings
    assert "unable to read 'node_info.json'" in warnings
    assert "missing system logs: all nodes" in warnings
    assert "missing cfstats: all nodes" in warnings

def test_parse_diag_reports_missing_files():
    """should see missing files in the warning list"""
    config = types.SimpleNamespace()
    test_dir = os.path.join(current_dir(__file__), "testdata", "diag", "missing")
    config.diag_dir = test_dir
    config.node_info_prefix = "node_info.json"
    config.system_log_prefix = "system.log"
    config.output_log_prefix = "output.log"
    config.cfstats_prefix = "cfstats"
    config.block_dev_prefix = "blockdev_report"
    parsed = parse_diag(config)
    warnings = parsed.get("warnings")
    assert len(warnings) == 4
    assert "missing output logs: node2" in warnings
    assert "missing blockdev_reports: node2" in warnings
    assert "missing system logs: node2" in warnings
    assert "missing cfstats: node2" in warnings

@pytest.mark.skipif(os.environ.get("TEST_LEVEL") == "fast", reason="fast mode")
def test_core_diag_integtration():
    """integration test with 6.7 tarball"""
    args = make_67_diag_args()
    def run():
        diag_cmd.run(args)
    output = steal_output(run)
    assert output == """sperf core diag version: 0.6.4


configuration #1
----------------
nodes count                   2
cass drive(s) read ahead      N/A
dse version                   6.7.7
cassandra version             N/A
solr version                  6.0.1.2.2647
spark version                 2.2.3.9
spark connector version       N/A
disk access mode              standard
disk optimization             ssd
memtable cleanup threshold    default
flush writers                 default
compaction throughput         16 mb
concurrent compactors         default
memtable size (heap)          default
memtable size (offheap)       default
memtable allocation type      offheap_objects
file cache size               default
heap size                     3759M
gc                            G1GC
total ram                     15 gb
total cpu cores (real)        8
threads per core              1
worst gc pause                800.00 ms (10.101.35.71)
worst write latency (all)     4.22 ms (system_schema.dropped_columns 10.101.35.71)
worst read latency (all)      2.88 ms (system.local 10.101.35.71)
worst tombstones query (all)  319 (system_distributed.nodesync_status 10.101.35.71)
worst live cells query (all)  447 (system_schema.columns 10.101.35.71)
largest table                 my_solr.my_table (133.32 mb 10.101.35.71)
busiest table reads           my_solr.my_table (99.76% of reads)
busiest table writes          my_solr.my_table (96.18% of writes)
worst partition in            system.size_estimates (10.101.35.71)
* max partition size          28.83 kb
* mean partition size         8.10 kb
* min partition size          2.25 kb

nodes
-----
10.101.35.71, 10.101.33.205


config diff from common:
* listen_interface: eth0

configuration #2
----------------
nodes count                   1
cass drive(s) read ahead      N/A
dse version                   6.7.7
cassandra version             N/A
solr version                  6.0.1.2.2647
spark version                 2.2.3.9
spark connector version       N/A
disk access mode              standard
disk optimization             ssd
memtable cleanup threshold    default
flush writers                 default
compaction throughput         16 mb
concurrent compactors         default
memtable size (heap)          default
memtable size (offheap)       default
memtable allocation type      offheap_objects
file cache size               default
heap size                     3759M
gc                            G1GC
total ram                     15 gb
total cpu cores (real)        8
threads per core              1
worst gc pause                258.00 ms (10.101.35.102)
worst write latency (all)     4.72 ms (system_schema.dropped_columns 10.101.35.102)
worst read latency (all)      6.11 ms (system_schema.keyspaces 10.101.35.102)
worst tombstones query (all)  7 (OpsCenter.events 10.101.35.102)
worst live cells query (all)  447 (system_schema.columns 10.101.35.102)
largest table                 my_solr.my_table (133.46 mb 10.101.35.102)
busiest table reads           my_solr.my_table (99.81% of reads)
busiest table writes          my_solr.my_table (95.04% of writes)
worst partition in            system_schema.columns (10.101.35.102)
* max partition size          9.66 kb
* mean partition size         2.16 kb
* min partition size          180 bytes

nodes
-----
10.101.35.102


config diff from common:
* listen_interface: default

parser warnings
---------------
no warnings"""
