#!/usr/bin/env python

import os
dir_path = os.path.dirname(os.path.realpath(__file__))

with open(dir_path + "/../CHANGELOG.TXT", "r") as c:
    with open("./pysper/changelog.py", "w") as w:
        w.write('CHANGES = """\n')
        for l in c:
            w.write(l.strip() + "\n")
        w.write('"""\n')
        w.flush()
