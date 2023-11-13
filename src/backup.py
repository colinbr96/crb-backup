import glob
import json
import logging
import os
import sys
import textwrap
import zipfile
from datetime import datetime
from pathlib import Path

from src.profile import load_profile
from src.utils.formatting import format_bytes
from src.utils.paths import path_to_drive_letter_dir


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
            f"Input Size: {format_bytes(self.src_bytes)}\n"
            f"Output Size: {format_bytes(self.dst_bytes)}\n"
            f"Reduction: {(1 - (self.dst_bytes / self.src_bytes)) * 100:.2f}%\n"
            f"Warnings: {self.warnings}\n"
            f"Errors: {self.errors}"
        )
        return "Backup Stats:\n" + textwrap.indent(stats_msg, " " * 2)


def backup(profile_name):
    profile = load_profile(profile_name)
    stats = BackupStats()
    files_to_backup: list[Path] = []

    for source in profile["sources"]:
        stats.sources += 1
        path = Path(source)

        if not path.exists():
            logging.warn(f"Source doesn't exist: {path}")
            stats.warnings += 1

        if path.is_dir():
            path = Path(source + "/**/*")

        for glob_file in glob.iglob(str(path), recursive=True):
            path = Path(glob_file)
            if path.is_file():
                files_to_backup.append(path)
                stats.files += 1
                stats.src_bytes += path.stat().st_size

    if not files_to_backup:
        logging.error("No files to backup")
        sys.exit(1)

    now = datetime.now()
    zip_filename = f'{profile["name"]}-{now.strftime("%Y-%m-%dT%H-%M-%S")}.zip'
    zip_filename = os.path.join(profile["destination"], zip_filename)
    logging.info(f"Creating backup archive: {zip_filename}")

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_backup:
            arcname = path_to_drive_letter_dir(file)
            logging.debug(f"Adding: {arcname}")
            zipf.write(file, arcname)
        zipf.writestr("profile.json", json.dumps(profile, indent=2))

    stats.dst_bytes = os.path.getsize(zip_filename)
    logging.info(stats)
