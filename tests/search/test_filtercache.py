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

"""tests the filter cache file parsing and report generation"""
import unittest
import types

from pysper import parser, dates
from pysper.search.filtercache import generate_recommendations, calculate_eviction_stats


def _build_node(name, avg_evict_freq=10.0, avg_evict_duration=500.0):
    node = types.SimpleNamespace()
    node.name = name
    node.last_evict_item_limit = 64000
    node.byte_limit = 10
    node.item_limit = 5
    node.perc_item_limit = 0.95
    node.avg_evict_duration = avg_evict_duration
    node.avg_evict_freq = avg_evict_freq
    return node


class TestFilterCache(unittest.TestCase):
    """test filter cache"""

    def test_generate_recommendations_with_2_recs(self):
        """should note which one is most important"""
        node_info = [
            _build_node("node1", avg_evict_freq=10.0),
            _build_node("node2", avg_evict_freq=5.1),
            _build_node("node21", avg_evict_freq=5.1),
            _build_node("node22", avg_evict_freq=5.1),
            _build_node("node23", avg_evict_freq=5.1),
            _build_node("node3", avg_evict_freq=500.0, avg_evict_duration=2120.1),
        ]
        report = []
        generate_recommendations(report, node_info)
        output = "\n".join(report)
        self.assertEqual(
            """recommendations
---------------
NOTE: Do top recommendation first.

* affects nodes: node1, node2, node21
                 node22, node23
  reason: Filter cache evictions are happening too frequently.
  fix: Raise filter cache item limit from 64000 to 256000 via -Dsolr.solrfiltercache.maxSize.
* affects nodes: node3
  reason: Filter cache eviction duration is too long.
  fix: Lower filter cache item limit from 64000 to 32000 via -Dsolr.solrfiltercache.maxSize.
""",
            output,
        )

    def test_generate_recommmendations_with_no_recs(self):
        """list no recommendations"""
        node_info = [
            _build_node("node1", avg_evict_freq=110.0),
            _build_node("node2", avg_evict_freq=55.1),
            _build_node("node3", avg_evict_freq=50, avg_evict_duration=20),
        ]
        report = []
        generate_recommendations(report, node_info)
        self.assertEqual(report[0], "recommendations")
        self.assertEqual(report[1], "---------------")
        self.assertIn("No recommendations\n", report)
        self.assertNotIn("NOTE: Do top recommendation first.", report)

    def test_generate_report_with_1_rec(self):
        """show recommendation"""
        node_info = [
            _build_node("node1", avg_evict_freq=1.0),
            _build_node("node2", avg_evict_freq=50.1),
            _build_node("node3", avg_evict_freq=50, avg_evict_duration=10),
        ]
        report = []
        generate_recommendations(report, node_info)
        self.assertEqual(report[0], "recommendations")
        self.assertEqual(report[1], "---------------")
        self.assertIn(
            "reason: Filter cache evictions are happening too frequently.", report[2]
        )
        self.assertIn(
            "fix: Raise filter cache item limit from 64000 to 256000 via -Dsolr.solrfiltercache.maxSize.",
            report[2],
        )
        self.assertNotIn("NOTE: Do top recommendation first.", report)

    def test_calculate_eviction_stats(self):
        lines = [
            "INFO  [RemoteMessageServer query worker - 81] 2020-01-21 11:34:33,033  SolrFilterCache.java:340 - Filter cache org.apache.solr.search.SolrFilterCache$1@7c723229 has reached 8000000 entries of a maximum of 8000000. Evicting oldest entries...",
            "ERROR [RemoteMessageServer query worker - 18] 2020-01-21 11:34:34,475  MessageServer.java:277 - Failed to process request:",
            "INFO  [RemoteMessageServer query worker - 81] 2020-01-21 11:34:35,448  SolrFilterCache.java:356 - ...eviction completed in 1304 milliseconds. Filter cache org.apache.solr.search.SolrFilterCache$1@7c723229 usage is now 32441266 bytes across 4000000 entries.",
            "INFO  [LocalMessageServer query worker - 77] 2020-01-21 12:24:23,912  SolrFilterCache.java:340 - Filter cache org.apache.solr.search.SolrFilterCache$1@324b2c16 has reached 3999974 entries of a maximum of 8000000. Evicting oldest entries...",
            "INFO  [LocalMessageServer query worker - 77] 2020-01-21 12:24:23,912  SolrFilterCache.java:356 - ...eviction completed in 1 milliseconds. Filter cache org.apache.solr.search.SolrFilterCache$1@324b2c16 usage is now 32005744 bytes across 3999962 entries.",
            "INFO  [RemoteMessageServer query worker - 41] 2020-01-21 12:47:26,942  SolrFilterCache.java:311 - Filter cache org.apache.solr.search.SolrFilterCache$6@5af917a4 has reached 16 GB bytes of off-heap memory usage, the maximum is 16 GB. Evicting oldest entries...",
            "INFO  [RemoteMessageServer query worker - 41] 2020-01-21 12:47:26,950  SolrFilterCache.java:328 - ...eviction completed in 9 milliseconds. Filter cache org.apache.solr.search.SolrFilterCache$6@5af917a4 usage is now 114781220 across 159 entries.",
            # new version of logs, after DSP-18693
            "INFO  [RemoteMessageServer query worker - 41] 2020-01-21 12:47:26,942  SolrFilterCache.java:311 - Filter cache org.apache.solr.search.SolrFilterCache$6@5af917b6 has reached 16 GB bytes of off-heap memory usage, the maximum is 16 GB. Evicting oldest entries...",
            "INFO  [RemoteMessageServer query worker - 41] 2020-01-21 12:47:26,950  SolrFilterCache.java:328 - ...eviction completed in 8 milliseconds. Filter cache org.apache.solr.search.SolrFilterCache$6@5af917b6 usage is now 114781220 bytes across 159 entries.",
            # eviction event without duration log line
            "INFO  [RemoteMessageServer query worker - 41] 2020-01-21 12:47:26,970  SolrFilterCache.java:311 - Filter cache org.apache.solr.search.SolrFilterCache$6@5af917c7 has reached 16 GB bytes of off-heap memory usage, the maximum is 16 GB. Evicting oldest entries...",
        ]
        raw_events = parser.read_system_log(lines)
        after_time = dates.date_parse("2020-01-21 00:00:00,000")
        before_time = dates.date_parse("2020-02-21 00:00:00,000")
        item_ev_stats, bytes_ev_stats = calculate_eviction_stats(
            raw_events, after_time, before_time
        )
        assert len(item_ev_stats.values()) == 2
        assert sum([s.duration for s in item_ev_stats.values()]) == 1304 + 1
        assert len(bytes_ev_stats.values()) == 3
        assert sum([s.duration for s in bytes_ev_stats.values()]) == 9 + 8 + 0
