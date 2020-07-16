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

"""responsible for date parsing and format detection"""
from datetime import datetime, timezone
import json
from pysper import env

CASSANDRA_LOG_FORMAT = "%Y-%m-%d %H:%M:%S,%f"

class DateTimeJSONEncoder(json.JSONEncoder):
    """date time json encoder that converst datetime to an string in isoformat"""
    def default(self, o):#pylint: disable=method-hidden
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

def max_utc_time():
    """returns max UTC time"""
    return datetime.max.replace(tzinfo=timezone.utc)

def min_utc_time():
    """returns min UTC time"""
    return datetime.min.replace(tzinfo=timezone.utc)

def date_parse(date_string):
    """uses dateutil to parse and sets the tz if none is provided"""
    dt = LogDateFormatParser().parse_timestamp(date_string)
    if not dt.tzinfo:
        return dt.replace(tzinfo=timezone.utc)
    return dt

class LogDateFormatParser:
    """LogDateFormatParser handles the particular format used in
    DSE logs
    """
    def __init__(self):
        if env.IS_US_FMT:
            self.mp = 5
            self.dp = 8
        else:
            self.mp = 8
            self.dp = 5

    def parse_timestamp(self, time_str):
        """ParseTimestamp creates a LogTimestamp based on the
        CASSANDRA_LOG_FORMAT and assumes UTC timezone always"""
        parsed = None
        try:
            parsed = datetime(
                int(time_str[:4]),
                int(time_str[self.mp:self.mp+2]),
                int(time_str[self.dp:self.dp+2]),
                int(time_str[11:13]),
                int(time_str[14:16]),
                int(time_str[17:19]),
                int(time_str[20:23]) * 1000
                )
        except ValueError as e:
            raise Exception("invalid date, try to rerun with sperf -l eu <subcommand> error was %s" % e)
        return parsed.replace(tzinfo=timezone.utc)
