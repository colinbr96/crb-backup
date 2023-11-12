import zipfile
import glob
import sys
from pathlib import Path
from datetime import datetime
import json
import logging
import os
import textwrap

from src.profile import load_profile
from src.utils.bytes import humanize_bytes


class BackupStats:
    sources = 0  # Number of sources seen
    files = 0  # Number of files backed up
    src_bytes = 0  # Number of source bytes backed up
    dst_bytes = 0  # Number of bytes backed up after compression
    warnings = 0  # Number of warnings
    errors = 0  # Number of errors

    def __str__(self):
        stats_msg = (
            f"Sources: {self.sources}\n"
            f"Files: {self.files}\n"
            f"Input Size: {humanize_bytes(self.src_bytes)}\n"
            f"Output Size: {humanize_bytes(self.dst_bytes)}\n"
            f"Reduction: {(1 - (self.dst_bytes / self.src_bytes)) * 100:.2f}%\n"
            f"Warnings: {self.warnings}\n"
            f"Errors: {self.errors}"
        )
        return "Backup Stats:\n" + textwrap.indent(stats_msg, " " * 2)


def backup(profile_name):
    profile = load_profile(profile_name)
    stats = BackupStats()
    files_to_backup = []

    for source in profile["sources"]:
        stats.sources += 1
        path = Path(source)

        if not path.exists():
            logging.warn(f"Source doesn't exist: {path}")
            stats.warnings += 1

        if path.is_dir():
            logging.debug(f"Dir: {path}")
            path = Path(source + "/**/*")

        for glob_file in glob.iglob(str(path), recursive=True):
            path = Path(glob_file)
            if path.is_file():
                logging.debug(f"File: {path}")
                files_to_backup.append(path)
                stats.files += 1
                stats.src_bytes += path.stat().st_size

    if not files_to_backup:
        logging.error("No files to backup")
        sys.exit(1)

    now = datetime.now()
    zip_filename = f'{profile["name"]}-{now.strftime("%Y-%m-%dT%H-%M-%S")}.zip'
    logging.info(f"Creating backup archive: {zip_filename}")

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_backup:
            zipf.write(file)
        zipf.writestr("profile.json", json.dumps(profile, indent=2))

    stats.dst_bytes = os.path.getsize(zip_filename)
    logging.info(stats)
