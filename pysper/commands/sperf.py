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

"""main sperf parent command"""
import argparse
from pysper import env, VERSION
from pysper.commands import core, search, sysbottle, flags, ttop, sperf_default


def _build_sperf_cmd():
    """main entry point command, returns subparsers to add more commands too"""
    parser = argparse.ArgumentParser(
        description="Sperf provides a number of useful "
        + "reports from the diagtarball, iostat and the nodes themselves.",
        formatter_class=flags.LineWrapRawTextHelpFormatter,
    )
    parser.add_argument(
        "-x",
        "--no-progress",
        dest="noprogress",
        action="store_true",
        help="shows file progress to show how long it takes to process each file",
    )
    parser.add_argument(
        "-v",
        "--debug",
        dest="debug",
        action="store_true",
        help="shows debug output. "
        + "Useful for bug reports and diagnosing issues with sperf",
    )
    parser.add_argument(
        "-fe",
        "--file_encoding",
        type=str,
        default="utf-8",
        help="shows debug output. "
        + "Useful for bug reports and diagnosing issues with sperf",
    )
    parser.add_argument(
        "-e",
        "--eu",
        dest="eu",
        action="store_true",
        help="set log format to EU. Is ignored by sysbottle which has it's own logging engine",
    )
    parser.add_argument(
        "-pt" "--permissive-time",
        dest="permissive_time",
        action="store_true",
        help="allow partial timestamps for commandline arguments",
    )
    sperf_default.build(parser)
    return parser, parser.add_subparsers(title="Commands")


def build_parser():
    """build the parser that wires up the subcommands and their flags"""
    parser, subparsers = _build_sperf_cmd()
    core.build(subparsers)
    search.build(subparsers)
    sysbottle.build(subparsers)
    ttop.build(subparsers)
    return parser


def run():
    """run is the entry point that selects the subcommand to run"""
    parser = build_parser()
    args = parser.parse_args()
    env.FILE_ENCODING = args.file_encoding
    env.PROGRESS = not args.noprogress
    if args.debug:
        env.DEBUG = args.debug
    if args.eu:
        env.IS_US_FMT = False
    if args.permissive_time:
        env.PERMISSIVE_TIME = True
    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as ex:
            if env.DEBUG:
                raise ex
            print(str(ex))
            print("")
            print(
                "To show strack trace use the -v flag. For example: 'sperf -v cassread'"
            )
    else:
        print("sperf version %s" % VERSION)
        print()
        sperf_default.run(args)
    # for formatting
    print("\n")
