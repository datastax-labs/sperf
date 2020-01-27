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

"""diag provides functions to quickly process a diag tarball"""
import os
import re
import io
import json
from collections import namedtuple
from pysper import env, dates

class UnknownStatusLoggerWriter:
    """decorates statuslogger events from DB-2552 change (applies to DSE 6.7.5+, 6.0.10+, 5.1.17+)"""

    def __init__(self):
        self.last_event_date = None
        self.int_convert_pool = ['active', 'pending', 'backpressure',
                                 'delayed', 'completed', 'blocked', 'all_time_blocked',
                                ]
        self.int_convert_table = ['ops', 'data']
        self.int_convert_cache = ['size', 'capacity']

    def _set_pool_header(self, event):
        event['date'] = self.last_event_date
        event['event_product'] = 'cassandra'
        event['event_category'] = 'status'
        event['event_type'] = 'threadpool_header'
        if event.get("delayed_header"):
            event['rule_type'] = 'new'
        else:
            event['rule_type'] = 'old'

    def _set_pool(self, event):
        #hack in working pool events
        event['date'] = self.last_event_date
        event['event_product'] = 'cassandra'
        event['event_category'] = 'status'
        event['event_type'] = 'threadpool_status'
        event['rule_type'] = 'new'
        if event.get('delayed'):
            event['rule_type'] = 'new'
        else:
            event['rule_type'] = 'old'
        for c in self.int_convert_pool:
            if event.get(c):
                event[c] = int(event.get(c))

    def _set_table_header(self, event):
        event['date'] = self.last_event_date
        event['event_product'] = 'cassandra'
        event['event_category'] = 'status'
        event['event_type'] = 'memtable_header'

    def _set_table(self, event):
        event['date'] = self.last_event_date
        event['event_product'] = 'cassandra'
        event['event_category'] = 'status'
        event['event_type'] = 'memtable_status'
        for c in self.int_convert_table:
            if event.get(c):
                event[c] = int(event.get(c))

    def _set_cache_header(self, event):
        event['date'] = self.last_event_date
        event['event_product'] = 'cassandra'
        event['event_category'] = 'status'
        event['event_type'] = 'cache_header'

    def _set_cache(self, event):
        event['date'] = self.last_event_date
        event['event_product'] = 'cassandra'
        event['event_category'] = 'status'
        event['event_type'] = 'cache_status'
        for c in self.int_convert_cache:
            if event.get(c):
                event[c] = int(event.get(c))

    def check(self, event):#pylint: disable=too-many-return-statements
        """sets the last_event_date if present, otherwise checks
        if pool information is present and adds the proper event type and last event date"""
        #handle cases where there is no last event date yet (skip? leave alone and log?). going with skip it atm
        if not event.get('date'):
            if env.DEBUG:
                print("LAST EVENT DATE %s" % self.last_event_date)
                print("BEFORE: %s" % event)
            if not self.last_event_date:
                return
        if event.get('date'):
            self.last_event_date = event['date']
        is_unknown = event.get('event_type') == 'unknown'
        if is_unknown and event.get('header'):
            self._set_pool_header(event)
            return
        if is_unknown and event.get('pool_name'):
            self._set_pool(event)
            return
        if is_unknown and event.get('column_family_header'):
            self._set_table_header(event)
            return
        if is_unknown and event.get('keyspace'):
            self._set_table(event)
            return
        if is_unknown and event.get('cache_type'):
            self._set_cache(event)
            return
        if is_unknown and event.get('cache_header'):
            self._set_cache_header(event)
            return

class UnableToReadDiagException(Exception):
    """standard exception through when the diag tarball is not accessible"""

    def __init__(self, directory, ex):
        super().__init__(("unable to access directory diag tarball in '%s'.\n" % directory) + \
            "run this command again from a diag tarball directory (should " + \
            "contain a 'nodes' folder)\n" + \
            "or specify the -d flag with the target diag tarball folder", ex)

    def __str__(self):
        return super().args[0]

LogLine = namedtuple('LogLine', 'level thread timestamp reporter raw_data')

class UniqEventPerNodeFilter:
    """previous processed events from other files will not be run
    additional times. This is a per node limit"""

    def __init__(self):
        self.current_node = None
        self.previous_files_events = {}
        self.queued_events = set()

    def set_node(self, node):
        """adds existing events to a "seen filter" which is
        consulted for all other events"""
        #clear out all queued events and place into previous queue for previous node
        for event_id in self.queued_events:
            self.previous_files_events[self.current_node][event_id] = None
        #setup new node
        if node not in self.previous_files_events:
            self.previous_files_events[node] = {}
        self.current_node = node
        #clear out all previous queued events
        self.queued_events = set()

    def is_duplicate(self, event):
        """checked against previously processed files"""
        if event.get("event_type") == "unknown":
            return False
        #event_id = hash(str(event))
        event_id = hash(json.dumps(event, cls=dates.DateTimeJSONEncoder, sort_keys=True))
        if event_id in self.previous_files_events[self.current_node]:
            if env.DEBUG:
                print("duplicate event: node: %s, event: %s" % (self.current_node, event))
            return True
        self.queued_events.add(event_id)
        return False


