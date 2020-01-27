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

"""validates the sysbottle args are in place"""
import argparse
import os
from pysper.commands import sysbottle
from tests import current_dir

def test_args():
    """verify schema args are wired up correctly"""
    parser = argparse.ArgumentParser(prog="mine", description="entry point")
    subparsers = parser.add_subparsers()
    sysbottle.build(subparsers)
    args = parser.parse_args(["sysbottle", "abc.txt", "-c", "90", "-q", "1", "-d", "sda", "-i", "5", "-t", "3"])
    assert hasattr(args, "file")
    assert hasattr(args, "cpu")
    assert hasattr(args, "diskQ")
    assert hasattr(args, "disks")
    assert hasattr(args, "iowait")
    assert hasattr(args, "throughput")

def test_sysbottle_run():
    """validates we don't get a bad exit code"""
    parser = argparse.ArgumentParser(prog="mine", description="entry point")
    subparsers = parser.add_subparsers()
    sysbottle.build(subparsers)
    test_file_1 = os.path.join(current_dir(__file__), '..', 'testdata', 'iostat')
    args = parser.parse_args(["sysbottle", test_file_1, "-c", "90", "-q", "1", "-d", "sda", "-i", "5", "-t", "3"])
    sysbottle.run(args)
