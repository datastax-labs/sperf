# Copyright 2021 DataStax, Inc
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

"""drops module has the command and logic for finding drops, their reasons and can make recommendations on next steps"""

import pprint
import os
import re
from datetime import datetime
from pysper import env
from pysper.commands import flags
import multiprocessing as mp


def build(subparsers):
    """setup the bgrep command"""
    help_text = "find drops and suggest possible causes and then fixes for those causes"
    drops_parser = subparsers.add_parser(
        "drops", help=help_text, formatter_class=flags.LineWrapRawTextHelpFormatter
    )
    drops_parser.add_argument(
        "locations",
        nargs="*",
        default=os.getcwd(),
        help="list of locations to parse, will parse any file passed to it, and any directory will be walked and searched for all system.log files",
    )
    drops_parser.add_argument(
        "-w",
        "--workers",
        type=int,
        nargs="?",
        default=mp.cpu_count(),
        help="number of workers to run when parsing (default 4)",
    )
    drops_parser.add_argument(
        "-st",
        "--start",
        type=str,
        nargs="?",
        const=None,
        default=None,
        help="start date/time to begin parsing (format: YYYY-MM-DD hh:mm:ss,SSS)",
    )
    drops_parser.add_argument(
        "-et",
        "--end",
        type=str,
        nargs="?",
        const=None,
        default=None,
        help="end date/time to stop parsing (format: YYYY-MM-DD hh:mm:ss,SSS)",
    )
    drops_parser.set_defaults(func=run)


class ReadDrops:
    def __init__(self, data):
        self.regex = re.compile(
            r"INFO  \[(?P<thread>.*)\] (?P<date>.{10} .{12}) *(?P<source_file>[^:]*):(?P<source_line>[0-9]*) - (?P<messageType>\S*) messages were dropped in the last 5 s: (?P<localCount>\d*) internal and (?P<remoteCount>\d*) cross node. Mean internal dropped latency: (?P<localLatency>\d*) ms and Mean cross-node dropped latency: (?P<remoteLatency>\d*) ms"
        )
        self.count = data

    def read_line(self, line, start_time_filter, end_time_filter):
        match = self.regex.search(line)
        if match:
            raw_date = match.group("date")
            date = datetime.fromisoformat(raw_date.replace(",", "."))
            if start_time_filter is not None and start_time_filter > date:
                return
            if end_time_filter is not None and end_time_filter < date:
                return
            local = match.group("localCount")
            remote = match.group("remoteCount")
            messageType = match.group("messageType")
            if date in self.count:
                if messageType in self.count[date]:
                    self.count[date][messageType]["local"] += local
                    self.count[date][messageType]["remote"] += remote
                else:
                    self.count[date][messageType] = {"local": local, "remote": remote}
            else:
                self.count[date] = {messageType: {"local": local, "remote": remote}}


def run(args):
    """run drops"""
    if env.DEBUG:
        print(args)
    data = mp.Manager().dict()
    parsers = [
        ReadDrops(data),
    ]
    parse_locations(
        args.locations,
        parsers,
        args.workers,
        start_time_filter=args.start,
        end_time_filter=args.end,
        verbose=env.DEBUG,
    )
    for k, v in data.items():
        pprint.pprint(k.strftime("%Y-%m-%d %H:%M:%S,%f"))
        pprint.pprint(v)


def read_file(f, parsers, start_time_filter, end_time_filter):
    """allows mp"""
    print("opening file " + f)
    with open(f) as fd:
        for line in fd:
            for p in parsers:
                p.read_line(line, start_time_filter, end_time_filter)


def parse_files(system_files, parsers, workers, start_time_filter, end_time_filter):
    with mp.Pool(processes=workers) as pool:
        responses = []
        for f in system_files:
            res = pool.apply_async(
                read_file,
                (
                    f,
                    parsers,
                    start_time_filter,
                    end_time_filter,
                ),
            )
            responses.append(res)
        for res in responses:
            res.get()


def parse_locations(
    locations,
    parsers,
    workers,
    syslog_name="system.log",
    start_time_filter=None,
    end_time_filter=None,
    verbose=False,
):
    """new mp version of diag parsing"""
    files = []
    for loc in locations:
        if verbose:
            print("looking at " + loc)
        if os.path.isfile(loc):
            if verbose:
                print("adding %s to file list" % loc)
            files.append(loc)
        elif os.path.isdir(loc):
            for root, _, f in os.walk(loc, topdown=False):
                for name in f:
                    if syslog_name in name:
                        file_name = os.path.join(root, name)
                        if verbose:
                            print("adding %s to file list" % file_name)
                        files.append(file_name)
        else:
            print("warning file %s is neither file or directory skipping" % loc)
    parse_files(files, parsers, workers, start_time_filter, end_time_filter)
