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

"""validates the schema args are in place"""
import unittest
import argparse
import os
from pysper.commands.core import schema
from tests import get_current_dir


class TestSchemaCommands(unittest.TestCase):
    """test sperf core schema command args"""

    def test_args(self):
        """verify schema args are wired up correctly"""
        parser = argparse.ArgumentParser(prog="mine", description="entry point")
        subparsers = parser.add_subparsers()
        schema.build(subparsers)
        args = parser.parse_args(["schema", "-d", "hello", "-f", "abc"])
        self.assertTrue(hasattr(args, "diag_dir"))
        self.assertTrue(hasattr(args, "files"))

    def test_shema_run(self):
        """validates we don't get a bad exit code"""
        parser = argparse.ArgumentParser(prog="mine", description="entry point")
        subparsers = parser.add_subparsers()
        schema.build(subparsers)
        test_file_1 = os.path.join(
            get_current_dir(__file__), "testdata", "emtpy_file_1.log"
        )
        test_file_2 = os.path.join(
            get_current_dir(__file__), "testdata", "emtpy_file_2.log"
        )
        args = parser.parse_args(["schema", "-f", "%s,%s" % (test_file_1, test_file_2)])
        schema.run(args)
