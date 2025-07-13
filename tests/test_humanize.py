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
"""test the various numbers and their output when using humanize"""
import unittest
from pysper import humanize


class TestHumanizeTime(unittest.TestCase):
    """tests time humanization"""

    def test_format_millis_999(self):
        """leaves millis unchanged"""
        self.assertEqual(humanize.format_millis(999), "999.00 ms")

    def test_format_millis_1000(self):
        """converts to 1 seconds"""
        self.assertEqual(humanize.format_millis(1000), "1.00 second")

    def test_format_millis_minutes(self):
        """converts to 1 minute"""
        self.assertEqual(humanize.format_millis(60000), "1.00 minute")

    def test_format_millis_hours(self):
        """converts to hours"""
        self.assertEqual(humanize.format_millis(60000 * 60), "1.00 hour")
        self.assertEqual(humanize.format_millis(60000 * 60 * 23), "23.00 hours")
        self.assertEqual(humanize.format_millis(60000 * 60 * 23.5), "23.50 hours")

    def test_format_millis_days(self):
        """converts to days"""
        self.assertEqual(humanize.format_millis(60000 * 60 * 24), "1.00 day")
        self.assertEqual(humanize.format_millis(60000 * 60 * 36), "1.50 days")

    def test_format_millis_years(self):
        """converts to years after 365 days"""
        self.assertEqual(humanize.format_millis(60000 * 60 * 24 * 365), "1.00 year")
        self.assertEqual(humanize.format_millis(60000 * 60 * 24 * 547.50), "1.50 years")

    def test_format_millis_years_with_separators(self):
        """to years after 999 years"""
        self.assertEqual(
            humanize.format_millis(60000 * 60 * 24 * 365 * 1000), "1,000.00 years"
        )
        self.assertEqual(
            humanize.format_millis(60000 * 60 * 24 * 365 * 1000 * 1.0005),
            "1,000.50 years",
        )

    def test_format_seconds_59(self):
        """leaves seconds unchanged"""
        self.assertEqual(humanize.format_seconds(59), "59 seconds")

    def test_format_seconds_minutes(self):
        """converts to 1 minute"""
        self.assertEqual(humanize.format_seconds(60), "1.00 minute")
        self.assertEqual(humanize.format_seconds(60.5), "1.01 minutes")

    def test_format_seconds_hours(self):
        """converts to hours"""
        self.assertEqual(humanize.format_seconds(60 * 60), "1.00 hour")
        self.assertEqual(humanize.format_seconds(60.0 * 60.5), "1.01 hours")

    def test_format_seconds_days(self):
        """converts to days"""
        self.assertEqual(humanize.format_seconds(60 * 60 * 24), "1.00 day")
        self.assertEqual(humanize.format_seconds(60.0 * 60.0 * 24.0), "1.00 day")

    def test_format_seconds_years(self):
        """converts to years after 365 days"""
        self.assertEqual(humanize.format_seconds(60 * 60 * 24 * 365), "1.00 year")
        self.assertEqual(humanize.format_seconds(60 * 60 * 24 * 367.7), "1.01 years")
        # test for signficance
        self.assertEqual(humanize.format_seconds(60 * 60 * 24 * 365.1), "1.00 year")

    def test_format_seconds_years_with_separators(self):
        """to years after 999 years"""
        self.assertEqual(
            humanize.format_seconds(60 * 60 * 24 * 365 * 1000), "1,000.00 years"
        )
        self.assertEqual(
            humanize.format_seconds(60 * 60 * 24 * 365 * 1000.9), "1,000.90 years"
        )


