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

"""tests for the base sperf command"""
import unittest
import os
import types
from pysper import VERSION
from pysper.commands.core import schema
from tests import current_dir, steal_output


class TestSchema(unittest.TestCase):
    """validate the schema module"""

    def test_sperf(self):
        """integration test, this is not the best test and only verifies no change in calculations
        as changes in the codebase occur."""
        args = types.SimpleNamespace()
        args.diag_dir = os.path.join(
            current_dir(__file__), "testdata", "diag", "DSE_CLUSTER"
        )
        args.files = []

        def run():
            schema.run(args)

        output = steal_output(run)
        # reads better with the extra newline
        header = "sperf core schema version: %s" % (VERSION)
        self.assertEqual(
            output,
            header
            + """


Schema read     : %s
Keyspace Count  : 15
Table Count     : 61
2i Count        : 1
MV Count        : 0
UDT Count       : 6
Solr Index Count: 1
Solr Table Count: 1"""
            % os.path.join(
                current_dir(__file__),
                "testdata",
                "diag",
                "DSE_CLUSTER",
                "nodes",
                "10.101.33.205",
                "driver",
                "schema",
            ),
        )

    def test_sperf_68(self):
        """integration test, this is not the best test and only verifies no change in calculations
        as changes in the codebase occur."""
        args = types.SimpleNamespace()
        args.diag_dir = os.path.join(current_dir(__file__), "testdata", "dse68")
        args.files = []

        def run():
            schema.run(args)

        output = steal_output(run)
        # reads better with the extra newline
        header = "sperf core schema version: %s" % (VERSION)
        self.assertEqual(
            output,
            header
            + """


Schema read     : %s
Keyspace Count  : 13
Table Count     : 36
2i Count        : 0
MV Count        : 0
UDT Count       : 6
Solr Index Count: 0
Solr Table Count: 0"""
            % os.path.join(
                current_dir(__file__),
                "testdata",
                "dse68",
                "nodes",
                "172.17.0.2",
                "driver",
                "schema",
            ),
        )
