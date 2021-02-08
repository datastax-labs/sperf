#sperf subcommands

documentation and options for each command

## sperf core

```
usage: sperf core [-h]
                  {bgrep,diag,gc,jarcheck,schema,slowquery,statuslogger} ...

optional arguments:
  -h, --help            show this help message and exit

DSE Core/Cassandra Commands:
  {bgrep,diag,gc,jarcheck,schema,slowquery,statuslogger}
    bgrep               search for custom regex and bucketize results
    diag                Generates a diagtarball report. DSE 5.0-6.8
    gc                  show gc info. provides time series of gc duration and
                        frequency
    jarcheck            Checks jar versions in output.logs. Supports tarballs
                        and files. DSE 5.0-6.8
    schema              Analyze schema for summary. DSE 5.0-6.8
    slowquery           Generates a report of slow queries in debug log. DSE
                        6.0-6.8. DEPRECATED use 'sperf core slowquery' instead
    statuslogger        Provides analysis of StatusLogger log lines. DSE
                        5.0-6.8
```

## sperf search

```
usage: sperf search [-h] {filtercache,queryscore} ...

optional arguments:
  -h, --help            show this help message and exit

Search Commands:
  {filtercache,queryscore}
    filtercache         Generates a report of filter cache evictions. DSE
                        Search 5.0.5+,5.1-6.7.
    queryscore          Tries to summarize queries in the debug log based on
                        score that attempts to estimate the relative potential
                        cost of queries. DSE Search 5.0-6.7
```

## sperf sysbottle

```
usage: sperf sysbottle [-h] [-c [CPU]] [-q [DISKQ]] [-d [DISKS]] [-i [IOWAIT]]
                       [-t [THROUGHPUT]]
                       file

positional arguments:
  file                  iostat file to generate report on

optional arguments:
  -h, --help            show this help message and exit
  -c [CPU], --cpu [CPU]
                        percentage cpu usage minus iowait% above this threshold is busy. Assumes hyperthreading is enabled (default 50)
  -q [DISKQ], --diskQ [DISKQ]
                        disk queue depth. above this threshold is considered busy. (default 1)
  -d [DISKS], --disks [DISKS]
                        comma separated list of disks to include in report, if no disks are provided then all found disks are included in report
  -i [IOWAIT], --iowait [IOWAIT]
                        percentage iowait above this threshold is marked as a busy disk (default 5)
  -t [THROUGHPUT], --throughput [THROUGHPUT]
                        percentage of total time where we consider a node 'busy' for bottleneck summary. Example by default (5.0%) if the CPU
                        and Disk are busy 5.0% of the total time measured then it is considered busy. (default 5)
```

## sperf ttop

```
usage: sperf ttop [-h] [-a] [-c] [-k [TOP_K]] [-st [START]] [-et [END]]
                  files [files ...]

positional arguments:
  files                 ttop file to generate report on

optional arguments:
  -h, --help            show this help message and exit
  -a, --alloc           show allocation instead of cpu
  -c, --collate         don't collate threads (default: true)
  -k [TOP_K], --top_k [TOP_K]
                        number of top threads to show (default all)
  -st [START], --start [START]
                        start date/time to begin parsing (format: YYYY-MM-DD hh:mm:ss,SSS)
  -et [END], --end [END]
                        end date/time to stop parsing (format: YYYY-MM-DD hh:mm:ss,SSS)
```

## sperf core bgrep

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
                        start date/time to begin parsing (format: YYYY-MM-DD hh:mm:ss,SSS)
  -et [END], --end [END]
                        end date/time to stop parsing (format: YYYY-MM-DD hh:mm:ss,SSS)
  -c, --case            case-sensitive search
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
```

## sperf core diag

```
usage: sperf core diag [-h] [-d DIAG_DIR] [-s SYSTEM_LOG_PREFIX]
                       [-l DEBUG_LOG_PREFIX] [-o OUTPUT_LOG_PREFIX]
                       [-n NODE_INFO_PREFIX] [-c CFSTATS_PREFIX]
                       [-b BLOCK_DEV_PREFIX]

