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
