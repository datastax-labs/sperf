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

"""bgrep command"""
from pysper.commands import flags
from pysper.bgrep import BucketGrep

def add_flags(subparsers, run_func):
    """helps share code between deprecated command and supported one"""
    help_text = 'search for custom regex and bucketize results'
    bgrep_parser = subparsers.add_parser('bgrep', help=help_text,
                                         formatter_class=flags.LineWrapRawTextHelpFormatter)
    bgrep_parser.add_argument("regex", help="regular expression to match")
    bgrep_parser.add_argument('-i', '--interval', type=int, nargs='?', const=3600, default=3600,
                              help="interval to report on in seconds (default 3600)")
    bgrep_parser.add_argument('-st', '--start', type=str, nargs='?', const=None, default=None,
                              help="start date/time to begin parsing")
    bgrep_parser.add_argument('-et', '--end', type=str, nargs='?', const=None, default=None,
                              help="end date/time to stop parsing")
    bgrep_parser.add_argument('-c', '--case', dest="case", action='store_true',
                              help="case-sensitive search")
    flags.add_diagdir(bgrep_parser)
    flags.add_files(bgrep_parser)
    bgrep_parser.set_defaults(func=run_func)

def build(subparsers):
    """setup the bgrep command"""
    add_flags(subparsers, run)

def run(args):
    """ run bgrep """
    files = None
    if args.files:
        files = args.files.split(',')
    b = BucketGrep(args.regex, diag_dir=args.diag_dir, files=files,
                   start=args.start, end=args.end, ignorecase=not args.case)
    b.print_report(interval=args.interval)
