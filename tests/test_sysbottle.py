""" Tests the sysbottle module """
import os
from datetime import datetime
from pysper.sysbottle import SysbottleReport, IOStatParser

def test_sysbottle_analyze():
    """ test sysbottle report """
    iostat = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testdata', 'iostat')

    report = SysbottleReport(iostat)
    report.analyze()

    assert report.analyzed
    assert report.count == 10
    assert len(report.devices) == 1
    assert len(report.cpu_stats['total']) == 10

    report.print_report()

def test_date_format():
    """makes sure parsing works with all formats"""
    #pylint: disable=protected-access
    real_time = datetime.strptime("2011-09-16 19:01:10", "%Y-%m-%d %H:%M:%S")
    parser = IOStatParser()
    eu_format = "16/09/11 19:01:10"
    parser._parse_date(eu_format)
    assert parser.iostat['date'] == real_time
    sky_format = "09/16/11 19:01:10"
    parser._parse_date(sky_format)
    assert parser.iostat['date'] == real_time
    us_format = "09/16/2011 07:01:10 PM"
    parser._parse_date(us_format)
    assert parser.iostat['date'] == real_time
