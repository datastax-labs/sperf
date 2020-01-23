"""top level tests package with helper methods"""
import os
from io import StringIO
import contextlib
import logging

LOGGER = logging.getLogger(__name__)

def test_dir():
    """returns the test directory"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata")

def test_dse_tarball():
    """default dse tarball to use for all tests"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata", "diag", "DSE_CLUSTER")

def test_cassandra_tarball():
    """default cassandra tarball of a given version to use for all tests"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata", "diag", "cassandra")

def current_dir(current_file):
    """takes the current_file and finds the directory where it is located"""
    return os.path.dirname(os.path.abspath(current_file))

def steal_output(func, *args, **kwargs):
    """captures stdout from a function"""
    temp_stdout = StringIO()
    with contextlib.redirect_stdout(temp_stdout):
        func(*args, **kwargs)
    output = temp_stdout.getvalue().strip()
    return output

def assert_in_output(expected_text, text):
    """asserts the expected_text is in the text, if not
    present will provide an output of the text field so it'll be easier to debug"""
    try:
        assert expected_text in text
    except Exception as ex:
        LOGGER.info(text)
        LOGGER.error(ex)
        raise
