#!/usr/bin/env python

with open("CHANGELOG.TXT", "r") as c:
    with open("./pysper/changelog.py", "w") as w:
        w.write('CHANGES = """\n')
        for l in c:
            w.write(l.strip() + "\n")
        w.write('"""\n')
        w.flush()
