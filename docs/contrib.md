# Contributing

1. Make sure you have Go 1.15 or greater.
2. run `git clone git@github.com:DataStax-Toolkit/sperf.git`
3. run `cd sperf`
4. run `make build`
5. run `./bin/sperf -h` and you should see the help for `sperf`

## Testing and validation

1. run `make test`
2. run `make lint`

## CI Server

This is done using GitHub actions are are located [here](https://github.com/DataStax-Toolkit/sperf/tree/master/.github/workflows) and automatically run
tests on Windows, Mac and Linux

## Creating a binary

### Manually

If you want to test the project or create a binary just out of your local work run the script `make build` which
will generate a binary ready for use on your platform.

### Automatically and Creating a Release

Releases are created when a tag starting with v is created. Watch the jobs progress in [GitHub Actions](https://github.com/DataStax-Toolkit/sperf/actions) and if it succeeds, 
it is safe to go ahead and move the release from draft status to public. See directions on how [to publish releases on GitHub](https://docs.github.com/en/github/administering-a-repository/managing-releases-in-a-repository)

Note until you publish the release, the binaries created will not be publicly available.
If you need to change the behavior of the release go ahead and edit [the release workflow file](https://github.com/DataStax-Toolkit/sperf/blob/master/.github/workflows/pythonrelease.yml)

## Regenerating the command documentation

The `docs/command.md` is generated from the latest help and is not automatically checked in. To regenerate run `python scripts/doc.py`

This will run against each command and subcommand and generate an entry in the `commands.md` file. This step must
be done manually or else the help files in the command line tool will get out of sync with the website.
