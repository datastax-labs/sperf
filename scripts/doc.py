#!/usr/bin/env python
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
"""doc.py runs each sperf subcommand with the
-h flag and then writes the result out to markdown files"""
import os
import re
import glob
import subprocess

def get_subcommands(cmd, extra=None):
    """run the command listed and extract all subcommands"""
    output = ""
    if extra:
        output = subprocess.run([cmd, extra, '-h'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    else:
        output = subprocess.run([cmd, '-h'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    commands = []
    for line in output.split("\n"):
        result = re.match(r"^    (?P<command>\S+) *", line)
        if not result:
            continue
        commands.append(result.group("command"))
    return commands

def write_output(cmd, subcommand, target_file, extra=None):
    """runs -h on the command listed and writes a file of the same name out to the directory"""
    output = ""
    if extra:
        output = subprocess.run([cmd, extra, subcommand, '-h'],
                stdout=subprocess.PIPE).stdout.decode('utf-8')
    else:
        output = subprocess.run([cmd, subcommand, '-h'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    with open(target_file, "a") as file_desc:
        file_desc.write("## sperf %s" % os.path.basename(subcommand))
        file_desc.write("\n\n")
        file_desc.write("```\n")
        file_desc.write(output)
        file_desc.write("```\n\n")

if __name__ == "__main__":
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    DOC_FILE = os.path.join(CURRENT_DIR, "..", "docs", "commands", "index.md")
    if os.path.isfile(DOC_FILE):
        os.remove(DOC_FILE)
    with open(DOC_FILE, 'w') as f:
        f.write("#sperf subcommands\n\n")
        f.write("documentation and options for each command\n\n")
    print("removed existing docs")
    for command in get_subcommands(os.path.join(CURRENT_DIR, "sperf")):
        write_output(os.path.join(CURRENT_DIR, "sperf"), command, DOC_FILE)
        print("doc for %s generated" % command)
    for command in get_subcommands(os.path.join(CURRENT_DIR, "sperf"), "core"):
        write_output(os.path.join(CURRENT_DIR, "sperf"), command,
                     DOC_FILE, "core")
        print("doc for core %s generated" % command)
    for command in get_subcommands(os.path.join(CURRENT_DIR, "sperf"), "search"):
        write_output(os.path.join(CURRENT_DIR, "sperf"), command,
                     DOC_FILE, "search")
        print("doc for search %s generated" % command)
