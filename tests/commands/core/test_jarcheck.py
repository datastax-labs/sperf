"""validates the jarcheck args are in place"""
import argparse
import os
import pytest
from pysper.commands.core import jarcheck
from tests import current_dir

def test_args():
    """verify jarcheck args are wired up correctly"""
    parser = argparse.ArgumentParser(prog="mine", description="entry point")
    subparsers = parser.add_subparsers()
    jarcheck.build(subparsers)
    args = parser.parse_args(["jarcheck", "-d", "hello", "-f", "abc", "-o"])
    assert hasattr(args, "diag_dir")
    assert hasattr(args, "diff_only")
    assert hasattr(args, "files")

def test_jarcheck_run():
    """validates we raise FNFE if nonexistent files are passed"""
    parser = argparse.ArgumentParser(prog="mine", description="entry point")
    subparsers = parser.add_subparsers()
    jarcheck.build(subparsers)
    test_file_1 = os.path.join(current_dir(__file__), "testdata", "emtpy_file_1.log")
    test_file_2 = os.path.join(current_dir(__file__), "testdata", "emtpy_file_2.log")
    args = parser.parse_args(["jarcheck", "-f", "%s,%s" % (test_file_1, test_file_2), "-o"])
    with pytest.raises(FileNotFoundError):
        jarcheck.run(args)
