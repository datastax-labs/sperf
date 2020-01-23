# sperf ttop

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
                        start date/time to begin parsing
  -et [END], --end [END]
                        end date/time to stop parsing
```
