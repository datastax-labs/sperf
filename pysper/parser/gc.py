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

""" parser for systemlog returning gc messages only """
from pysper.parser.rules import switch, update_message, mkcapture
from pysper.parser.captures import system_capture_rule
from pysper.parser.cases import gc_rules

capture_message = switch((gc_rules()))
capture_line = mkcapture(system_capture_rule, update_message(capture_message))
