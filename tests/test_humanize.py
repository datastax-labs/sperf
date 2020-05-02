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
from pysper import humanize

def test_format_millis_999():
    """leaves millis unchanged"""
    assert humanize.format_millis(999) == "999.00 ms"

def test_format_millis_1000():
    """converts to 1 seconds"""
    assert humanize.format_millis(1000) == "1.00 second"

def test_format_millis_minutes():
    """converts to 1 minute"""
    assert humanize.format_millis(60000) == "1.00 minute"

def test_format_millis_hours():
    """converts to hours"""
    assert humanize.format_millis(60000 * 60) == "1.00 hour"
    assert humanize.format_millis(60000 * 60 * 23) == "23.00 hours"
    assert humanize.format_millis(60000 * 60 * 23.5) == "23.50 hours"

def test_format_millis_days():
    """converts to days"""
    assert humanize.format_millis(60000 * 60 * 24) == "1.00 day"
    assert humanize.format_millis(60000 * 60 * 36) == "1.50 days"

def test_format_millis_years():
    """converts to years after 365 days"""
    assert humanize.format_millis(60000 * 60 * 24 * 365) == "1.00 year"
    assert humanize.format_millis(60000 * 60 * 24 * 547.50) == "1.50 years"

def test_format_millis_years_with_separators():
    """to years after 999 years"""
    assert humanize.format_millis(60000 * 60 * 24 * 365 * 1000) == "1,000.00 years"
    assert humanize.format_millis(60000 * 60 * 24 * 365 * 1000 * 1.0005) == "1,000.50 years"

def test_format_seconds_59():
    """leaves seconds unchanged"""
    assert humanize.format_seconds(59) == "59 seconds"

def test_format_seconds_minutes():
    """converts to 1 minute"""
    assert humanize.format_seconds(60) == "1.00 minute"
    assert humanize.format_seconds(60.5) == "1.01 minutes"

def test_format_seconds_hours():
    """converts to hours"""
    assert humanize.format_seconds(60 * 60) == "1.00 hour"
    assert humanize.format_seconds(60.0 * 60.5) == "1.01 hours"

def test_format_seconds_days():
    """converts to days"""
    assert humanize.format_seconds(60 * 60 * 24) == "1.00 day"
    assert humanize.format_seconds(60.0 * 60.0 * 24.0) == "1.00 day"

def test_format_seconds_years():
    """converts to years after 365 days"""
    assert humanize.format_seconds(60 * 60 * 24 * 365) == "1.00 year"
    assert humanize.format_seconds(60 * 60 * 24 * 367.7) == "1.01 years"
    #test for signficance
    assert humanize.format_seconds(60 * 60 * 24 * 365.1) == "1.00 year"

def test_format_seconds_years_with_separators():
    """to years after 999 years"""
    assert humanize.format_seconds(60 * 60 * 24 * 365 * 1000) == "1,000.00 years"
    assert humanize.format_seconds(60 * 60 * 24 * 365 * 1000.9) == "1,000.90 years"

def test_format_bytes_999():
    """leave alone"""
    assert humanize.format_bytes(999) == "999 bytes"

def test_format_bytes_999point5():
    """round"""
    assert humanize.format_bytes(999.4) == "999 bytes"
    assert humanize.format_bytes(999.5) == "1,000 bytes"

def test_format_bytes_1023():
    """add separator"""
    assert humanize.format_bytes(1023) == "1,023 bytes"
    assert humanize.format_bytes(1023.4) == "1,023 bytes"

def test_format_bytes_1024():
    """convert to k"""
    assert humanize.format_bytes(1024) == "1.00 kb"
    assert humanize.format_bytes(1024.4) == "1.00 kb"

def test_format_bytes_mb():
    """convert to mb"""
    assert humanize.format_bytes(1024 ** 2) == "1.00 mb"
    assert humanize.format_bytes(1024.4 ** 2) == "1.00 mb"

def test_format_bytes_1000_mb():
    """convert to mb and add separator"""
    assert humanize.format_bytes((1024 ** 2) * 1000) == "1,000.00 mb"
    assert humanize.format_bytes((1024 ** 2) * 1000.4) == "1,000.40 mb"

def test_format_bytes_gb():
    """convert to gb"""
    assert humanize.format_bytes(1024 ** 3) == "1.00 gb"
    assert humanize.format_bytes((1024 ** 3) * 1.04) == "1.04 gb"

def test_format_bytes_1000_gb():
    """convert to gb and add separtor"""
    assert humanize.format_bytes((1024 ** 3) * 1000) == "1,000.00 gb"
    assert humanize.format_bytes((1024 ** 3) * 1000.4) == "1,000.40 gb"

