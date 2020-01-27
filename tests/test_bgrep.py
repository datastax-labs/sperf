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
from pysper.bgrep import BucketGrep
from tests import current_dir

def test_bgrep():
    """validates bgrep matches every line"""
    b = BucketGrep('main', files=[os.path.join(current_dir(__file__), 'testdata', 'simple.log')])
    b.analyze()
    assert len(b.matches) == 2

def test_bgrep_when_statuslogger_lines_present():
    """statuslogger matching maybe breaking bgrep"""
    b = BucketGrep('RANGE_SLICE messages were dropped', \
            files=[os.path.join(current_dir(__file__), 'testdata', 'statusloggernew_debug.log')])
    b.analyze()
    assert len(b.matches) == 1

def test_no_matches():
    """should match no rows"""
    b = BucketGrep('this should never match anything', \
                   files=[os.path.join(current_dir(__file__), 'testdata', 'statusloggernew_debug.log')])
    b.analyze()
    assert not b.matches

def test_nodate():
    """validates bgrep matches lines without a date"""
    b = BucketGrep('.*No such file or directory.*', \
            files=[os.path.join(current_dir(__file__), 'testdata', 'traceback.log')])
    b.analyze()
    assert len(b.matches) == 1
