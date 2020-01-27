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
import argparse
import os
from pysper.commands.core import schema
from tests import current_dir

def test_args():
    """verify schema args are wired up correctly"""
    parser = argparse.ArgumentParser(prog="mine", description="entry point")
    subparsers = parser.add_subparsers()
    schema.build(subparsers)
    args = parser.parse_args(["schema", "-d", "hello", "-f", "abc"])
    assert hasattr(args, "diag_dir")
    assert hasattr(args, "files")

def test_shema_run():
    """validates we don't get a bad exit code"""
    parser = argparse.ArgumentParser(prog="mine", description="entry point")
    subparsers = parser.add_subparsers()
    schema.build(subparsers)
    test_file_1 = os.path.join(current_dir(__file__), "testdata", "emtpy_file_1.log")
    test_file_2 = os.path.join(current_dir(__file__), "testdata", "emtpy_file_2.log")
    args = parser.parse_args(["schema", "-f", "%s,%s" % (test_file_1, test_file_2)])
    schema.run(args)
