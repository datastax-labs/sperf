# Copyright 2021 DataStax, Inc
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

"""tests for slow query """

import unittest
from datetime import datetime, timezone
from pysper.core import slowquery


class TestSlowQueryRegex(unittest.TestCase):
    """test sperf regex against various slowquery logs"""

    def test_begin_timeout(self):
        start = "DEBUG [ScheduledTasks:1] 2020-07-22 13:39:05,889  MonitoringTask.java:152 - 1 operations timed out in the last 5074 msecs:"
        p = slowquery.SlowQueryParser()
        m = p.begin_timed_out.match(start)
        self.assertTrue(m)
        self.assertEqual(m.group("numslow"), "1")
        self.assertEqual(m.group("date"), "2020-07-22 13:39:05,889")

    def test_timeout(self):
        log1 = "<SELECT * FROM keyspace1.standard1 WHERE key= 1>, total time 10058 msec, timeout 10000 msec"
        p = slowquery.SlowQueryParser()
        m = p.timed_out_match.match(log1)
        self.assertTrue(m)
        self.assertEqual(
            m.group("query"), "SELECT * FROM keyspace1.standard1 WHERE key= 1"
        )
        self.assertEqual(m.group("time"), "10058")
        self.assertEqual(m.group("threshold"), "10000")

    def test_slow_query(self):
        log1 = "<SELECT * FROM my_solr.my_table WHERE id = 00000000-0040-c812-0000-0000002016a4 LIMIT 5000>, time 1490 msec - slow timeout 500 msec/cross-node"
        p = slowquery.SlowQueryParser()
        m = p.slow_match.match(log1)
        self.assertTrue(m)
        self.assertEqual(
            m.group("query"),
            "SELECT * FROM my_solr.my_table WHERE id = 00000000-0040-c812-0000-0000002016a4 LIMIT 5000",
        )
        self.assertEqual(m.group("time"), "1490")


class TestSlowQueryLineParse(unittest.TestCase):
    """test sperf line parsing logic"""

    def test_slow(self):
        start = "DEBUG [ScheduledTasks:1] 2020-01-10 17:01:56,039  MonitoringTask.java:172 - 161 operations were slow in the last 5001 msecs:"
        log1 = "<SELECT * FROM my_solr.my_table WHERE id = 00000000-0040-c812-0000-0000002016a4 LIMIT 5000>, time 1490 msec - slow timeout 500 msec/cross-node"
        log2 = "<SELECT * FROM my_solr.my_table WHERE id = 00000000-004c-6471-0000-0000003cb986 LIMIT 5000>, time 1431 msec - slow timeout 500 msec/cross-node"

        p = slowquery.SlowQueryParser()
        g = p.parse([start, log1, log2])
        ret = next(g)
        self.assertEqual(
            ret["date"], datetime(2020, 1, 10, 17, 1, 56, 39000, tzinfo=timezone.utc)
        )
        self.assertEqual(ret["numslow"], 161)
        self.assertEqual(ret["type"], "slow")
        self.assertEqual(
            ret["query"],
            "SELECT * FROM my_solr.my_table WHERE id = 00000000-0040-c812-0000-0000002016a4 LIMIT 5000",
        )
        self.assertEqual(ret["time"], "1490")
        ret = next(g)
        self.assertEqual(ret["type"], "slow")
        self.assertEqual(
            ret["query"],
            "SELECT * FROM my_solr.my_table WHERE id = 00000000-004c-6471-0000-0000003cb986 LIMIT 5000",
        )
        self.assertEqual(ret["time"], "1431")

    def test_timeout(self):
        start = "DEBUG [ScheduledTasks:1] 2020-07-22 13:39:05,889  MonitoringTask.java:152 - 1 operations timed out in the last 5074 msecs:"
        log1 = "<SELECT * FROM keyspace1.standard1 WHERE key= 1>, total time 10058 msec, timeout 10000 msec"

        p = slowquery.SlowQueryParser()
        g = p.parse([start, log1])
        ret = next(g)
        self.assertEqual(ret["numslow"], 1)
        self.assertEqual(
            ret["date"], datetime(2020, 7, 22, 13, 39, 5, 889000, tzinfo=timezone.utc)
        )
        self.assertEqual(ret["type"], "timed_out")
        self.assertEqual(ret["query"], "SELECT * FROM keyspace1.standard1 WHERE key= 1")
        self.assertEqual(ret["time"], "10058")
        self.assertEqual(ret["threshold"], "10000")
