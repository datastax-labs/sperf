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
from pysper.search.filtercache import generate_recommendations


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
