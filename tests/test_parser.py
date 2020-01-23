"""validates the basic logline function works correctly"""
import os
from pysper.parser.rules import capture, default, rule
from pysper import parser
from tests import current_dir

capture_line = rule(
    capture(
        r'(?P<level>[A-Z]+)'
    ),
    default(event_product='unknown', event_category='unknown', event_type='unknown'))

def test_parses_all_matches():
    """validates the parser returns every line"""
    rows = []
    with open(os.path.join(current_dir(__file__), "testdata", "simple.log")) as test_file:
        events = parser.read_log(test_file, capture_line)
        rows = list(events)
    assert len(rows) == 2
    line1 = "WARN"
    assert rows[0]['level'] == line1
    line2 = "ERROR"
    assert rows[1]['level'] == line2
