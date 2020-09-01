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
"""tests reporter module"""
import unittest
from pysper.core.diag import reporter


class TestReporter(unittest.TestCase):
    """format helper tests"""

    def test_format_table_stats(self):
        """NA, suffix and happy path tests"""
        line = reporter.format_table_stat(("127.0.0.1", "mykey.mytable", 13000))
        self.assertEqual(line, "13,000 (mykey.mytable 127.0.0.1)")
        line = reporter.format_table_stat(
            ("127.0.0.1", "mykey.mytable", 13000), val_suffix="ms"
        )
        self.assertEqual(line, "13,000 ms (mykey.mytable 127.0.0.1)")
        line = reporter.format_table_stat(None)
        self.assertEqual(line, "N/A")
        line = reporter.format_table_stat(())
        self.assertEqual(line, "N/A")
        line = reporter.format_table_stat(("mynode", "table"))
        self.assertEqual(line, "N/A")

    def test_format_table_loc(self):
        """NA and happy path tests"""
        line = reporter.format_table_loc(("mytable", "mynode"))
        self.assertEqual(line, "mytable (mynode)")
        self.assertEqual(reporter.format_table_loc(()), "N/A")
        self.assertEqual(reporter.format_table_loc(None), "N/A")
        self.assertEqual(reporter.format_table_loc(("abc",)), "N/A")

    def test_format_partition_bytes(self):
        """NA and happy path tests"""
        line = reporter.format_partition_bytes((1, 2, 3, 3072), 3)
        self.assertEqual(line, "3.00 kb")
        line = reporter.format_partition_bytes(None, None)
        self.assertEqual(line, "N/A")
        line = reporter.format_partition_bytes((1,), 1)
        self.assertEqual(line, "N/A")
        line = reporter.format_partition_bytes((1,), None)
        self.assertEqual(line, "N/A")
