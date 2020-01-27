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

"""slow query command wiring"""
from pysper.commands import flags
from pysper.core.slowquery import SlowQueryAnalyzer

def add_flags(subparsers, run_default_func, is_deprecated=True):
    """add flags used to share code between deprecated and supported commands"""
    help_text = 'Generates a report of slow queries in debug log. DSE 6.0-6.7'
    if is_deprecated:
        help_text = help_text + ". DEPRECATED use 'sperf core slowquery' instead"
    slowquery_parser = subparsers.add_parser('slowquery',
                                             help=help_text,
                                             formatter_class=flags.LineWrapRawTextHelpFormatter)
    flags.files_and_diag(slowquery_parser)
    slowquery_parser.add_argument('-i', '--interval', type=int, nargs='?', const=3600, default=3600,
                                  help="interval to report on in seconds (default 3600)")
    slowquery_parser.add_argument('-t', '--top', type=int, nargs='?', const=3, default=3,
                                  help="number of top queries to show (default 3)")
    slowquery_parser.add_argument('-st', '--start', type=str, nargs='?', const=None, default=None,
                                  help="start date/time to begin parsing")
    slowquery_parser.add_argument('-et', '--end', type=str, nargs='?', const=None, default=None,
                                  help="end date/time to stop parsing")
    slowquery_parser.set_defaults(func=run_default_func)

def build(subparsers):
    """adds the flags for slow query"""
    add_flags(subparsers, run)

def run(args):
    """run the slowquery analyzer"""
    run_func(args, 'sperf core slowquery')

def run_func(args, command_name):
    """made for code sharing between deprecated and supported functions"""
    files = None
    if args.files:
        files = args.files.split(',')
    sqa = SlowQueryAnalyzer(diag_dir=args.diag_dir, files=files, start=args.start, end=args.end)
    sqa.print_report(command_name, interval=args.interval, top=args.top)
