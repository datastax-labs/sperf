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

"""humanize provides formatting help for large numbers and makes bytes and ms easier to read"""
from decimal import Decimal

SECOND = 1000
MINUTE = 60000
HOUR = 3600000
DAY = 86400000
#this is not strictly correct as it ignores leap
#years but fits expectations when reading output
YEAR = 31536000000

KB = 1024
MB = 1048576
GB = 1073741824
TB = 1099511627776
PB = 1125899906842624

def format_millis(num_ms):
    """converts milliseconds to a human readable string.
    NOTE when returning years this pretends leap seconds don't exist and that a year is consistently 365 days exactly"""
    if num_ms < SECOND:
        return "%s ms" % format_num_float(num_ms)
    if num_ms < MINUTE:
        seconds = float(num_ms)/ SECOND
        return "%s %s" % (format_num_float(seconds), pluralize(seconds, "second"))
    if num_ms < HOUR:
        minutes = float(num_ms) / MINUTE
        return "%s %s" % (format_num_float(minutes), pluralize(minutes, "minute"))
    if num_ms < DAY:
        hours = float(num_ms)/ HOUR
        return "%s %s" % (format_num_float(hours), pluralize(hours, "hour"))
    if num_ms < YEAR:
        days = float(num_ms)/ DAY
        return "%s %s" % (format_num_float(days), pluralize(days, "day"))
    years = float(num_ms)/ YEAR
    return "%s %s" % (format_num_float(years), pluralize(years, "year", precision=2))

def format_seconds(num_sec):
    """converts seconds to a human readable string
    NOTE when returning years this pretends leap seconds don't exist and that a year is consistently 365 days exactly"""
    if num_sec < 60:
        return "%s %s" % (format_num(num_sec), pluralize(num_sec, "second"))
    return format_millis(num_sec * 1000)

def to_bytes(num, unit):
    """converts human number back into bytes"""
    unit_lr = unit.lower()
    if unit_lr == "pb":
        return num * PB
    if unit_lr == "tb":
        return num * TB
    if unit_lr == "gb":
        return num * GB
    if unit_lr == "mb":
        return num * MB
    if unit_lr == "kb":
        return num * KB
    if unit_lr == "bytes":
        return num
    raise "unexpected unit %s of number %i, cannot process filter cache stats" % (unit, num)

def format_bytes(num_bytes, prec=2):
    """converts bytes into a human readable string. NOTE: uses 1024 base and not 1000 base"""
    formatted = ""
    if num_bytes is None:
        formatted = "Not available"
    elif num_bytes < KB:
        formatted = "%s %s" % (format_num(round(num_bytes)), pluralize(num_bytes, "byte"))
    elif num_bytes < MB:
        formatted = "%s kb" % format_num_float(float(num_bytes) / KB, prec)
    elif num_bytes < GB:
        mbs = float(num_bytes) / MB
        formatted = "%s mb" % format_num_float(mbs, prec)
    elif num_bytes < TB:
        gbs = float(num_bytes) / GB
        formatted = "%s gb" % format_num_float(gbs, prec)
    elif num_bytes < PB:
        tbs = float(num_bytes) / TB
        formatted = "%s tb" % format_num_float(tbs, prec)
    else:
        formatted = "%s pb" % format_num_float(float(num_bytes) / PB, prec)
    return formatted

def pluralize(num, string, precision=2):
    """very very naive pluralize, just adds s"""
    if round(Decimal(num), precision) > round(Decimal("1.00"), precision):
        return "%ss" % string
    return string

def format_num(number):
    """add commas"""
    return "{:,d}".format(round(number))

def format_num_float(number, prec=2):
    """add commas"""
    return "{:,.{}f}".format(number, prec)

def format_list(data, wrap_every=3, sep=", ", newline="\n"):
    """wrap every 3 elements into a newline.
    Separate every element with specified separator"""
    if not data:
        return ""
    output = []
    for idx, el in enumerate(data):
        suffix = sep
        if (idx + 1) % wrap_every == 0:
            suffix = newline
        output.append(el)
        output.append(suffix)
    return "".join(output[0:-1])

def pad_table(table, min_width=0, extra_pad=0):
    """takes a multidimensional array of strings and pads them so they're evenly formatted when printed out"""
    longest = []
    most_cols = 0
    for row in table:
        #naively assumes we're always passing in collections and not a string
        most_cols = max(len(row), most_cols)
    num = 0
    for row in table:
        if len(row) != most_cols:
            continue
        col_length = []
        for col in row:
            col_length.append(len(col))
        if not longest:
            longest = col_length
            num = len(col_length)
        else:
            for i in range(num):
                a = longest[i]
                b = col_length[i]
                if b > a:
                    longest[i] = b
    #pad step
    for ri, row in enumerate(table):
        for i, col in enumerate(row):
            pad = longest[i]
            row[i] = "%-*s" % (max(pad+extra_pad, min_width), col)
        table[ri] = row
