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

"""simple version output"""
import sys
from pysper import VERSION
from pysper.changelog import CHANGES
from pysper.commands import flags


def build(subparsers):
    """setups the version command"""
    version_parser = subparsers.add_parser(
        "version",
        help="list the version of sperf",
        formatter_class=flags.LineWrapRawTextHelpFormatter,
    )
    version_parser.set_defaults(
        func=lambda _: print(
            "sperf %s-%s\n\nchangelog:\n%s" % (VERSION, sys.version, CHANGES)
        )
    )
