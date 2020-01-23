#!/usr/bin/env python
"""doc.py runs each sperf subcommand with the
-h flag and then writes the result out to markdown files"""
import os
import re
import glob
import subprocess

def remove_all(target_dir):
    """yank the existing docs"""
    filelist = glob.glob(os.path.join(target_dir, "*.md"))
    for file_path in filelist:
        os.remove(file_path)

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

def write_output(cmd, subcommand, target_dir, extra=None):
    """runs -h on the command listed and writes a file of the same name out to the directory"""
    output = ""
    if extra:
        output = subprocess.run([cmd, extra, subcommand, '-h'],
                stdout=subprocess.PIPE).stdout.decode('utf-8')
    else:
        output = subprocess.run([cmd, subcommand, '-h'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    with open(os.path.join(target_dir, os.path.basename(subcommand) + ".md"), "w") as file_desc:
        file_desc.write("# sperf %s" % os.path.basename(subcommand))
        file_desc.write("\n\n")
        file_desc.write("```\n")
        file_desc.write(output)
        file_desc.write("```\n")

if __name__ == "__main__":
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    DOC_DIR = os.path.join(CURRENT_DIR, "..", "docs", "commands")
    remove_all(DOC_DIR)
    print("removed existing docs")
    for command in get_subcommands(os.path.join(CURRENT_DIR, "sperf")):
        write_output(os.path.join(CURRENT_DIR, "sperf"), command, DOC_DIR)
        print("doc for %s generated" % command)
    for command in get_subcommands(os.path.join(CURRENT_DIR, "sperf"), "core"):
        write_output(os.path.join(CURRENT_DIR, "sperf"), command,
                     os.path.join(DOC_DIR, "core"), "core")
        print("doc for core %s generated" % command)
    for command in get_subcommands(os.path.join(CURRENT_DIR, "sperf"), "search"):
        write_output(os.path.join(CURRENT_DIR, "sperf"), command,
                     os.path.join(DOC_DIR, "search"), "search")
        print("doc for search %s generated" % command)