optional arguments:
  -h, --help            show this help message and exit
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
  -s SYSTEM_LOG_PREFIX, --system_log_prefix SYSTEM_LOG_PREFIX
                        if system.log in the diag tarball has an oddball name, can still look based on this prefix (default "system.log")
  -l DEBUG_LOG_PREFIX, --debug_log_prefix DEBUG_LOG_PREFIX
                        if debug.log in the diag tarball has an oddball name, can still look based on this prefix (default "debug.log")
  -o OUTPUT_LOG_PREFIX, --output_log_prefix OUTPUT_LOG_PREFIX
                        if output.log in the diag tarball has an oddball name, can still look based on this prefix (default "output.log")
  -n NODE_INFO_PREFIX, --node_info_prefix NODE_INFO_PREFIX
                        if node_info.json in the diag tarball has an oddball name, can still look based on this prefix (default
                        "node_info.json")
  -c CFSTATS_PREFIX, --cfstats_prefix CFSTATS_PREFIX
                        if cfstats in the diag tarball has an oddball name, can still look based on this prefix (default "cfstats")
  -b BLOCK_DEV_PREFIX, --block_dev_prefix BLOCK_DEV_PREFIX
                        if blockdev_report in the diag tarball has an oddball name, can still look based on this prefix (default
                        "blockdev_report")
```

## sperf core gc

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
                        start date/time to begin parsing (format: YYYY-MM-DD hh:mm:ss,SSS)
  -et [END], --end [END]
                        end date/time to stop parsing (format: YYYY-MM-DD hh:mm:ss,SSS)
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
```

## sperf core jarcheck

```
usage: sperf core jarcheck [-h] [-f FILES] [-d DIAG_DIR] [-o]

optional arguments:
  -h, --help            show this help message and exit
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
  -o, --diffonly        only report on the jars that are different
```

## sperf core schema

```
usage: sperf core schema [-h] [-f FILES] [-d DIAG_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
```

## sperf core slowquery

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
                        start date/time to begin parsing (format: YYYY-MM-DD hh:mm:ss,SSS)
  -et [END], --end [END]
                        end date/time to stop parsing (format: YYYY-MM-DD hh:mm:ss,SSS)
```

## sperf core statuslogger

```
usage: sperf core statuslogger [-h] [-r [REPORTER]] [-s [STAGES]]
                               [-st [START]] [-et [END]]
                               [-dl DEBUG_LOG_PREFIX] [-sl SYSTEM_LOG_PREFIX]
                               [-f FILES] [-d DIAG_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -r [REPORTER], --reporter [REPORTER]
                        report to run, either summary or histogram (default summary)
  -s [STAGES], --stages [STAGES]
                        csv list of stage prefixes to collect, or 'all' (default: all)
  -st [START], --start [START]
                        start date/time to begin parsing (format: YYYY-MM-DD hh:mm:ss,SSS)
  -et [END], --end [END]
                        end date/time to stop parsing (format: YYYY-MM-DD hh:mm:ss,SSS)
  -dl DEBUG_LOG_PREFIX, --debug_log_prefix DEBUG_LOG_PREFIX
                        if debug.log in the diag tarball has an oddball name, can still look based on this prefix (default "debug.log")
  -sl SYSTEM_LOG_PREFIX, --system_log_prefix SYSTEM_LOG_PREFIX
                        if system.log in the diag tarball has an oddball name, can still look based on this prefix (default "system.log")
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
```

## sperf search filtercache

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
                        optional filter for log times to only look at logs after this time (format: YYYY-MM-DD hh:mm:ss,SSS)
  -b BEFORE, --before BEFORE
                        optional filter for log times to only look at logs before this time (format: YYYY-MM-DD hh:mm:ss,SSS)
```

## sperf search queryscore

```
usage: sperf search queryscore [-h] [-s SCORETHRESHOLD] [-t TOP] [-u]
                               [-l LOG_PREFIX] [-f FILES] [-d DIAG_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -s SCORETHRESHOLD, --scorethreshold SCORETHRESHOLD
                        The score threshold to list a 'bad query'
  -t TOP, --top TOP     show the top N worst queries by score.
  -u, --uniquereasons   show only queries with a unique score and combination of reasons.
  -l LOG_PREFIX, --log_prefix LOG_PREFIX
                        if debug.log in the diag tarball has a different, name, sperf can still look based on this prefix (default "debug.log")
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
```

