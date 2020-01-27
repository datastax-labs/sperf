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

"""ttop command wiring"""
from pysper.commands import flags
from pysper.ttop import TTopAnalyzer

def build(subparsers):
    """adds the flags for ttop"""
    ttop_parser = subparsers.add_parser('ttop',
                                        help='Analyze ttop files',
                                        formatter_class=flags.LineWrapRawTextHelpFormatter)
    ttop_parser.add_argument("files", help="ttop file to generate report on", nargs='+')
    ttop_parser.add_argument('-a', '--alloc', action='store_true', dest='alloc', default=False,
                             help='show allocation instead of cpu')
    ttop_parser.add_argument('-c', '--collate', action='store_false', dest='collate', default=True,
                             help="don't collate threads (default: true)")
    ttop_parser.add_argument('-k', '--top_k', type=int, nargs='?', const=None, default=None,
                             help="number of top threads to show (default all)")
    ttop_parser.add_argument('-st', '--start', type=str, nargs='?', const=None, default=None,
                             help="start date/time to begin parsing")
    ttop_parser.add_argument('-et', '--end', type=str, nargs='?', const=None, default=None,
                             help="end date/time to stop parsing")
    ttop_parser.set_defaults(func=run)

def run(args):
    """run the ttop analyzer"""
    analyzer = TTopAnalyzer(args.files)
    analyzer.print_report(top=args.top_k, alloc=args.alloc, collate=args.collate, start=args.start, end=args.end)
