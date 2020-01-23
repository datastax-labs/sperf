"""tests the dates.py module"""
from pysper import dates

def test_european_dates():
    """day before month"""
    parser = dates.LogDateFormatParser()
    parsed = parser.parse_timestamp("2018-23-10 15:50:01.123")
    assert parsed.strftime(parser.cassandra_log_format) == "2018-10-23 15:50:01,123000"

def test_us_dates():
    """month before day"""
    parser = dates.LogDateFormatParser()
    parsed = parser.parse_timestamp("2018-10-23 15:50:01.123")
    assert parsed.strftime(parser.cassandra_log_format) == "2018-10-23 15:50:01,123000"

def test_back_to_back():
    """since this flips a "mode" we should test if combinations work"""
    parser = dates.LogDateFormatParser()
    parsed = parser.parse_timestamp("2018-10-23 15:50:01.123")
    assert parsed.strftime(parser.cassandra_log_format) == "2018-10-23 15:50:01,123000"
    parsed = parser.parse_timestamp("2018-23-10 15:50:01.123")
    assert parsed.strftime(parser.cassandra_log_format) == "2018-10-23 15:50:01,123000"
    parsed = parser.parse_timestamp("2018-23-10 15:50:01.123")
    assert parsed.strftime(parser.cassandra_log_format) == "2018-10-23 15:50:01,123000"
    parsed = parser.parse_timestamp("2018-10-23 15:50:01.123")
    assert parsed.strftime(parser.cassandra_log_format) == "2018-10-23 15:50:01,123000"

def test_us_dates_with_comma_for_ms():
    """ms for some reason is done with a comma in our logs"""
    parser = dates.LogDateFormatParser()
    parsed = parser.parse_timestamp("2018-10-23 15:50:01,123")
    assert parsed.strftime(parser.cassandra_log_format) == "2018-10-23 15:50:01,123000"

def test_european_dates_with_comma_for_ms():
    """ms for some reason is done with a comma in our logs"""
    parser = dates.LogDateFormatParser()
    parsed = parser.parse_timestamp("2018-23-10 15:50:01,123")
    assert parsed.strftime(parser.cassandra_log_format) == "2018-10-23 15:50:01,123000"
