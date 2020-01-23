# sperf diag

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
