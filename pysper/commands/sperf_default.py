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

"""sperf bare command that is aimed at new users and provides a general summary
"""
from pysper import env
from pysper import sperf_default
from pysper.commands.core.diag import add_args


def build(diag_parser):
    """build uses the args from the new command"""
    add_args(diag_parser)


def run(args):
    """launches 'sperf default command'"""
    try:
        sperf_default.run(args)
    except Exception as ex:  # pylint: disable=broad-except
        if env.DEBUG:
            raise ex
        print(str(ex))
        print("")
        print("To show strack trace use the -v flag. For example: 'sperf -v cassread'")
