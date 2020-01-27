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
import os
import types
import pytest
from pysper import sperf_default
from tests import current_dir, steal_output

@pytest.mark.skipif(os.environ.get("TEST_LEVEL") == "fast", reason="fast mode")
def test_sperf():
    """integration test"""
    args = types.SimpleNamespace()
    args.diag_dir = os.path.join(current_dir(__file__), "testdata", "diag", "DSE_CLUSTER")
    args.output_log_prefix = "output.log"
    args.debug_log_prefix = "debug.log"
    args.system_log_prefix = "system.log"
    args.node_info_prefix = "node_info.json"
    args.block_dev_prefix = "blockdev_report"
    args.cfstats_prefix = "cfstats"
    def run():
        sperf_default.run(args)
    output = steal_output(run)
        #reads better with the extra newline
    assert "\n" + output == """
nodes                               3                                                    
dse version(s) (startup logs)       { 6.7.7 }                                            
cassandra version(s) (startup logs) N/A                                                  
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
* There were 16 incidents of GC over 500ms. Run `sperf core gc` for more analysis."""

def test_empty_recommendations():
    """pass cthrough recommendations engine"""
    parsed = {"warnings": [], "rec_logs": [], "configs": {}}
    recommendations = sperf_default.generate_recommendations(parsed)
    assert not recommendations
