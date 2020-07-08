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

"""schema subcommand does a lightweight reporting of the clusters schema"""
from collections import namedtuple
from pysper import diag

Config = namedtuple('Config', 'files diag_dir')

def read(files):
    """reads the output of cqlsh schema..atm only
    reads the first file until we have diff support"""
    report = {
        "keyspaces": 0,
        "tables": 0,
        "2i": 0,
        "mvs": 0,
        "solr": 0,
        "solr_table": 0,
        "parsed_file": "Not Found",
        }
    if not files:
        return report
    schema_file = files[0]
    report["parsed_files"] = schema_file
    solr_tables = set()
    solr_indexes = []
    with diag.FileWithProgress(schema_file) as file_desc:
        for line in file_desc:
            if "CREATE TABLE" in line:
                report["tables"] += 1
                continue
            if "CREATE KEYSPACE" in line:
                report["keyspaces"] += 1
                continue
            if "CREATE INDEX" in line:
                report["2i"] += 1
                continue
            if "CREATE MATERIALIZED" in line:
                report["mvs"] += 1
                continue
            if "CREATE CUSTOM INDEX" in line:
                tokens = line.split(" ")
                table = tokens[5]
                #uses a set to accont for both formats
                solr_tables.add(table)
                solr_indexes.append(table)
    report["solr_table"] = len(solr_tables)
    report["solr"] = len(solr_indexes)
    return report

def generate_report(parsed_schema):
    """generate_report provides"""
    report = []
    report.append("")
    report.append("Schema read     : %s" % parsed_schema["parsed_file"])
    report.append("Keyspace Count  : %i" % parsed_schema["keyspaces"])
    report.append("Table Count     : %i" % parsed_schema["tables"])
    report.append("2i Count        : %i" % parsed_schema["2i"])
    report.append("MV Count        : %i" % parsed_schema["mvs"])
    report.append("Solr Index Count: %i" % parsed_schema["solr"])
    report.append("Solr Table Count: %i" % parsed_schema["solr_table"])
    return "\n".join(report)
