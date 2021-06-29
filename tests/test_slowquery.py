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
from pysper.commands.core import slowquery
from tests import current_dir, steal_output


class TestSperfDefault(unittest.TestCase):
    """test sperf default"""

    def test_sperf(self):
        """integration test, this is not the best test and only verifies no change in calculations
        as changes in the codebase occur."""
        self.maxDiff = None
        args = types.SimpleNamespace()
        args.diag_dir = os.path.join(
            current_dir(__file__), "testdata", "diag", "DSE_CLUSTER"
        )
        args.files = []
        args.top = 3
        args.interval = 3600
        args.start = None
        args.end = None

        def run():
            slowquery.run(args)

        output = steal_output(run)
        # reads better with the extra newline
        self.assertEqual(
            output,
            "sperf core slowquery version: %s" % (VERSION)
            + "\n\n"
            + """this is not a very accurate report, use it to discover basics, but I suggest analyzing the logs by hand for any outliers

. <574ms + >661ms ! >1285ms X >1687ms
------------------------------
2020-01-10 16:58:55.839000+00:00  ........................!!.!!++++!+!.!!.++!+!+..+..X.++!+!!.+!.!+!++!!.+.+.

worst period: 2020-01-10 16:58:55.839000+00:00 (65342ms)

slow query breakdown
--------------------
75 total, 48 cross-node, 0 timeouts

Top 3 slow queries:
------------------------------
1688ms: SELECT * FROM my_solr.my_table WHERE id = 00000000-0041-d584-0000-0000004956fd LIMIT 5000

1535ms: SELECT * FROM my_solr.my_table WHERE id = 00000000-0047-87cc-0000-0000004e94af LIMIT 5000

1522ms: SELECT * FROM my_solr.my_table WHERE id = 00000000-0008-b249-0000-00000044c1f3 LIMIT 5000""",
        )

    def test_sperf_68(self):
        """integration test for DSE 6.8 format, this is not the best test and only verifies no change in calculations
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
        # reads better with the extra newline
        self.assertEqual(
            output,
            "sperf core slowquery version: %s" % (VERSION)
            + "\n\n"
            + """this is not a very accurate report, use it to discover basics, but I suggest analyzing the logs by hand for any outliers

. <10000ms + >10003ms ! >10005ms X >10057ms
------------------------------
2020-07-22 13:39:05.889000+00:00  .X.+.!!.

worst period: 2020-07-22 13:39:05.889000+00:00 (72158ms)

slow query breakdown
--------------------
8 total, 0 cross-node, 7 timeouts

Top 3 slow queries:
------------------------------
10058ms: SELECT * FROM keyspace1.standard1 WHERE key= 1

10006ms: SELECT * FROM keyspace1.standard1 WHERE C3 = 30783739393164656164636535346463653436633764343738393962313463616366396262623565643135366538613864386630396562336233343235623662373464386563 AND  LIMIT 1

10006ms: SELECT * FROM keyspace1.standard1 WHERE C2 = 307836313933373336353935666436333031643163 AND  LIMIT 1""",
        )
