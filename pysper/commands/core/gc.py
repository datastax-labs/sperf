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

"""gc command"""
from pysper.commands import flags
from pysper.core.gcinspector import GCInspector

def add_flags(subparsers, run_func):
    """helps share code between deprecated command and supported one"""
    help_text = 'show gc info. provides time series of gc duration and frequency'
    gc_parser = subparsers.add_parser('gc', help=help_text,
                                      formatter_class=flags.LineWrapRawTextHelpFormatter)
    gc_parser.add_argument('-r', '--reporter', type=str, nargs='?', const='summary', default='summary',
                           help="report to run, either summary or nodes (default summary)")
    gc_parser.add_argument('-i', '--interval', type=int, nargs='?', const=3600, default=3600,
                           help="interval to report on in seconds (default 3600)")
    gc_parser.add_argument('-k', '--top-k', type=int, nargs='?', const=3, default=3,
                           help="top K worst GC events to show (default 3)")
    gc_parser.add_argument('-st', '--start', type=str, nargs='?', const=None, default=None,
                           help="start date/time to begin parsing")
    gc_parser.add_argument('-et', '--end', type=str, nargs='?', const=None, default=None,
                           help="end date/time to stop parsing")
    flags.add_diagdir(gc_parser)
    flags.add_files(gc_parser)
    gc_parser.set_defaults(func=run_func)

def build(subparsers):
    """setup the gc command"""
    add_flags(subparsers, run)

def run(args):
    """ run the gcinspector """
    files = None
    if args.files:
        files = args.files.split(',')
    g = GCInspector(diag_dir=args.diag_dir, files=files, start=args.start, end=args.end)
    if args.reporter == 'summary':
        g.print_report(interval=args.interval, top=args.top_k)
    elif args.reporter == 'nodes':
        g.print_report(interval=args.interval, by_node=True, top=args.top_k)
    else:
        print("Invalid reporter %s: must be either summary or nodes" % args.reporter)
