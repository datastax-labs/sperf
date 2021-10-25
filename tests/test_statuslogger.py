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

"""tests for the base sperf command"""
import unittest
import os
import types
from pysper import VERSION
from pysper.commands.core import statuslogger
from tests import current_dir, steal_output


class TestSperf(unittest.TestCase):
    def test_sperf(self):
        """integration test, this is not the best test and only verifies no change in calculations
        as changes in the codebase occur."""
        args = types.SimpleNamespace()
        args.diag_dir = os.path.join(
            current_dir(__file__), "testdata", "diag", "DSE_CLUSTER"
        )
        args.files = []
        args.stages = "all"
        args.start = None
        args.end = None
        args.debug_log_prefix = "debug.log"
        args.reporter = "summary"
        args.system_log_prefix = "system.log"
        self.maxDiff = None

        def run():
            statuslogger.run(args)

        output = steal_output(run)
        # reads better with the extra newline
        self.assertEqual(
            output,
            "sperf core statuslogger version: %s\n" % (VERSION)
            + """
Summary (22,055 lines)
Summary (445 skipped lines)

dse versions: {'6.7.7'}
cassandra versions: {'DSE Private Fork'}
first log time: 2020-01-10 15:27:58.554000+00:00
last log time: 2020-01-10 17:21:13.549000+00:00
duration: 1.89 hours
total stages analyzed: 2
total nodes analyzed: 3

GC pauses  max        p99        p75        p50        p25        min
           ---        ---        ---        ---        ---        ---
ms         800        729        358        282        243        201
total GC events: 236

busiest tables by ops across all nodes
------------------------------
* 10.101.35.102: OpsCenter.rollups60: 66,464 ops / 3.38 mb data

busiest table by data across all nodes
------------------------------
* 10.101.35.102: my_solr.my_table: 37,132 ops / 9.37 mb data

busiest stages across all nodes
------------------------------
* CompactionExecutor active:   1  (10.101.35.102)
* TPC/0/WRITE_REMOTE active:   1  (10.101.35.102)
* CompactionExecutor pending:  1  (10.101.35.102)

busiest stages in PENDING
------------------------------
10.101.35.102:
       CompactionExecutor:  1

WARNING more than one version present assuming no version with recommendations""",
        )

    def test_sperf_68(self):
        """integration test, this is not the best test and only verifies no change in calculations
        as changes in the codebase occur."""
        args = types.SimpleNamespace()
        args.diag_dir = os.path.join(current_dir(__file__), "testdata", "dse68")
        args.files = []
        args.start = None
        args.end = None
        args.stages = "all"
        args.reporter = "summary"
        args.debug_log_prefix = "debug.log"
        args.system_log_prefix = "system.log"
        self.maxDiff = None

        def run():
            statuslogger.run(args)

        output = steal_output(run)
        # reads better with the extra newline
        self.assertEqual(
            output,
            "sperf core statuslogger version: %s\n" % (VERSION)
            + """
Summary (20,245 lines)
Summary (2,204 skipped lines)

dse versions: {'6.8.1'}
cassandra versions: {'DSE Private Fork'}
first log time: 2020-07-20 09:09:27.757000+00:00
last log time: 2020-07-22 13:49:40.782000+00:00
duration: 2.19 days
total stages analyzed: 17
total nodes analyzed: 1

GC pauses  max        p99        p75        p50        p25        min
           ---        ---        ---        ---        ---        ---
ms         2066       2066       1371       615        436        251
total GC events: 7

busiest tables by ops across all nodes
------------------------------
* 172.17.0.2: system.paxos: 103,106 ops / 309 bytes data

busiest table by data across all nodes
------------------------------
* 172.17.0.2: keyspace1.standard1: 4,237 ops / 45.40 mb data

busiest stages across all nodes
------------------------------
* TPC/1/READ_LOCAL pending:             100  (172.17.0.2)
* TPC/1/READ_LOCAL active:              32   (172.17.0.2)
* MemtablePostFlush pending:            6    (172.17.0.2)
* MemtableFlushWriter active:           3    (172.17.0.2)
* PerDiskMemtableFlushWriter_0 active:  2    (172.17.0.2)
* CompactionExecutor active:            1    (172.17.0.2)
* MemtablePostFlush active:             1    (172.17.0.2)
* TPC/all/EXECUTE_STATEMENT active:     1    (172.17.0.2)
* LwtStage active:                      1    (172.17.0.2)
* TPC/other active:                     1    (172.17.0.2)
* TPC/other/EXECUTE_STATEMENT active:   1    (172.17.0.2)
* TPC/0/TIMED_TIMEOUT active:           1    (172.17.0.2)

busiest stages in PENDING
------------------------------
172.17.0.2:
       TPC/1/READ_LOCAL:   100
       MemtablePostFlush:  6""",
        )
