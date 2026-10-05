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

"""droppedmessages command flag wiring"""

from pysper.commands import flags
from pysper.core.droppedmessages import DroppedMessages


def add_flags(subparsers, run_default_func):
    """flags for dropped message analysis"""
    parser = subparsers.add_parser(
        "droppedmessages",
        help="Analyzes Cassandra/DSE dropped messages",
        formatter_class=flags.LineWrapRawTextHelpFormatter,
    )

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        nargs="?",
        default="all",
        help="message type to analyze, or 'all' (default: all)",
    )

    parser.add_argument(
        "-st",
        "--start",
        type=str,
        nargs="?",
        const=None,
        default=None,
        help="start date/time to begin parsing "
        "(format: YYYY-MM-DD hh:mm:ss,SSS)",
    )

    parser.add_argument(
        "-et",
        "--end",
        type=str,
        nargs="?",
        const=None,
        default=None,
        help="end date/time to stop parsing "
        "(format: YYYY-MM-DD hh:mm:ss,SSS)",
    )

    parser.add_argument(
        "-w",
        "--window",
        type=int,
        default=20,
        help="minutes before and after an incident to search "
        "for related symptoms (default: 20)",
    )

    parser.add_argument(
        "-sl",
        "--system_log_prefix",
        default="system.log",
        help="system log filename prefix (default system.log)",
    )

    flags.files_and_diag(parser)
    parser.set_defaults(func=run_default_func)


def build(subparsers):
    """build droppedmessages command"""
    add_flags(subparsers, run)


def run(args):
    """run droppedmessages"""
    run_func(args, "sperf core droppedmessages")


def run_func(args, command_name):
    """run droppedmessages"""

    files = None
    if args.files:
        files = args.files.split(",")

    message_type = None
    if args.type.lower() != "all":
        message_type = args.type.upper()

    DroppedMessages(
        args.diag_dir,
        files=files,
        message_type=message_type,
        command_name=command_name,
        start=args.start,
        end=args.end,
        window_minutes=args.window,
        syslog_prefix=args.system_log_prefix,
    ).print_summary()