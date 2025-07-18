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

"""parses jars from the classpath and compares them"""
from pysper import env, diag, parser
from pysper.humanize import pluralize
from pysper.core import OrderedDefaultDict


class JarCheckParser:
    """class to parse and analyze the jars in the classpath of an outlog"""

    def __init__(self, diag_dir=None, files=None):
        self.diag_dir = diag_dir
        self.files = files
        self.analyzed = False
        self.jars = OrderedDefaultDict(int)
        self.files_analyzed = 0

    def analyze(self):
        error_if_file_not_found = False
        """ analyze log files """
        if self.files:
            error_if_file_not_found = True
            target = self.files
        elif self.diag_dir:
            target = diag.find_logs(self.diag_dir, "output.log")
        else:
            self.analyzed = True
            return
        for file in target:
            with diag.FileWithProgress(file) as log:
                if not log.file_desc and error_if_file_not_found:
                    raise FileNotFoundError(log.error)
                for event in parser.read_output_log(log):
                    if event["event_type"] == "classpath":
                        thisjars = OrderedDefaultDict(int)
                        for jar in event["classpath"].split(":"):
                            j = jar.split("/")[-1]
                            if j.endswith("jar"):
                                # to eliminate dupes within the same file, because java is crazy town
                                if j not in thisjars:
                                    thisjars[j] += 1
                                    self.jars[j] += 1
                self.files_analyzed += 1
        self.analyzed = True

    def print_report(self, diff_only=False):
        """print the report"""
        if not self.analyzed:
            self.analyze()
        if not self.files_analyzed:
            print("Nothing analyzed")
            return
        skewed = []
        common = []
        for jar in self.jars:
            if self.jars[jar] != self.files_analyzed:
                if jar not in skewed:
                    skewed.append((jar, self.jars[jar]))
            else:
                if jar not in common:
                    common.append((jar, self.jars[jar]))
        if not diff_only and common:
            print("Common jars")
            print("-" * 30)
            for jar in sorted(common):
                if env.DEBUG:
                    print(jar)
                else:
                    print(jar[0])
        if skewed:
            print()
            print("Inconsistent jars")
            print("-" * 30)
            for jar in sorted(skewed):
                if env.DEBUG:
                    print(jar)
                else:
                    print(jar[0])
        print()
        print("Analyzed", self.files_analyzed, pluralize(self.files_analyzed, "file"))
