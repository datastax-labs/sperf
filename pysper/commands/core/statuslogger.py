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

"""statuslogger command flag wiring"""
from pysper.commands import flags
from pysper.core.statuslogger import StatusLogger, WANTED_STAGES_PREFIXES

def add_flags(subparsers, run_default_func, is_deprecated=False):
    """for code sharing of flags between deprecated and supported"""
    csv_stages = ','.join(s for s in WANTED_STAGES_PREFIXES)
    help_text = "Provides analysis of StatusLogger log lines. DSE 5.0-6.7"
    if is_deprecated:
        help_text = help_text + ". DEPRECATED use 'sperf core statuslogger' instead"
    statuslogger_parser = subparsers.add_parser('statuslogger',
                                                help=help_text,
                                                formatter_class=flags.LineWrapRawTextHelpFormatter)
    statuslogger_parser.add_argument('-r', '--reporter', type=str, nargs='?', const='summary', default='summary',
                                     help="report to run, either summary or histogram (default summary)")
    statuslogger_parser.add_argument('-s', '--stages', type=str, nargs='?', const=csv_stages, default=csv_stages,
                                     help="csv list of stage prefixes to collect, or 'all' (default: %s)" % csv_stages)
    statuslogger_parser.add_argument('-st', '--start', type=str, nargs='?', const=None, default=None,
                                     help="start date/time to begin parsing")
    statuslogger_parser.add_argument('-et', '--end', type=str, nargs='?', const=None, default=None,
                                     help="end date/time to stop parsing")

    statuslogger_parser.add_argument('-dl', '--debug_log_prefix',
                                     default='debug.log',
                                     help='if debug.log in the diag tarball has an oddball name, ' + \
                                         'can still look based on this prefix ' + \
                                         '(default "debug.log")')
    statuslogger_parser.add_argument('-sl', '--system_log_prefix',
                                     default='system.log',
                                     help='if system.log in the diag tarball has an oddball name, ' + \
                                         'can still look based on this prefix ' + \
                                         '(default "system.log")')
    flags.files_and_diag(statuslogger_parser)
    statuslogger_parser.set_defaults(func=run_default_func)

def build(subparsers):
    """build statuslogger command"""
    add_flags(subparsers, run)

def run(args):
    """run statuslogger"""
    run_func(args, 'sperf core statuslogger')

def run_func(args, command_name):
    """run statuslogger"""
    wanted = None
    files = None
    if args.files:
        files = args.files.split(',')
    if args.stages != 'all':
        wanted = tuple(filter(None, args.stages.split(',')))
    if args.reporter == 'histogram':
        StatusLogger(args.diag_dir, files=files, wanted_stages=wanted, command_name=command_name, \
            start=args.start, end=args.end, syslog_prefix=args.system_log_prefix).print_histogram()
    elif args.reporter == 'summary':
        StatusLogger(args.diag_dir, files=files, wanted_stages=wanted, command_name=command_name, \
            start=args.start, end=args.end, syslog_prefix=args.system_log_prefix).print_summary()
    else:
        print("invalid reporter %s, must be either histogram or summary" % args.reporter)
