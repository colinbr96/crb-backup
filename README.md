# CRB Backup

## Installation

1. `git clone git@github.com:colinbr96/crb-backup.git`
2. `cd crb-backup/`
3. `python3 crbbackup.py init`

## How it works

### Backup

Example: `python3 crbbackup.py backup --profile <profile>`

Reads the configuration profile and copies all input files to the specified destination.

### Restore (WIP)

Example: `python3 crbbackup.py restore --file <file>`

Reads the configuration profile (stored in the backup file) and restores it to its original location.
