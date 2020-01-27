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
from pysper import env
from pysper.core.diag import parse_diag
from pysper.diag import find_files
from tests import current_dir

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
