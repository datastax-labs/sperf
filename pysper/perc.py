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
"""percentile implementations"""


class Stats:
    """Stats is an array wrapper that provides min, max and percentiles"""

    def __init__(self, data):
        """must do a sort on startup"""
        self.data = sorted(data)

    def max(self):
        """max gets the largest element"""
        return self.data[-1]

    def min(self):
        """max gets the smallest element"""
        return self.data[0]

    def percentile(self, percentile):
        """provides a naive implemenation of percentiles"""
        return self.data[int(len(self.data) * (percentile / 100.0))]
