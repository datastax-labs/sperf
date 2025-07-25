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

"""analyzes debug.logs for slow queries"""
import re
from collections import OrderedDict
from pysper.diag import find_logs, FileWithProgress
from pysper.parser.rules import date
from pysper.util import bucketize
from pysper.dates import date_parse
from pysper import VERSION, perc
from pysper.core import OrderedDefaultDict


class SlowQueryParser:
    """parses logs for slow queries"""

    BEGIN = "begin"
    begin_match = re.compile(
        r" *(?P<level>[A-Z]*) *\[(?P<thread_name>[^\]]*?)[:_-]?(?P<thread_id>[0-9]*)\] (?P<date>.{10} .{12}) *(?P<source_file>[^:]*):(?P<source_line>[0-9]*) - (?P<numslow>\d+) operations were slow in the last (?P<threshold>\d+) msecs:"
    )
    slow_match_multiple = re.compile(
        r"\<((?P<query>.*))\>, was slow (?P<count>\d+) times: avg\/min\/max (?P<avg>\d+)/(?P<min>\d+)\/(?P<time>\d+) msec - slow timeout (?P<threshold>\d+) msec(?P<cross>\/cross-node)?"
    )
    slow_match = re.compile(
        r"\<((?P<query>.*))\>, time (?P<time>\d+) msec - slow timeout (?P<threshold>\d+) msec(?P<cross>\/cross-node)?"
    )
    fail_match_multiple = re.compile(
        r"\<((?P<query>.*))\>, timed out (?P<numslow>\d+) times: avg\/min\/max (?P<avg>\d+)/(?P<min>\d+)\/(?P<time>\d+) msec -timeout (?P<threshold>\d+) msec(?P<cross>\/cross-node)?"
    )
    fail_match = re.compile(
        r"\<((?P<query>.*))\>, total time (?P<time>\d+) msec - timeout (?P<threshold>\d+) msec(?P<cross>\/cross-node)?"
    )

    begin_timed_out = re.compile(
        r" *(?P<level>[A-Z]*) *\[(?P<thread_name>[^\]]*?)[:_-]?(?P<thread_id>[0-9]*)\] (?P<date>.{10} .{12}) *(?P<source_file>[^:]*):(?P<source_line>[0-9]*) - (?P<numslow>\d+) operations timed out in the last (?P<threshold>\d+) msecs:"
    )
    timed_out_match = re.compile(
        r"\<(?P<query>.*)\>, total time (?P<time>\d+) msec, timeout (?P<threshold>\d+) msec"
    )

    def parse(self, logfile):
        """parses a debug log for slow queries"""
        ret = OrderedDict()
        for line in logfile:
            m = self.begin_match.match(line)
            time_match = self.begin_timed_out.match(line)
            if m:
                ret["numslow"] = int(m.group("numslow"))
                ret["date"] = date()(m.group("date"))
            elif time_match:
                ret["numslow"] = int(time_match.group("numslow"))
                ret["date"] = date()(time_match.group("date"))
            else:
                for match in [
                    self.slow_match,
                    self.fail_match,
                    self.slow_match_multiple,
                    self.fail_match_multiple,
                    self.timed_out_match,
                ]:
                    m = match.match(line)
                    if m:
                        ret.update(m.groupdict())
                        if match in [self.fail_match, self.fail_match_multiple]:
                            ret["type"] = "fail"
                        elif match == self.timed_out_match:
                            ret["type"] = "timed_out"
                        else:
                            ret["type"] = "slow"
                        yield ret
                        break


class SlowQueryAnalyzer:
    """analyzes results from parsing slow queries"""

    def __init__(self, diag_dir, files=None, start=None, end=None):
        self.diag_dir = diag_dir
        self.files = files
        self.parser = SlowQueryParser()
        self.querytimes = OrderedDefaultDict(list)
        self.queries = []
        self.analyzed = False
        self.start = None
        self.end = None
        self.cross = 0
        self.timedout = 0
        self.start_time = None
        self.end_time = None
        if start:
            self.start_time = date_parse(start)
        if end:
            self.end_time = date_parse(end)

    def analyze(self):
        """analyze slow queries"""
        parser = SlowQueryParser()
        target = find_logs(self.diag_dir, "debug.log")
        if self.files:
            target = self.files
        for f in target:
            with FileWithProgress(f) as log:
                for query in parser.parse(log):
                    if self.start_time and query["date"] < self.start_time:
                        continue
                    if self.end_time and query["date"] > self.end_time:
                        continue
                    if not self.start:
                        self.start = query["date"]
                        self.end = query["date"]
                    if query["date"] > self.end:
                        self.end = query["date"]
                    if query["date"] < self.start:
                        self.start = query["date"]
                    if "avg" in query:
                        for x in range(query["numslow"]):
                            self.querytimes[query["date"]].append(int(query["time"]))
                    else:
                        self.querytimes[query["date"]].append(int(query["time"]))
                    self.queries.append((query["query"], int(query["time"])))
                    if "type" in query and query["type"] == "timed_out":
                        self.timedout += 1 * int(query["numslow"])
                    if query["cross"] is not None:
                        self.cross += 1
        self.analyzed = True

    def print_report(self, command_name, interval=3600, top=3):
        """print the report"""
        if not self.analyzed:
            self.analyze()
        print("%s version: %s" % (command_name, VERSION))
        print("")
        print(
            "this is not a very accurate report, use it to discover basics, but I suggest analyzing the logs by hand for any outliers"
        )
        print("")

        if not self.queries:
            if self.files:
                print("no queries found the files provided")
                for file_name in self.files:
                    print("- %s" % file_name)
            else:
                print("no queries found in diag tarball '%s'" % self.diag_dir)
            return
        self.__print_query_times(
            sorted(
                bucketize(
                    self.querytimes, start=self.start, end=self.end, seconds=interval
                ).items(),
                key=lambda t: t[0],
            )
        )
        print("slow query breakdown")
        print("--------------------")
        print(
            len(self.queries),
            "total, %s cross-node, %s timeouts" % (self.cross, self.timedout),
        )
        print()
        print("Top %s slow queries:" % top)
        print("-" * 30)
        for query, time in sorted(
            self.queries, key=lambda t: (t[1], t[0]), reverse=True
        )[0:top]:
            print("%sms: %s" % (time, query))
            print("")

    def __print_query_times(self, data):
        """print data to the user, expecting datetime keys and list(int) values"""
        timings = perc.Stats([q[1] for q in self.queries])
        window = timings.percentile(25) - 1
        window2 = timings.percentile(50) - 1
        window3 = timings.percentile(75) - 1
        window4 = timings.percentile(99) - 1
        print(". <%sms + >%sms ! >%sms X >%sms" % (window, window2, window3, window4))
        print("-" * 30)
        worst = None
        for time, qtimes in data:
            total = sum(qtimes)
            if not worst:
                worst = (time, total)
            elif total > worst[1]:
                worst = (time, total)
            print(time, " ", end="")
            for qtime in qtimes:
                c = "."
                if qtime > window2:
                    c = "+"
                if qtime > window3:
                    c = "!"
                if qtime > window4:
                    c = "X"
                print(c, end="")
            print("")
        print("")
        print("worst period: %s (%sms)" % worst)
        print("")
