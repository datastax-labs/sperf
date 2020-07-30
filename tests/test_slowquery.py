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
from pysper import VERSION
from pysper.commands.core import slowquery
from tests import current_dir, steal_output

@pytest.mark.skipif(os.environ.get("TEST_LEVEL") == "fast", reason="fast mode")
def test_sperf():
    """integration test, this is not the best test and only verifies no change in calculations
as changes in the codebase occur."""
    args = types.SimpleNamespace()
    args.diag_dir = os.path.join(current_dir(__file__), "testdata", "diag", "DSE_CLUSTER")
    args.files = []
    args.top = 3
    args.interval = 3600
    args.start = None
    args.end = None
    def run():
        slowquery.run(args)
    output = steal_output(run)
        #reads better with the extra newline
    assert output == "sperf core slowquery version: %s" % (VERSION) + """

. <5000ms + >5000ms ! >5004ms X >5004ms
------------------------------
2020-01-10 16:58:55.839000+00:00  XXXXXXXXXXXXXXXXXXXXXXXX++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

worst period: 2020-01-10 16:58:55.839000+00:00 (930282ms)

3 slow queries, 1 cross-node

Top 3 slow queries:
------------------------------
5005ms: <SELECT * FROM my_solr.my_table WHERE id = 00000000-0057-1aa2-0000-0000002c726f LIMIT 5000>

5001ms: <SELECT * FROM my_solr.my_table WHERE id = 00000000-0040-c812-0000-0000002016a4 LIMIT 5000>

5001ms: <SELECT * FROM my_solr.my_table WHERE id = 00000000-004f-c914-0000-0000004d6abe LIMIT 5000>"""

@pytest.mark.skipif(os.environ.get("TEST_LEVEL") == "fast", reason="fast mode")
def test_sperf_68():
    """integration test, this is not the best test and only verifies no change in calculations
as changes in the codebase occur."""
    args = types.SimpleNamespace()
    args.diag_dir = os.path.join(current_dir(__file__), "testdata", "dse68")
    args.files = []
    args.top = 3
    args.interval = 3600
    args.start = None
    args.end = None
    def run():
        slowquery.run(args)
    output = steal_output(run)
        #reads better with the extra newline
    assert output == "sperf core slowquery version: %s" % (VERSION) + """

. <5073ms + >5073ms ! >5073ms X >5073ms
------------------------------
2020-07-22 13:39:05.889000+00:00  X

worst period: 2020-07-22 13:39:05.889000+00:00 (5074ms)

1 slow queries, 0 cross-node

Top 3 slow queries:
------------------------------
5074ms: <SELECT config FROM dse_insights.insights_config WHERE key = 1>"""
