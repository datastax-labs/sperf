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

""" pysper utilities """
import os
import itertools
import bisect
import datetime
import numpy as np

#pylint: disable=too-many-arguments
def print_percentiles(label, data_list, indent=11, width=8, strformat="%.2f", pmin=True, pmax=True,
                      reverse=False, percentiles=(99, 75, 50, 25)):
    """ prints formatted percentiles using numpy from data in a list """
    np_array = np.array(data_list)
    printables = [label.ljust(indent)]
    if pmax:
        printables.append((strformat % np.amax(np_array)).ljust(width))
    for p in percentiles:
        printables.append((strformat % np.percentile(np_array, p)).ljust(width))
    if pmin:
        printables.append((strformat % np.amin(np_array)).ljust(width))
    if reverse:
        printables = reversed(printables)
    print("".join(printables))

def print_percentile_headers(label='', names=('max', 'p99', 'p75', 'p50', 'p25', 'min'), indent=11, width=8):
    """ prints evenly spaced headers, appropriate for percentiles """
    printables = [label.ljust(indent)]
    for name in names:
        printables.append(name.ljust(width))
    print("".join(printables))

#pylint: disable=too-many-arguments
def get_percentiles(label, data_list, strformat="%.2f", pmin=True, pmax=True,
                    reverse=False, percentiles=(99, 75, 50, 25)):
    """ gets formatted percentiles using numpy from data in a list """
    np_array = np.array(data_list)
    printables = [label]
    if pmax:
        printables.append((strformat % np.amax(np_array)))
    for p in percentiles:
        printables.append((strformat % np.percentile(np_array, p)))
    if pmin:
        printables.append((strformat % np.amin(np_array)))
    if reverse:
        printables = list(reversed(printables))
    return printables

def get_percentile_headers(label='', names=('max', 'p99', 'p75', 'p50', 'p25', 'min')):
    """ gets evenly spaced headers, appropriate for percentiles """
    printables = [label]
    for name in names:
        printables.append(name)
    return printables

def node_name(filepath):
    """ guess the node name from a filepath """
    parts = filepath.split(os.path.sep)
    try:
        return parts[parts.index('nodes')+1]
    except ValueError:
        return filepath

def extract_node_name(path, ignore_missing_nodes=False):
    """extracts the token after the 'nodes'"""
    tokens = path.split(os.sep)
    last_nodes_index = -1
    for i, token in enumerate(tokens):
        if token == "nodes":
            last_nodes_index = i
    if last_nodes_index == -1:
        if ignore_missing_nodes:
            return path
        raise "path '%s' does not contain 'nodes' and " + \
                "is not a valid diag tarball, so cannot determine the node"  % path
    try:
        # we're interested in getting the token after nodes
        return tokens[last_nodes_index+1]
    except IndexError:
        raise "there is nothing after the 'nodes' entry of '%s'" % path

def bucketize(data, start, end, seconds=3600):
    """ split the data into time-based buckets determined by seconds.
    Expects data to be a dict of datetime keys with list values """
    if start is None:
        raise ValueError("pysper.util.bucketize cannot work without a start time")
    if end is None:
        raise ValueError("pysper.util.bucketize cannot work without an end time")
    interval = datetime.timedelta(seconds=seconds)
    numbuckets = int((end - start).total_seconds() / seconds)
    # a calendar of sorts, made up of the desired intervals
    grid = [start+n*interval for n in range(numbuckets+1)]
    if not grid:
        # bucket too big, throw everything in a single
        return {start: list(itertools.chain.from_iterable(data.values()))}
    # build with empty lists instead of defaultdict so we cover empty intervals
    buckets = dict((time, []) for time in grid)
    for time, values in sorted(data.items(), key=lambda t: t[0]):
        # find the closest period in the 'calendar' and put everything there
        idx = bisect.bisect(grid, time)
        buckets[grid[idx-1]].extend(values)
    return buckets

def write_underline(s):
    """write an underline for the listed string. useful for reports"""
    return "".join(["-" for x in range(len(s))])

def textbar(maximum, value, fill='-', length=20):
    """print a text bar scaled to length with value relative to maximum"""
    percent = value / maximum
    num = int(round(length * percent))
    ret = ''
    # pylint: disable=unused-variable
    for x in range(num):
        ret += fill
    return ret
