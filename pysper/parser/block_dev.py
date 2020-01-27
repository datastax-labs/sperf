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

# pylint: disable=line-too-long
"""parses block dev reports"""
from pysper.parser.rules import capture, convert, default, rule

capture_line = rule(
    capture(
        #rw     8   512  4096          0    800166076416   /dev/sdb
        r'(?P<ro>[a-z]*) +(?P<ra>[0-9]*) +(?P<ssz>[0-9]*) +(?P<blk_sz>[0-9]*) *\s(?P<start_sec>[0-9]*) +(?P<size>[0-9]*) +(?P<device>.*)'
    ),
    convert(int, 'ra', 'ssz', 'blk_sz', 'blk_sz', 'start_sec', 'size'),
    default(event_product='unknown', event_category='unknown', event_type='unknown'))
