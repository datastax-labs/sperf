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