class TestHumanizeBytes(unittest.TestCase):
    """tests humanization of data"""

    def test_format_bytes_999(self):
        """leave alone"""
        self.assertEqual(humanize.format_bytes(999), "999 bytes")

    def test_format_bytes_999point5(self):
        """round"""
        self.assertEqual(humanize.format_bytes(999.4), "999 bytes")
        self.assertEqual(humanize.format_bytes(999.5), "1,000 bytes")

    def test_format_bytes_1023(self):
        """add separator"""
        self.assertEqual(humanize.format_bytes(1023), "1,023 bytes")
        self.assertEqual(humanize.format_bytes(1023.4), "1,023 bytes")

    def test_format_bytes_1024(self):
        """convert to k"""
        self.assertEqual(humanize.format_bytes(1024), "1.00 kb")
        self.assertEqual(humanize.format_bytes(1024.4), "1.00 kb")

    def test_format_bytes_mb(self):
        """convert to mb"""
        self.assertEqual(humanize.format_bytes(1024**2), "1.00 mb")
        self.assertEqual(humanize.format_bytes(1024.4**2), "1.00 mb")

    def test_format_bytes_1000_mb(self):
        """convert to mb and add separator"""
        self.assertEqual(humanize.format_bytes((1024**2) * 1000), "1,000.00 mb")
        self.assertEqual(humanize.format_bytes((1024**2) * 1000.4), "1,000.40 mb")

    def test_format_bytes_gb(self):
        """convert to gb"""
        self.assertEqual(humanize.format_bytes(1024**3), "1.00 gb")
        self.assertEqual(humanize.format_bytes((1024**3) * 1.04), "1.04 gb")

    def test_format_bytes_1000_gb(self):
        """convert to gb and add separtor"""
        self.assertEqual(humanize.format_bytes((1024**3) * 1000), "1,000.00 gb")
        self.assertEqual(humanize.format_bytes((1024**3) * 1000.4), "1,000.40 gb")

    def test_format_bytes_tb(self):
        """convert to tb"""
        self.assertEqual(humanize.format_bytes(1024**4), "1.00 tb")
        self.assertEqual(humanize.format_bytes((1024**4) * 1.04), "1.04 tb")

    def test_format_bytes_1000_tb(self):
        """convert to tb and add separator"""
        self.assertEqual(humanize.format_bytes((1024**4) * 1000), "1,000.00 tb")
        self.assertEqual(humanize.format_bytes((1024**4) * 1000.04), "1,000.04 tb")

    def test_format_bytes_1000_pb(self):
        """convert to tb and add separator"""
        self.assertEqual(humanize.format_bytes((1024**5) * 1000), "1,000.00 pb")
        self.assertEqual(humanize.format_bytes((1024**5) * 1000.04), "1,000.04 pb")

    def test_format_bytes_none(self):
        """undefined input"""
        self.assertEqual(humanize.format_bytes(None), "Not available")


class TestFormatRawNumbers(unittest.TestCase):
    """validates the number is formatted for the US market"""

    def test_format_num(self):
        """test various numbers with separator"""
        self.assertEqual(humanize.format_num(999), "999")
        self.assertEqual(humanize.format_num(1000), "1,000")
        self.assertEqual(humanize.format_num(1000000), "1,000,000")
        self.assertEqual(humanize.format_num(999.4), "999")
        self.assertEqual(humanize.format_num(1000.4), "1,000")
        self.assertEqual(humanize.format_num(1000000.4), "1,000,000")

    def test_format_num_float(self):
        """test various numbers with separator"""
        self.assertEqual(humanize.format_num_float(999.52), "999.52")
        self.assertEqual(humanize.format_num_float(1000.52), "1,000.52")
        self.assertEqual(humanize.format_num_float(1000000.52), "1,000,000.52")
        self.assertEqual(humanize.format_num_float(999), "999.00")
        self.assertEqual(humanize.format_num_float(1000), "1,000.00")
        self.assertEqual(humanize.format_num_float(1000000), "1,000,000.00")


