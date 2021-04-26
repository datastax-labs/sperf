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

"""validate utility functions"""
import unittest
import os
import datetime
from collections import defaultdict
from pysper import util


class TestUtil(unittest.TestCase):
    """test the util module"""

    def test_extract_node_name(self):
        """simple test of split handling in a path"""
        my_node = util.extract_node_name(os.path.join("exy", "abc", "nodes", "my_node"))
        self.assertEqual(my_node, "my_node")

        # should match last nodes token
        my_node = util.extract_node_name(
            os.path.join("exy", "nodes", "abc", "nodes", "my_node")
        )
        self.assertEqual(my_node, "my_node")

    def test_bucketize(self):
        """test bucketize"""
        junk = defaultdict(list)
        data = [1, 1, 1, 1, 1, 1, 1, 1]
        junk[datetime.datetime(2019, 5, 11, 0, 0, 0, 0)] = data
        junk[datetime.datetime(2019, 5, 11, 1, 0, 0, 0)] = data
        junk[datetime.datetime(2019, 5, 11, 2, 0, 0, 0)] = data
        junk[datetime.datetime(2019, 5, 11, 3, 0, 0, 0)] = data
        self.assertEqual(
            len(
                util.bucketize(
                    junk,
                    start=datetime.datetime(2019, 5, 11),
                    end=datetime.datetime(2019, 5, 11, 3),
                )
            ),
            4,
        )
        self.assertEqual(
            len(
                util.bucketize(
                    junk,
                    start=datetime.datetime(2019, 5, 11),
                    end=datetime.datetime(2019, 5, 11, 3),
                    seconds=86400,
                )
            ),
            1,
        )

    def test_get_percentiles(self):
        """happy path"""
        perc = util.get_percentiles(
            "my_label",
            [1.111, 2.222, 3.333, 4.444, 5.555, 6.666, 7.777, 8.888, 9.999, 10],
        )
        self.assertEqual(len(perc), 7)
        self.assertEqual(perc[0], "my_label")
        self.assertEqual(perc[1], "10.00")
        self.assertEqual(perc[2], "10.00")
        self.assertEqual(perc[3], "8.89")
        self.assertEqual(perc[4], "6.67")
        self.assertEqual(perc[5], "3.33")
        self.assertEqual(perc[6], "1.11")

    def test_get_percentiles_reverse(self):
        """demonstrates the behavior of reverse=True"""
        perc = util.get_percentiles(
            "my_label",
            [1.111, 2.222, 3.333, 4.444, 5.555, 6.666, 7.777, 8.888, 9.999, 10],
            reverse=True,
        )
        self.assertEqual(len(perc), 7)
        self.assertEqual(perc[6], "my_label")
        self.assertEqual(perc[5], "10.00")
        self.assertEqual(perc[4], "10.00")
        self.assertEqual(perc[3], "8.89")
        self.assertEqual(perc[2], "6.67")
        self.assertEqual(perc[1], "3.33")
        self.assertEqual(perc[0], "1.11")

    def test_get_percentile_headers(self):
        """happy path and default"""
        perc = util.get_percentile_headers(
            label="stuff", names=("max", "p99", "p90", "p25", "min")
        )
        self.assertEqual(perc[0], "stuff")
        self.assertEqual(perc[1], "max")
        self.assertEqual(perc[2], "p99")
        self.assertEqual(perc[3], "p90")
        self.assertEqual(perc[4], "p25")
        self.assertEqual(perc[5], "min")
        perc = util.get_percentile_headers()
        self.assertEqual(perc[0], "")
        self.assertEqual(perc[1], "max")
        self.assertEqual(perc[2], "p99")
        self.assertEqual(perc[3], "p75")
        self.assertEqual(perc[4], "p50")
        self.assertEqual(perc[5], "p25")
        self.assertEqual(perc[6], "min")

    def test_write_underline(self):
        """happy path"""
        self.assertEqual(util.write_underline("1234"), "----")

    def test_write_underline_empty(self):
        """empty"""
        self.assertEqual(util.write_underline(""), "")

    def test_write_underline_single(self):
        """happy path"""
        self.assertEqual(util.write_underline("h"), "-")
