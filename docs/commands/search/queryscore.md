# sperf queryscore

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
