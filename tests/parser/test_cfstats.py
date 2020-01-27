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

"""test the cfstats module"""
import os
import math
import pytest
from pysper.parser import cfstats
from tests import test_dse_tarball 

def test_read_cfstats_file():
    """validate multiple keyspaces and tables are found as well as float and
    int parsing with and without ms suffix"""
    parsed = cfstats.read_file(os.path.join(test_dse_tarball(), 'nodes', '10.101.33.205', 'nodetool', 'cfstats'))
    assert parsed
    key = parsed.get('my_solr')
    assert key
    table = key.get('my_table')
    assert table
    assert table.get('SSTable count') == 1
    assert table.get('Local write count') == 4114233
    assert table.get('Local read count') == 4953524
    assert ("%.2f") % table.get('Local read latency') == "0.26"
    assert ("%.2f") % table.get('Local write latency') == "0.40"
    ##finds other keyspaces too
    assert parsed['system'].get('local')
    assert parsed['system']['local'].get('SSTable count') == 2

def test_spaceless_keyspace_line_cfstats_format():
    """keyspace has no space before :"""
    parser = cfstats.Parser()
    lines= [
        "Keyspace: dse_analytics",
		"\t\tTable: alwayson_sql_cache_table",
		"\t\tSSTable count: 0",
        "",
		"\t\tTable: alwayson_sql_info",
		"\t\tSSTable count: 3",
        "",
        "----------------",
        "Keyspace: abc",
        "\t\tTable: fancy_name",
        "\t\tSSTable count: 10",
    ]
    for line in lines:
        parser.capture_line(line+"\n")
    import pprint
    pp = pprint.PrettyPrinter()
    pp.pprint(parser.parsed)
    assert parser.parsed['abc']['fancy_name']['SSTable count'] == 10

def test_parse_cfstats_unable_to_parse_index():
    """regression test against problems parsing table name with ()"""
    parser = cfstats.Parser()
    lines= [
        "Keyspace : dse_analytics",
		"\t\tTable: alwayson_sql_cache_table",
		"\t\tSSTable count: 0",
        "",
		"\t\tTable: alwayson_sql_info",
		"\t\tSSTable count: 3",
        "",
        "----------------",
        "Keyspace : abc",
        "\t\tTable (index): summary.fancy_accountvalue.fancy_accountvalue_summary_class_name_idx",
        "\t\tSSTable count: 10",
    ]
    for line in lines:
        parser.capture_line(line+"\n")
    import pprint
    pp = pprint.PrettyPrinter()
    pp.pprint(parser.parsed)
    assert parser.parsed['abc']['summary.fancy_accountvalue.fancy_accountvalue_summary_class_name_idx']['SSTable count'] == 10

def test_parse_cfstats():
    """happy path"""
    parser = cfstats.Parser()
    lines = [
        "Total number of tables: 44",
        "----------------",
        "Keyspace : keyspace1",
        "\tRead Count: 0",
        "\tRead Latency: NaN ms",
        "\tWrite Count: 330000",
        "\tWrite Latency: 0.04408098181818182 ms",
        "\tPending Flushes: 0",
        "\t\tTable: counter1",
        "\t\tSSTable count: 20",
        "",
        "\t\tTable: standard1",
        "\t\tSSTable count: 2",
        "----------------",
        "Keyspace : keyspace2",
        "\tRead Count: 0",
        "\tRead Latency: NaN ms",
        "\tWrite Count: 330000",
        "\tWrite Latency: 0.04408098181818182 ms",
        "\tPending Flushes: 0",
        "\t\tTable: counter2",
        "\t\tSSTable count: 10",
        "\t\tLocal read latency: NaN ms",
        "\t\tLocal write latency: 0.050 ms",
        "\t\tMaximum tombstones per slice (last five minutes): 5",
        ]
    for line in lines:
        parser.capture_line(line)
    parsed = parser.parsed
    assert len(parsed) == 2
    assert parsed['keyspace1']["counter1"]["SSTable count"] == 20
    assert parsed['keyspace1']["standard1"]["SSTable count"] == 2
    assert parsed['keyspace2']["counter2"]["SSTable count"] == 10
    assert parsed['keyspace2']["counter2"]["Maximum tombstones per slice (last five minutes)"] == 5
    assert math.isnan(parsed['keyspace2']["counter2"]["Local read latency"])
    assert "%.3f" % parsed['keyspace2']["counter2"]["Local write latency"] == "0.050"