def test_format_bytes_tb():
    """convert to tb"""
    assert humanize.format_bytes(1024 ** 4) == "1.00 tb"
    assert humanize.format_bytes((1024 ** 4) * 1.04) == "1.04 tb"

def test_format_bytes_1000_tb():
    """convert to tb and add separator"""
    assert humanize.format_bytes((1024 ** 4) * 1000) == "1,000.00 tb"
    assert humanize.format_bytes((1024 ** 4) * 1000.04) == "1,000.04 tb"

def test_format_bytes_1000_pb():
    """convert to tb and add separator"""
    assert humanize.format_bytes((1024 ** 5) * 1000) == "1,000.00 pb"
    assert humanize.format_bytes((1024 ** 5) * 1000.04) == "1,000.04 pb"

def test_format_bytes_none():
    """undefined input"""
    assert humanize.format_bytes(None) == "Not available"


def test_format_num():
    """test various numbers with separator"""
    assert humanize.format_num(999) == "999"
    assert humanize.format_num(1000) == "1,000"
    assert humanize.format_num(1000000) == "1,000,000"
    assert humanize.format_num(999.4) == "999"
    assert humanize.format_num(1000.4) == "1,000"
    assert humanize.format_num(1000000.4) == "1,000,000"

def test_format_num_float():
    """test various numbers with separator"""
    assert humanize.format_num_float(999.52) == "999.52"
    assert humanize.format_num_float(1000.52) == "1,000.52"
    assert humanize.format_num_float(1000000.52) == "1,000,000.52"
    assert humanize.format_num_float(999) == "999.00"
    assert humanize.format_num_float(1000) == "1,000.00"
    assert humanize.format_num_float(1000000) == "1,000,000.00"

def test_pad_table_with_min_width_and_padding():
    """tests table padding with various paddings and min width"""
    data = [["1", "2", "3"]]
    data.append(["2", "2222", "33333"])
    humanize.pad_table(data, min_width=2, extra_pad=1)
    #first column
    assert data[0][0] == "1 "
    assert data[1][0] == "2 "

    #second column
    assert data[0][1] == "2    "
    assert data[1][1] == "2222 "

    #third column
    assert data[0][2] == "3     "
    assert data[1][2] == "33333 "

def test_pad_table():
    """padding defaults"""
    data = [["1", "2", "3"]]
    data.append(["2", "2222", "33333"])
    humanize.pad_table(data)
    #first column
    assert data[0][0] == "1"
    assert data[1][0] == "2"

    #second column
    assert data[0][1] == "2   "
    assert data[1][1] == "2222"

    #third column
    assert data[0][2] == "3    "
    assert data[1][2] == "33333"

def test_pad_table_headers():
    """demonstrates the use of irrelagular data added to table that is ignored"""
    data = [["my header"]]
    data.append(["1", "2", "3"])
    data.append(["2", "2222", "33333"])
    humanize.pad_table(data, min_width=2, extra_pad=1)
    #header
    assert data[0][0] == "my header"

    #column are unbroken
    assert data[1][0] == "1 "
    assert data[2][0] == "2 "
    assert data[1][1] == "2    "
    assert data[2][1] == "2222 "
    assert data[1][2] == "3     "
    assert data[2][2] == "33333 "

def test_to_bytes():
    """happy path test of all units"""
    assert humanize.to_bytes(2, "bytes") == 2
    assert humanize.to_bytes(2, "kb") == 2048
    assert humanize.to_bytes(2, "mb") == 2097152
    assert humanize.to_bytes(2, "gb") == 2147483648
    assert humanize.to_bytes(2, "tb") == 2199023255552
    assert humanize.to_bytes(2, "pb") == 2251799813685248
    assert humanize.to_bytes(2, "ByTes") == 2
    assert humanize.to_bytes(2, "KB") == 2048
    assert humanize.to_bytes(2, "mB") == 2097152
    assert humanize.to_bytes(2, "GB") == 2147483648
    assert humanize.to_bytes(2, "tB") == 2199023255552
    assert humanize.to_bytes(2, "Pb") == 2251799813685248


def test_format_list_with_no_elements():
    """zero case"""
    assert humanize.format_list([]) == ""

def test_format_list_with_1_element():
    """should not mess with single element output"""
    assert humanize.format_list(["1"]) == "1"

def test_format_list_with_2_elements():
    """should use separator"""
    assert humanize.format_list(["1", "2"]) == "1, 2"

def test_format_list_with_many_elements():
    """should wrap next line"""
    data = ["1", "2", "3", "4", "5", "6", "7"]
    output = humanize.format_list(data)
    assert output == "1, 2, 3\n4, 5, 6\n7"
