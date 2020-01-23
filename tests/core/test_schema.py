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
        })
    assert repr(report) == repr("""
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
