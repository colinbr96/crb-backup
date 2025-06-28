# CRB Backup

A Python CLI tool to create and execute filesystem backups

## Getting started

1. Install [Python 3.11](https://www.python.org/downloads/) or higher.
2. `git clone git@github.com:colinbr96/crb-backup.git`
3. `cd crb-backup/`
4. `python3 crbbackup.py profile add`
5. Enter a profile name and a destination folder. The destination is where the backup zip files will be created.
6. Edit the profile JSON file to add a list of `sources`. These are the folders that will be backed up. Feel free to use [glob](https://docs.python.org/3/library/glob.html) patterns to only match certain types of files/folders.

Example profile file:

```json
{
  "version": 1,
  "name": "my-backup",
  "sources": [
    "C:/Users/Colin/Saved Games/",
    "D:/Documents/**/*.pdf",
    "D:/Documents/**/*.docx"
  ],
  "destination": "G:/Google Drive/Backups/CRB Backup/"
}
```

## Usage

### Profile management

Example: `python3 crbbackup.py profile add`

- Creates a new profile using interactive prompts.

### Backup

Example: `python3 crbbackup.py backup --profile <profile>`

- Reads the configuration profile and copies all input files to the specified destination.
- The profile file is included in the backup archive.
- To see a list of all files as they are backed up, use `crbbackup.py --verbose` or `-vv`
- To output a CSV with a list of all backed-up files, use `--output-csv` or `-o`

### Restore

Example: `python3 crbbackup.py restore --file <file>`

- Reads the backup zip file and restores the files to their original location.
- Also restores the profile if it is missing.

## Limitations

- You can only create full backups. Incremental & differential backups are not supported.
