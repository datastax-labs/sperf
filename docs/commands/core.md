# sperf core

```
usage: sperf core [-h]
                  {bgrep,diag,gc,jarcheck,schema,slowquery,statuslogger} ...

optional arguments:
  -h, --help            show this help message and exit

DSE Core/Cassandra Commands:
  {bgrep,diag,gc,jarcheck,schema,slowquery,statuslogger}
    bgrep               search for custom regex and bucketize results
    diag                Generates a diagtarball report. DSE 5.0-6.7
    gc                  show gc info. provides time series of gc duration and
                        frequency
    jarcheck            Checks jar versions in output.logs. Supports tarballs
                        and files. DSE 5.0-6.7
    schema              Analyze schema for summary. DSE 5.0-6.7
    slowquery           Generates a report of slow queries in debug log. DSE
                        6.0-6.7. DEPRECATED use 'sperf core slowquery' instead
    statuslogger        Provides analysis of StatusLogger log lines. DSE
                        5.0-6.7
```
