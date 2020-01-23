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
