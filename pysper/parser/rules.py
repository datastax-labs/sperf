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

'''
A set of functions defining a domain-specific language that specifies a set of rules for
parsing the lines in a log fil
'''
import re
from datetime import datetime
from collections import defaultdict
import pytz

class switch:
    '''
    Tries multiple rules in the specified order until one returns a value other than None.
    Returns the result of the first successful rule.  Can be configured to run only a
    subset of the rules using an optional case value.
    '''

    def __init__(self, children):
        '''
        Constructor expects to be passed one or more case and rule objects. The case objects are
        used to group the rules.
        '''

        self.rules = defaultdict(list)
        keys = None
        for child in children:
            if isinstance(child, case):
                keys = child.keys
            else:
                for key in keys:
                    self.rules[key].append(child)

    def __call__(self, key, data):
        if key in self.rules:
            for r in self.rules[key]:
                result = r(data)
                if result is not None:
                    return result
        return None

class case:
    "Specifies an alternative for a switch rule."

    def __init__(self, *keys):
        '''
        Constructor expects to be passed one or more strings. At least one of the strings in
        the case must match the case value passed to the switch for the case to be selected.
        '''
        self.keys = keys

class rule:
    '''
    Executes the condition, and optionally one or more actions. If the condition returns None,
    the rule returns None immediately.  If the condition returns something other than None, the
    rule executes each action in order, passing the result of the condition into each.
    '''


    def __init__(self, source, *transforms):
        '''
        Constructor expects the first parameter to be a function that takes a string as input. The
        condition should return None to indicate failure or something else to indicate success.
        The remaining parameters should be functions that act on the result of the condition.
        '''
        self.source = source
        self.transforms = transforms

    def __call__(self, string):
        fields = self.source(string)
        if fields is not None:
            for transform in self.transforms:
                transform(fields)
        return fields

class capture:
    '''
    Matches the input string against one or more regular expressions and returns a dictionary of
    values captured by regex's named capture groups. Returns None if none of the regular expressions
    match the input string. Returns an empty dict if the regular expression doesn't contains any
    named capture groups.
    '''

    def __init__(self, *regex_strings):
        "Constructor expects a list of one or more regular expression strings."
        self.regexes = []
        for regex in regex_strings:
            self.regexes.append(re.compile(regex))

    def __call__(self, string):
        for regex in self.regexes:
            cap = regex.match(string)
            if cap:
                return cap.groupdict()
        return None

class convert:
    '''
    Applies the specified conversion function against each of the named fields in the input dictionary.
    The value of each field is passed to the conversion function and is replaced by the value returned
    by the conversion function.
    '''

    def __init__(self, func, *field_names):
        '''
        Constructor expects a conversion function followed by fields specifying one or more field names.
        The conversion function should take a string as input and return a converted value.
        '''
        self.func = func
        self.field_names = field_names

    def __call__(self, fields):
        for field_name in self.field_names:
            if field_name in fields and fields[field_name] is not None:
                fields[field_name] = self.func(fields[field_name])

class update:
    "Updates the specified fields in the input dictionary with the specified values."

    def __init__(self, **extras):
        '''
        Constructor expects a set of named parameters specifying key value pairs to be set in the input
        dictionary.
        '''
        self.extras = extras

    def __call__(self, fields):
        fields.update(self.extras)

class default:
    '''
    Updates the specified fields in the input dictionary with the specified values only if the field
    does not already exist.
    '''

    def __init__(self, **defaults):
        '''
        Constructor expects a set of named parameters specifying key value pairs to be set in the input
        dictionary.
        '''
        self.defaults = defaults

    def __call__(self, fields):
        for key, value in self.defaults.items():
            if key not in fields:
                fields[key] = value

def strip(string):
    "Strips the leading and trailing whitespace from the supplied string and returns the result."
    return string.strip()

class date:
    """Parses the supplied date and returns the resulting datetime value.
    assumes UTC format since none of our logs provide TZ"""

    def __init__(self, newformat):
        "Constructor expects a date string supported by datetime.strptime."
        self.format = newformat

    def __call__(self, adate):
        parsed = datetime.strptime(adate, self.format)
        if not parsed.tzinfo:
            return pytz.utc.localize(dt=parsed, is_dst=False)
        return parsed

class split:
    "Splits the supplied string and returns the resulting list."

    def __init__(self, delimiter):
        "Constructor expects a string to use as the delimiter."
        self.delimiter = delimiter

    def __call__(self, string):
        return string.split(self.delimiter)

class update_message:
    "Updates message fields from the capture message which is presumably a java log"

    def __init__(self, capture_message):
        self.capture_message = capture_message

    def __call__(self, fields):
        """ updates message fields """
        if 'source_file' not in fields or 'message' not in fields:
            return
        subfields = self.capture_message(fields['source_file'][:-5], fields['message'])
        if subfields is not None:
            fields.update(subfields)

def mkcapture(cap_rule, update_func, with_date=True):
    """ build a top-level capture function """
    if with_date:
        return rule(
            cap_rule,
            convert(date('%Y-%m-%d %H:%M:%S,%f'), 'date'),
            convert(int, 'source_line'),
            update_func,
            default(event_product='unknown', event_category='unknown', event_type='unknown'))
    return rule(
        cap_rule,
        convert(int, 'source_line'),
        update_func,
        default(event_product='unknown', event_category='unknown', event_type='unknown'))

def percent(value):
    "Converts the supplied string to a floating point and multiplies it by 100."
    return float(value) * 100

def int_with_commas(value):
    "Removes any commas from the input string and converts the result to an int."
    return int(value.replace(',', ''))

def nodeconfig(nodeconfig_line):
    """ converts to nodeconfig """
    config = {}
    tokens = nodeconfig_line.split('; ')
    for token in tokens:
        pairs = token.split('=')
        if len(pairs) > 1:
            config[pairs[0]] = pairs[1]
    return config

def jvm_args(args_line):
    """ converts jvm args to k/v pairs """
    args = {}
    tokens = args_line.split(',')
    for token in tokens:
        pairs = token.split('=')
        if len(pairs) > 1:
            key = pairs[0].strip()
            value = "".join(pairs[1:]).strip()
            if key in args:
                args[key].append(value)
            else:
                args[key] = [value]
        else:
            #we don't care if we've seen a duplicate here
            args[token.strip()] = True
    return args
