"""validates the statuslogger args are in place"""
import argparse
import os
import pytest
from pysper.commands.core import statuslogger
from tests import current_dir

def test_args():
    """verify schema args are wired up correctly"""
    parser = argparse.ArgumentParser(prog="mine", description="entry point")
    subparsers = parser.add_subparsers()
    statuslogger.build(subparsers)
    args = parser.parse_args(["statuslogger", "-f", "foo", "-d", "diag", "-s", "stages", "-r", "report"])
    assert hasattr(args, "files")
    assert hasattr(args, "diag_dir")
    assert hasattr(args, "stages")
    assert hasattr(args, "reporter")

@pytest.mark.skipif(os.environ.get("TEST_LEVEL") == "fast", reason="fast mode")
def test_statuslogger_run():
    """validates we don't get a bad exit code"""
    parser = argparse.ArgumentParser(prog="mine", description="entry point")
    subparsers = parser.add_subparsers()
    statuslogger.build(subparsers)
    test_dir_1 = os.path.join(current_dir(__file__), '..', 'testdata', 'diag', 'statuslogger')
    args = parser.parse_args(["statuslogger", "-d", test_dir_1, "-r", "histogram"])
    statuslogger.run(args)
