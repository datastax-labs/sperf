# sperf filtercache

```
usage: sperf search filtercache [-h] [-f FILES] [-d DIAG_DIR]
                                [-s SYSTEM_LOG_PREFIX] [-a AFTER] [-b BEFORE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
  -s SYSTEM_LOG_PREFIX, --system_log_prefix SYSTEM_LOG_PREFIX
                        if system.log in the diag tarball has a different, name, sperf can still look based on this prefix (default
                        "system.log")
  -a AFTER, --after AFTER
                        optional filter for log times to only look at logs after this time
  -b BEFORE, --before BEFORE
                        optional filter for log times to only look at logs before this time
```
