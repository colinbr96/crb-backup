# CRB Backup

A Python CLI tool to create and execute filesystem backups

## Getting started

1. Install [Python 3.11](https://www.python.org/downloads/) or higher.
2. `git clone git@github.com:colinbr96/crb-backup.git`
3. `cd crb-backup/`
4. `python3 crbbackup.py init`
5. Enter a profile name and a destination folder. The destination is where the backup zip files will be created.
6. Edit the profile JSON file to add a list of `sources`. These are the folders that will be backed up. Feel free to use [glob](https://docs.python.org/3/library/glob.html) patterns to only match certain types of files/folders.

Example profile:

```json
// my-backup.json
{
  "version": 1,
  "name": "my-backup",
  "sources": [
    "C:/Users/Colin/Saved Games/",
    "D:/Documents/**/*.pdf",
    "D:/Documents/**/*.docx",
  ],
  "destination": "G:/Google Drive/Backups/CRB Backup/"
}
```

## Usage

### Backup

Example: `python3 crbbackup.py backup --profile <profile>`

- Reads the configuration profile and copies all input files to the specified destination.
- To see a list of all files as they are backed up, use `crbbackup.py --verbose` or `-v`

### Restore (WIP)

Example: `python3 crbbackup.py restore --file <file>`

- Reads the configuration profile (stored in the backup file) and restores it to its original location.

## Limitations

- Python 3 must be installed. Python 3.11 or higher is recommended.
- You can only create full backups. Incremental & differential backups are not supported.
- You need to manually specify the source directories in the profile JSON file.
