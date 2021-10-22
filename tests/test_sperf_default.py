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
from pysper import sperf_default
from tests import current_dir, steal_output, make_67_diag_args


class TestSperfDefaultIntegration(unittest.TestCase):
    """integration tests for sperf default"""

    def test_sperf(self):
        """integration test"""
        args = make_67_diag_args()

        def run():
            sperf_default.run(args)

        output = steal_output(run)
        # reads better with the extra newline
        self.maxDiff = None
        self.assertEqual(
            "\n" + output,
            """
nodes                               3
dse version(s) (startup logs)       { 6.7.7 }
cassandra version(s) (startup logs) { DSE private fork }
solr version(s) (startup logs)      { 6.0.1.2.2647 }
spark version(s) (startup logs)     { 2.2.3.9 }
worst gc pause (system logs)        800.00 ms (10.101.35.71)
worst read latency (cfstats)        6.11 ms (system_schema.keyspaces 10.101.35.102)
worst write latency (cfstats)       4.72 ms (system_schema.dropped_columns 10.101.35.102)
worst tombstones query (cfstats)    319 (system_distributed.nodesync_status 10.101.35.71)
worst live cells query (cfstats)    447 (system_schema.columns 10.101.35.71)
largest table (cfstats)             my_solr.my_table (133.46 mb 10.101.35.102)
busiest table reads (cfstats)       my_solr.my_table (99.78% of reads)
busiest table writes (cfstats)      my_solr.my_table (95.80% of writes)
largest partition (cfstats)         28.83 kb system.size_estimates (10.101.35.71)

errors parsing
--------------
No parsing errors

recommendations
---------------
* There were 16 incidents of GC over 500ms. Run `sperf core gc` for more analysis.
* There were drops of the following request types: MUTATION for a total of 1096 drops. Run sperf core statuslogger and look for high pending stages for those messages types.
* Global local backpressure was active on the following nodes: 10.101.35.102 (1 times). GC was over target %s times however despire TPC backpressure being active it may be dangerous to raise TPC limits, run sperf core statuslogger for further analysis on the type of requests that are pending.""",
        )

    def test_sperf_68(self):
        """integration test"""
        args = types.SimpleNamespace()
        args.diag_dir = os.path.join(current_dir(__file__), "testdata", "dse68")
        args.output_log_prefix = "output.log"
        args.debug_log_prefix = "debug.log"
        args.system_log_prefix = "system.log"
        args.node_info_prefix = "node_info.json"
        args.block_dev_prefix = "blockdev_report"
        args.cfstats_prefix = "cfstats"
        self.maxDiff = None

        def run():
            sperf_default.run(args)

        output = steal_output(run)
        # reads better with the extra newline
        self.assertEqual(
            "\n" + output,
            """
WARN cannot find -XX:MaxGCPauseMillis in the logs setting common default of 500ms

nodes                               1
dse version(s) (startup logs)       { 6.8.1 }
cassandra version(s) (startup logs) { DSE private fork }
solr version(s) (startup logs)      { 6.0.1.4.2746 }
spark version(s) (startup logs)     { 2.4.0.14 }
worst gc pause (system logs)        2.07 seconds (172.17.0.2)
worst read latency (cfstats)        0.19 ms (dse_insights.insights_config 172.17.0.2)
worst write latency (cfstats)       0.42 ms (system.sstable_activity 172.17.0.2)
worst tombstones query (cfstats)    1 (dse_system.shared_data 172.17.0.2)
worst live cells query (cfstats)    639 (system_schema.columns 172.17.0.2)
largest table (cfstats)             keyspace1.standard1 (1.79 gb 172.17.0.2)
busiest table reads (cfstats)       system.paxos (64.62% of reads)
busiest table writes (cfstats)      keyspace1.standard1 (99.27% of writes)
largest partition (cfstats)         41.51 kb keyspace1.standard1 (172.17.0.2)

errors parsing
--------------
* missing output logs: all nodes
* unable to read 'node_info.json'

recommendations
---------------
* There were 5 incidents of GC over 500ms. Run `sperf core gc` for more analysis.
* There were drops of the following request types: RANGE_SLICE, LWT for a total of 8 drops. Run sperf core statuslogger and look for high pending stages for those messages types.
* There were 2 incidents of zero copy errors related to bloom filter generation. This COULD be an explaination for increased read latencies, however, this error can be only due to the sstables being so small they are immediately deleted and therefore there is no bloom filter generated. In that case there is no issue with this warning. Keep an eye on this. If there are no other good explainations for increased latencies run `nodetool upgradesstables -s` on each node then restart to regenerate and load new bloom filters.
* Local core backpressure was active on the following nodes: 172.17.0.2 (320 times - 3 different cores). GC was over target %s times however despire TPC backpressure being active it may be dangerous to raise TPC limits, run sperf core statuslogger for further analysis on the type of requests that are pending.
* TPC core imbalance detected on nodes: 172.17.0.2 (1 times). The data model is likely broken. Look for time series with large buckets and little randomization of writes, large IN queries, and hot partitions on writes. On DSE versions before 6.8.5 consider upgrading first before changing the data model.
* Tombstone warnings found, there were 1001 total tombstones scanned. The data model has a problem.""",
        )

    def test_empty_recommendations(self):
        """pass cthrough recommendations engine"""
        self.maxDiff = None
        parsed = {"warnings": [], "rec_logs": [], "configs": {}}
        recommendations = sperf_default.generate_recommendations(parsed)
        self.assertEqual(len(recommendations), 0)
