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
from datetime import datetime
import json
import pytz
from dateutil import parser

CASSANDRA_LOG_FORMAT = "%Y-%m-%d %H:%M:%S,%f"

class DateTimeJSONEncoder(json.JSONEncoder):
    """date time json encoder that converst datetime to an string in isoformat"""
    def default(self, o):#pylint: disable=method-hidden
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

def max_utc_time():
    """returns max UTC time"""
    utc_tz = pytz.utc
    return utc_tz.localize(dt=datetime.max, is_dst=False)

def min_utc_time():
    """returns min UTC time"""
    utc_tz = pytz.utc
    return utc_tz.localize(dt=datetime.min, is_dst=False)

def date_parse(date_string):
    """uses dateutil to parse and sets the tz if none is provided"""
    dt = parser.parse(date_string)
    if not dt.tzinfo:
        return pytz.utc.localize(dt=dt, is_dst=False)
    return dt

class LogDateFormatParser:
    """LogDateFormatParser handles the particular format used in
    DSE logs
    """
    def __init__(self):
        self.cassandra_log_format = "%Y-%m-%d %H:%M:%S,%f"
        self.cassandra_log_format_eu = "%Y-%d-%m %H:%M:%S,%f"
        self.current_format = self.cassandra_log_format

    def parse_timestamp(self, time_str):
        """ParseTimestamp creates a LogTimestamp based on the
        CASSANDRA_LOG_FORMAT and assumes UTC timezone always"""
        parsed = None
        time_str = time_str.replace(".", ",")
        try:
            parsed = datetime.strptime(time_str, self.current_format)
        except ValueError:
            #try opposite of whatever DEFAULT_FORMAT was
            alternate_format = ""
            if self.current_format == self.cassandra_log_format:
                alternate_format = self.cassandra_log_format_eu
            else:
                alternate_format = self.cassandra_log_format
            parsed = datetime.strptime(time_str, alternate_format)
            #if successful flip default
            self.current_format = alternate_format
        utc_tz = pytz.utc
        return utc_tz.localize(dt=parsed, is_dst=False)
