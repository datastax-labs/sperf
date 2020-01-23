# sperf statuslogger

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
                        csv list of stage prefixes to collect, or 'all' (default:
                        TPC/all/READ,TPC/all/WRITE,Gossip,Messaging,Compaction,MemtableFlush,Mutation,Read,Native)
  -st [START], --start [START]
                        start date/time to begin parsing
  -et [END], --end [END]
                        end date/time to stop parsing
  -dl DEBUG_LOG_PREFIX, --debug_log_prefix DEBUG_LOG_PREFIX
                        if debug.log in the diag tarball has an oddball name, can still look based on this prefix (default "debug.log")
  -sl SYSTEM_LOG_PREFIX, --system_log_prefix SYSTEM_LOG_PREFIX
                        if system.log in the diag tarball has an oddball name, can still look based on this prefix (default "system.log")
  -f FILES, --files FILES
                        comma separated file list to compare. Alternative to --diagdir
  -d DIAG_DIR, --diagdir DIAG_DIR
                        where the diag tarball directory is exported, should be where the nodes folder is located (default ".")
```
