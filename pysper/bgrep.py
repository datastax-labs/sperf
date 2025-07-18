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

"""bucketgrep module"""
import re
import os
from pysper.parser.rules import date
from pysper import VERSION, diag
from pysper.util import bucketize, textbar, extract_node_name
from pysper.dates import date_parse
from pysper.core import OrderedDefaultDict


class BucketGrep:
    """greps for custom regex and bucketizes results"""

    strayre = r".*"
    basere = r" *(?P<level>[A-Z]*) *\[(?P<thread_name>[^\]]*?)[:_-]?(?P<thread_id>[0-9]*)\] (?P<date>.{10} .{12}) *.*"

    def __init__(
        self,
        regex,
        diag_dir=None,
        files=None,
        start=None,
        end=None,
        ignorecase=True,
        report="summary",
    ):
        self.diag_dir = diag_dir
        self.files = files
        self.start = None
        self.end = None
        self.start_time = None
        self.end_time = None
        self.last_time = None
        self.report = report
        if start:
            self.start_time = date_parse(start)
        if end:
            self.end_time = date_parse(end)
        if ignorecase:
            self.strayregex = re.compile(self.strayre + regex + ".*", re.IGNORECASE)
            self.timeregex = re.compile(self.basere + regex + ".*", re.IGNORECASE)
            self.supplied_regex = regex.lower()
        else:
            self.strayregex = re.compile(self.strayre + regex + ".*")
            self.timeregex = re.compile(self.basere + regex + ".*")
            self.supplied_regex = regex
        self.valid_log_regex = re.compile(self.basere)
        self.node_matches = OrderedDefaultDict()
        self.matches = OrderedDefaultDict(list)
        self.count = 0
        self.unknown = 0
        self.analyzed = False

    def analyze(self):
        """parses logs for results"""
        print("bucketgrep version %s" % VERSION)
        print("search: '%s'" % self.supplied_regex)
        target = None
        if self.files:
            target = self.files
        elif self.diag_dir:
            if self.diag_dir == ".":
                directory_path = os.getcwd()
                print("from directory '%s':" % directory_path)
            else:
                print("from directory '%s':" % self.diag_dir)
            target = diag.find_logs(self.diag_dir)
        else:
            raise Exception("no diag dir and no files specified")
        for file in target:
            with diag.FileWithProgress(file) as log:
                node_name = extract_node_name(file, ignore_missing_nodes=True)
                self.node_matches[node_name] = OrderedDefaultDict(list)
                for line in log:
                    # as long as it's a valid log line we want the date,
                    # even if we don't care about the rest of the line so we can set
                    # the last date for any straregex lines that match
                    current_dt = self.valid_log_regex.match(line)
                    if current_dt:
                        dt = date()(current_dt.group("date"))
                        # if the log line is valite we want to set the last_time
                        self.last_time = dt
                    # we now can validate if our search term matches the log line
                    d = self.timeregex.match(line)
                    if d:
                        # normal case, well-formatted log line
                        self.__setdates(dt)
                        if self.start_time and dt < self.start_time:
                            continue
                        if self.end_time and dt > self.end_time:
                            continue
                        self.matches[dt].append(line)
                        self.node_matches[node_name][dt].append(line)
                        self.count += 1
                    else:
                        m = self.strayregex.match(line)
                        # check for a match in an unformatted line, like a traceback
                        if m:
                            if self.last_time is None:
                                # match, but no previous timestamp to associate with
                                self.unknown += 1
                                continue
                            self.matches[self.last_time].append(line)
                            self.node_matches[node_name][self.last_time].append(line)
                            self.count += 1
        self.analyzed = True

    def __setdates(self, dt):
        if not self.start:
            self.start = dt
            self.end = dt
            return
        if dt > self.end:
            self.end = dt
        if dt < self.start:
            self.start = dt

    def print_report(self, interval=3600):
        """print bucketized result counts"""

        print()
        if not self.analyzed:
            self.analyze()
        if not self.matches:
            print("No matches found")
            if self.unknown:
                print(self.unknown, "matches without timestamp")
            return
        if self.report == "summary":
            print()
            print("cluster wide")
            print("------------")
            buckets = sorted(
                bucketize(
                    self.matches, start=self.start, end=self.end, seconds=interval
                ).items(),
                key=lambda t: t[0],
            )
            maxval = len(max(buckets, key=lambda t: len(t[1]))[1])
            for time, matches in buckets:
                pad = ""
                for x in range(len(str(maxval)) - len(str(len(matches)))):
                    pad += " "
                print(
                    time.strftime("%Y-%m-%d %H:%M:%S") + pad,
                    len(matches),
                    textbar(maxval, len(matches)),
                )
        else:
            print()
            print()
            print("per node numbers")
            print("----------------")
            for node in sorted(self.node_matches.keys()):
                print()
                print("node: %s" % node)
                print("--------")
                if not len(self.node_matches[node]):
                    print("No matches for %s found" % node)
                    continue
                buckets = sorted(
                    bucketize(
                        self.node_matches[node],
                        start=self.start,
                        end=self.end,
                        seconds=interval,
                    ).items(),
                    key=lambda t: t[0],
                )
                maxval = len(max(buckets, key=lambda t: len(t[1]))[1])
                for time, matches in buckets:
                    pad = ""
                    for x in range(len(str(maxval)) - len(str(len(matches)))):
                        pad += " "
                    print(
                        time.strftime("%Y-%m-%d %H:%M:%S") + pad,
                        len(matches),
                        textbar(maxval, len(matches)),
                    )
        if self.unknown:
            print(self.unknown, "matches without timestamp")
