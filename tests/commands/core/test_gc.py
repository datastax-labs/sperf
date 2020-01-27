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

"""validates the gc args are in place"""
import argparse
import os
import pytest
from pysper.commands.core import gc

def test_args():
    """verify gc args are wired up correctly"""
    parser = argparse.ArgumentParser(prog="mine", description="entry point")
    subparsers = parser.add_subparsers()
    gc.build(subparsers)
    args = parser.parse_args(["gc", "-f", "foo", "-d", "diag", "-i", "3600", "-r", "report"])
    assert hasattr(args, "files")
    assert hasattr(args, "diag_dir")
    assert hasattr(args, "interval")
    assert hasattr(args, "reporter")

@pytest.mark.skipif(os.environ.get("TEST_LEVEL") == "fast", reason="fast mode")
def test_gc_run():
    """validates we don't get a bad exit code"""
    parser = argparse.ArgumentParser(prog="mine", description="entry point")
    subparsers = parser.add_subparsers()
    gc.build(subparsers)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir_1 = current_dir + "/../testdata/diag/statuslogger"
    args = parser.parse_args(["gc", "-d", test_dir_1, "-r", "nodes"])
    gc.run(args)