class TestTablePadding(unittest.TestCase):
    """tests the formatting of tables when padding is used"""

    def test_find_last_valid_col(self):
        """tests finding the last non empty col in a row"""
        self.assertEqual(humanize.find_last_valid_col(["a", "b", "c"]), 2)
        self.assertEqual(humanize.find_last_valid_col(["a", "b", ""]), 1)
        self.assertEqual(humanize.find_last_valid_col([""]), 0)
        self.assertEqual(humanize.find_last_valid_col([]), -1)

    def test_pad_table_should_always_trim_last_col(self):
        """verifies when the last col is missing in a row the next column is padded down"""
        data = [["1", "2", ""]]
        data.append(["2", "2222", "33333"])
        humanize.pad_table(data, min_width=2, extra_pad=1)
        # first column
        self.assertEqual(data[0][0], "1 ")
        self.assertEqual(data[1][0], "2 ")

        # second column
        self.assertEqual(data[0][1], "2")
        self.assertEqual(data[1][1], "2222 ")

        # last column does not pad
        self.assertEqual(data[0][2], "")
        self.assertEqual(data[1][2], "33333")

    def test_pad_table_with_min_width_and_padding(self):
        """tests table padding with various paddings and min width"""
        data = [["1", "2", "3"]]
        data.append(["2", "2222", "33333"])
        humanize.pad_table(data, min_width=2, extra_pad=1)
        # first column
        self.assertEqual(data[0][0], "1 ")
        self.assertEqual(data[1][0], "2 ")

        # second column
        self.assertEqual(data[0][1], "2    ")
        self.assertEqual(data[1][1], "2222 ")

        # last column does not pad
        self.assertEqual(data[0][2], "3")
        self.assertEqual(data[1][2], "33333")

    def test_pad_table(self):
        """padding defaults"""
        data = [["1", "2", "3"]]
        data.append(["2", "2222", "33333"])
        humanize.pad_table(data)
        # first column
        self.assertEqual(data[0][0], "1")
        self.assertEqual(data[1][0], "2")

        # second column
        self.assertEqual(data[0][1], "2   ")
        self.assertEqual(data[1][1], "2222")

        # last column does not pad
        self.assertEqual(data[0][2], "3")
        self.assertEqual(data[1][2], "33333")

    def test_pad_table_headers(self):
        """demonstrates the use of irrelagular data added to table that is ignored"""
        data = [["my header"]]
        data.append(["1", "2", "3"])
        data.append(["2", "2222", "33333"])
        humanize.pad_table(data, min_width=2, extra_pad=1)
        # header
        self.assertEqual(data[0][0], "my header")

        # column are unbroken
        self.assertEqual(data[1][0], "1 ")
        self.assertEqual(data[2][0], "2 ")
        self.assertEqual(data[1][1], "2    ")
        self.assertEqual(data[2][1], "2222 ")
        # as always last column does not pad
        self.assertEqual(data[1][2], "3")
        self.assertEqual(data[2][2], "33333")


class TestFromHumanToRawBytes(unittest.TestCase):
    """validates the behavior of to_bytes method"""

    def test_to_bytes(self):
        """happy path test of all units"""
        self.assertEqual(humanize.to_bytes(2, "bytes"), 2)
        self.assertEqual(humanize.to_bytes(2, "kb"), 2048)
        self.assertEqual(humanize.to_bytes(2, "mb"), 2097152)
        self.assertEqual(humanize.to_bytes(2, "gb"), 2147483648)
        self.assertEqual(humanize.to_bytes(2, "tb"), 2199023255552)
        self.assertEqual(humanize.to_bytes(2, "pb"), 2251799813685248)
        self.assertEqual(humanize.to_bytes(2, "ByTes"), 2)
        self.assertEqual(humanize.to_bytes(2, "KB"), 2048)
        self.assertEqual(humanize.to_bytes(2, "mB"), 2097152)
        self.assertEqual(humanize.to_bytes(2, "GB"), 2147483648)
        self.assertEqual(humanize.to_bytes(2, "tB"), 2199023255552)
        self.assertEqual(humanize.to_bytes(2, "Pb"), 2251799813685248)


class TestHumanizeFormatList(unittest.TestCase):
    """validates the behavior of the format_list method"""

    def test_format_list_with_no_elements(self):
        """zero case"""
        self.assertEqual(humanize.format_list([]), "")

    def test_format_list_with_1_element(self):
        """should not mess with single element output"""
        self.assertEqual(humanize.format_list(["1"]), "1")

    def test_format_list_with_2_elements(self):
        """should use separator"""
        self.assertEqual(humanize.format_list(["1", "2"]), "1, 2")

    def test_format_list_with_many_elements(self):
        """should wrap next line"""
        data = ["1", "2", "3", "4", "5", "6", "7"]
        output = humanize.format_list(data)
        self.assertEqual(output, "1, 2, 3\n4, 5, 6\n7")
