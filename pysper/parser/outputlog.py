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

# pylint: disable=line-too-long
""" parser for dse output.log """
from pysper.parser.rules import switch, rule, convert, default
from pysper.parser.captures import output_capture_rule
from pysper.parser.cases import config_rules, dd_rules, daemon_rules

capture_message = switch((
    *daemon_rules(),
    *config_rules(),
    *dd_rules(),
))

def update_message(fields):
    """ updates message fields """
    subfields = None
    if 'source_file' in fields:
        subfields = capture_message(fields['source_file'][:-5], fields['message'])
    else:
        #need to handle the no source file output.log format
        if fields['message']:
            # dirty hack where it the message structure tells us what we want
            tokens = fields['message'].split()
            if tokens[0] == 'DiskAccessMode':
                subfields = capture_message('DatabaseDescriptor', fields['message'])
            elif len(tokens) > 1 and tokens[0] == 'This' and (tokens[1] == "instance" or tokens[1] == "machine"):
                subfields = capture_message('DseConfig', fields['message'])
    if subfields is not None:
        fields.update(subfields)

capture_line = rule(output_capture_rule,
                    convert(int, 'source_line'),
                    update_message,
                    default(event_product='unknown', event_category='unknown', event_type='unknown'))
