# sperf slowquery

```
usage: sperf core slowquery [-h] [-f FILES] [-d DIAG_DIR] [-i [INTERVAL]]
                            [-t [TOP]] [-st [START]] [-et [END]]

optional arguments:
  -h, --help            show this help message and exit
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
  -i [INTERVAL], --interval [INTERVAL]
                        interval to report on in seconds (default 3600)
  -t [TOP], --top [TOP]
                        number of top queries to show (default 3)
  -st [START], --start [START]
                        start date/time to begin parsing
  -et [END], --end [END]
                        end date/time to stop parsing
```
