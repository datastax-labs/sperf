# sperf bgrep

```
usage: sperf core bgrep [-h] [-i [INTERVAL]] [-st [START]] [-et [END]] [-c]
                        [-d DIAG_DIR] [-f FILES]
                        regex

positional arguments:
  regex                 regular expression to match

optional arguments:
  -h, --help            show this help message and exit
  -i [INTERVAL], --interval [INTERVAL]
                        interval to report on in seconds (default 3600)
  -st [START], --start [START]
                        start date/time to begin parsing
  -et [END], --end [END]
                        end date/time to stop parsing
  -c, --case            case-sensitive search
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
```
