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

"""cfstats table stat parser"""
import re
from pysper import diag

def read_file(cfstat_file):
    """parses an individual file"""
    with diag.FileWithProgress(cfstat_file) as cfstat_file_desc:
        if cfstat_file_desc.error:
            raise IOError(cfstat_file_desc.error)
        parser = Parser()
        for line in cfstat_file_desc:
            parser.capture_line(line.rstrip('\n'))
        return parser.parsed

class Parser:
    """parses CFStats"""

    def __init__(self):
        self.parsed = {}
        self.current_table = ""
        self.current_keyspace = ""
        self.rules = [
            {"m": re.compile(r'Keyspace : (?P<keyspace_name>[^\n]+)'), \
                    "f": self._keyspace_match},
            {"m": re.compile(r'Keyspace: (?P<keyspace_name>[^\n]+)'), \
                    "f": self._keyspace_match},
            {"m": re.compile(r'\t\tTable: (?P<table_name>[^\n]+)'), \
                    "f": self._table_match},
            {"m": re.compile(r'\t\tTable \(index\): (?P<table_name>[^\n]+)'), \
                    "f": self._table_match},
            {"m": re.compile(r'\t\t(?P<key>.+): (?P<value>\d+\.\d+)'), \
                    "f": self._table_stat_float_match},
            {"m": re.compile(r'\t\t(?P<key>.+): (?P<value>NaN)'), \
                    "f": self._table_stat_float_match},
            {"m": re.compile(r'\t\t(?P<key>.+): (?P<value>\d+)'), \
                    "f": self._table_stat_int_match},
            {"m": re.compile(r'\t\t(?P<key>.+): (?P<value>\w+)'), \
                    "f": self._table_stat_regex},
            ]

    def _keyspace_match(self, match):
        self.current_keyspace = match.group('keyspace_name')
        self.parsed[self.current_keyspace] = {}

    def _table_match(self, match):
        self.current_table = match.group('table_name')
        self.parsed[self.current_keyspace][self.current_table] = {}

    def _table_stat_float_match(self, match):
        key = match.group('key')
        value = match.group('value')
        self.parsed[self.current_keyspace][self.current_table][key] = float(value)

    def _table_stat_int_match(self, match):
        key = match.group('key')
        value = match.group('value')
        self.parsed[self.current_keyspace][self.current_table][key] = int(value)

    def _table_stat_regex(self, match):
        key = match.group('key')
        value = match.group('value')
        self.parsed[self.current_keyspace][self.current_table][key] = value

    def capture_line(self, line):
        """matches keyspace, tables and their stats"""
        for rule in self.rules:
            match = rule["m"].match(line)
            if match:
                rule["f"](match)
                return
