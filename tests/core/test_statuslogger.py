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

""" tests the statuslogger module """
import os
from pysper.core.statuslogger import StatusLogger, Summary
from tests import test_dse_tarball, current_dir

def test_should_count_ops():
    """validate ops counting is doing the right thing even when crossing logs"""
    tarball = os.path.join(current_dir(__file__), '..', 'testdata', 'sample_table_tarball')
    sl = StatusLogger(tarball)
    sl.analyze()
    s = Summary(sl.nodes)
    tables = s.get_busiest_tables('ops')
    #this proves the extra logs in debug.log and system.log that are duplicate are ignored
    #and that the extra entry from statuslogger is not causing a double count
    busiest = tables[0]
    assert busiest[1][0] == 'keyspace1.standard1'
    assert busiest[1][1].ops == 5931
    assert busiest[1][1].data == 75690238


def test_skip_duplicate_events_diag():
    """should merge events on the same node in different logs"""
    sl = StatusLogger(test_dse_tarball())
    sl.analyze()
    assert sl.analyzed
    assert len(sl.nodes) == 3
    s = Summary(sl.nodes)
    assert s.lines == 22054
    assert s.skipped_lines == 444
    assert s.get_busiest_stages()[0] == ['10.101.35.102', 'active', 'CompactionExecutor', 1]

def test_db2552_debug_log_format():
    """should work with new statuslogger files"""
    files = [os.path.join(current_dir(__file__), '..', 'testdata', 'statusloggernew_debug.log')]
    sl = StatusLogger(None, files=files)
    sl.analyze()
    assert sl.analyzed
    s = Summary(sl.nodes)
    busiest_stages = s.get_busiest_stages()
    name, status, stage, value = busiest_stages[0]
    assert name == files[0]
    assert stage == "TPC/all/WRITE_REMOTE"
    assert status == "pending"
    assert value == 13094

def test_db2552_system_log_format():
    """should work with new statuslogger files"""
    files = [os.path.join(current_dir(__file__), '..', 'testdata', 'statuslogger_new.log')]
    sl = StatusLogger(None, files=files)
    sl.analyze()
    assert sl.analyzed
    s = Summary(sl.nodes)
    busiest_stages = s.get_busiest_stages()
    name, status, stage, value = busiest_stages[0]
    assert name == files[0]
    assert stage == "TPC/all/WRITE_REMOTE"
    assert status == "pending"
    assert value == 13094

def test_68_debug_log_format():
    """should work with DSE 6.8 statuslogger debug files"""
    files = [os.path.join(current_dir(__file__), '..', 'testdata', 'statuslogger68_debug.log')]
    sl = StatusLogger(None, files=files)
    sl.analyze()
    assert sl.analyzed
    s = Summary(sl.nodes)
    busiest_stages = s.get_busiest_stages()
    name, status, stage, value = busiest_stages[0]
    assert name == files[0]
    assert stage == "TPC/all/WRITE_REMOTE"
    assert status == "pending"
    assert value == 13094

def test_68_system_log_format():
    """should work with DSE 6.8 statuslogger files"""
    files = [os.path.join(current_dir(__file__), '..', 'testdata', 'statuslogger_68.log')]
    sl = StatusLogger(None, files=files)
    sl.analyze()
    assert sl.analyzed
    s = Summary(sl.nodes)
    busiest_stages = s.get_busiest_stages()
    name, status, stage, value = busiest_stages[0]
    assert name == files[0]
    assert stage == "TPC/all/WRITE_REMOTE"
    assert status == "pending"
    assert value == 13094
