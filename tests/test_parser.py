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
