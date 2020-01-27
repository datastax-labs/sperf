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

"""schema subcommand builder"""
from pysper import diag, VERSION
from pysper.core import schema
from pysper.commands import flags

def add_flags(subparsers, run_default_func):
    """for code sharing between deprecated and supported commands"""
    help_text = 'Analyze schema for summary. DSE 5.0-6.7'
    schema_parser = subparsers.add_parser('schema', help=help_text,
                                          formatter_class=flags.LineWrapRawTextHelpFormatter)
    flags.files_and_diag(schema_parser)
    schema_parser.set_defaults(func=run_default_func)

def build(subparsers):
    """adds flags to schema cmd"""
    add_flags(subparsers, run)

def run(args):
    """run is the entrypoint for the sperf schema command"""
    run_func(args, 'sperf core schema')

def run_func(args, cmd_name):
    """for code sharing with deprecated schema"""
    print("%s: %s\n" % (cmd_name, VERSION))
    config = schema.Config(args.files, args.diag_dir)
    files = diag.find_files(config, "schema")
    parsed_schema = schema.read(files)
    print(schema.generate_report(parsed_schema))
