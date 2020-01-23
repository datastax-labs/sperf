# sperf gc

```
usage: sperf core gc [-h] [-r [REPORTER]] [-i [INTERVAL]] [-k [TOP_K]]
                     [-st [START]] [-et [END]] [-d DIAG_DIR] [-f FILES]

optional arguments:
  -h, --help            show this help message and exit
  -r [REPORTER], --reporter [REPORTER]
                        report to run, either summary or nodes (default summary)
  -i [INTERVAL], --interval [INTERVAL]
                        interval to report on in seconds (default 3600)
  -k [TOP_K], --top-k [TOP_K]
                        top K worst GC events to show (default 3)
  -st [START], --start [START]
                        start date/time to begin parsing
  -et [END], --end [END]
                        end date/time to stop parsing
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
```
