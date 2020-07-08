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

"""tests the schema module"""
import os
from pysper.core import schema
from tests import test_dse_tarball

def test_schema_report():
    """test generate report"""
    report = schema.generate_report({
        "keyspaces": 16,
        "tables": 124,
        "2i": 6,
        "mvs": 10,
        "solr": 31,
        "solr_table": 11,
        "parsed_file": "test",
        })
    assert repr(report) == repr("""
Schema read     : test
Keyspace Count  : 16
Table Count     : 124
2i Count        : 6
MV Count        : 10
Solr Index Count: 31
Solr Table Count: 11""")

def test_read_schema():
    """test the read schema report"""
    test_file = os.path.join(test_dse_tarball(), "nodes", "10.101.33.205", "driver", "schema")
    files = [test_file]
    parsed = schema.read(files)
    assert parsed["keyspaces"] == 15
    assert parsed["tables"] == 61
    assert parsed["2i"] == 1
    assert parsed["mvs"] == 0
    assert parsed["solr"] == 1
    assert parsed["solr_table"] == 1
