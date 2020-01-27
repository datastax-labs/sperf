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
from pysper.core.diag import reporter

#format helper tests
def test_format_table_stats():
    """NA, suffix and happy path tests"""
    line = reporter.format_table_stat(("127.0.0.1", "mykey.mytable", 13000))
    assert line == "13,000 (mykey.mytable 127.0.0.1)"
    line = reporter.format_table_stat(("127.0.0.1", "mykey.mytable", 13000), val_suffix="ms")
    assert line == "13,000 ms (mykey.mytable 127.0.0.1)"
    line = reporter.format_table_stat(None)
    assert line == "N/A"
    line = reporter.format_table_stat(())
    assert line == "N/A"
    line = reporter.format_table_stat(("mynode", "table"))
    assert line == "N/A"

def test_format_table_loc():
    """NA and happy path tests"""
    line = reporter.format_table_loc(("mytable", "mynode"))
    assert line == "mytable (mynode)"
    assert reporter.format_table_loc(()) == "N/A"
    assert reporter.format_table_loc(None) == "N/A"
    assert reporter.format_table_loc(("abc", )) == "N/A"

def test_format_partition_bytes():
    """NA and happy path tests"""
    line = reporter.format_partition_bytes((1, 2, 3, 3072), 3)
    assert line == "3.00 kb"
    line = reporter.format_partition_bytes(None, None)
    assert line == "N/A"
    line = reporter.format_partition_bytes((1, ), 1)
    assert line == "N/A"
    line = reporter.format_partition_bytes((1, ), None)
    assert line == "N/A"