def grep_date(log_string):
    """gets just the date from the log"""
    # pylint: disable=line-too-long
    match = re.search(rb' *(?P<level>[A-Z]*) *\[(?P<thread_name>[^\]]*?)[:_-]?(?P<thread_id>[0-9]*)\] (?P<date>.{10} .{12})*', log_string)
    if match:
        date_value = match.group("date").decode('ascii')
        date_parser = dates.LogDateFormatParser()
        return date_parser.parse_timestamp(date_value)
    return dates.min_utc_time()

def log_range(file_path):
    """gets timestamp of first log and last log"""
    with open(file_path, "rb") as file_handle:
        first = file_handle.readline()        # Read the first line.
        if not first:                         # empty files are safe to not process
            return dates.max_utc_time(), dates.min_utc_time()
        check = file_handle.read(1)
        if check == b'':         # parse first line twice if only one line
            return grep_date(first), grep_date(first)
        file_handle.seek(-2, os.SEEK_END)     # Jump to the second last byte.
        while file_handle.read(1) != b"\n":   # Until EOL is found...
            file_handle.seek(-2, os.SEEK_CUR) # ...jump back the read byte plus one more.
        last = file_handle.readline()         # Read last line.
    return grep_date(first), grep_date(last)

def find_files(config, file_to_find):
    """finds all the files in config.diag_dir that matches the prefix or will use
    the config.files string (split on ,) if present and not use a prefix but a full
    file name match.
    Example:
        files = [my.log], diag_dir = "" => only matches my.log NOT my.log.1
        file_to_find = "my.log", files = [], diag_dir = "mydir" => matches my.log, my.log.1, my.log.2, etc
    """
    files = []
    use_as_prefix = True
    if config.files:
        files = config.files.split(",")
        use_as_prefix = False
    elif config.diag_dir:
        try:
            files = find_logs(config.diag_dir, file_to_find, use_as_prefix)
        except Exception as ex:
            if env.DEBUG:
                print(ex)
            raise UnableToReadDiagException(config.diag_dir, ex)
    else:
        print("no --diagdir or --files flag used")
        return None
    return files

def find_logs(diag_dir, file_to_find='system.log', use_as_prefix=True):
    """will find all logs that match the prefix under diag_dir"""
    matches = []
    for (dirpath, _, files) in os.walk(diag_dir):
        for filename in files:
            if use_as_prefix:
                if use_as_prefix and filename.startswith(file_to_find):
                    fullpath = os.path.join(dirpath, filename)
                    matches.append(fullpath)
                elif not use_as_prefix and filename == file_to_find:
                    fullpath = os.path.join(dirpath, filename)
                    matches.append(fullpath)
    return matches

class FileWithProgress:
    """logs open, close if --progress is enabled only works with reads. will always log errors"""
    def __init__(self, filepath):
        self.filepath = filepath
        self.error = ""
        try:
            self.file_desc = open(self.filepath, encoding='utf8')
        except IOError as exception:
            msg = "error opening: %s with %s" % (self.filepath, str(exception))
            if env.PROGRESS:
                print("!", end='', flush=True)
            if env.DEBUG:
                print(msg)
            self.file_desc = None
            self.error = msg

    def __iter__(self):
        if not self.file_desc:
            return iter(())
        return self.file_desc.__iter__()

    def __next__(self):
        #silently skip if file_desc not set
        if not self.file_desc:
            if env.PROGRESS:
                print("x", end='', flush=True)
            return StopIteration()
        return self.file_desc.__next__()

    def __enter__(self):
        if env.PROGRESS:
            print(".", end='', flush=True)
        return self

    def read(self):
        """wrapper around file read"""
        return self.file_desc.read()

    def readline(self):
        """wrapper around file readline"""
        return self.file_desc.readline()

    def seek(self, pos, whence=io.SEEK_SET):
        """wrapper around file seek"""
        return self.file_desc.seek(pos, whence)

    def __exit__(self, exec_type, exec_value, traceback):
        if env.PROGRESS:
            print(".", end='', flush=True)
        if self.file_desc:
            self.file_desc.__exit__(exec_type, exec_value, traceback)
