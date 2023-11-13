import glob
import json
import logging
import os
import sys
import textwrap
import zipfile
from datetime import datetime
from pathlib import Path

from src.profile import Profile
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


def backup(profile_name: str):
    profile = Profile.load(profile_name)
    files_to_backup, stats = get_files_to_backup(profile)

    if not files_to_backup:
        logging.error("No files to backup")
        sys.exit(1)

    zip_filename = archive_files(files_to_backup, profile)
    stats.dst_bytes = os.path.getsize(zip_filename)
    logging.info(stats)


def get_files_to_backup(profile: Profile) -> tuple[list[Path], BackupStats]:
    stats = BackupStats()
    files: list[Path] = []

    for source in profile.sources:
        stats.sources += 1

        if not source.exists():
            logging.warn(f"Source doesn't exist: {source}")
            stats.warnings += 1

        if source.is_dir():
            source = source / "**/*"

        for glob_file in glob.iglob(str(source), recursive=True):
            source = Path(glob_file)
            if source.is_file():
                files.append(source)
                stats.files += 1
                stats.src_bytes += source.stat().st_size

    return files, stats


def archive_files(files: list[Path], profile: Profile):
    now = datetime.now()
    zip_filename = f'{profile.name}-{now.strftime("%Y-%m-%dT%H-%M-%S")}.zip'
    zip_filename = os.path.join(profile.destination, zip_filename)
    logging.info(f"Creating backup archive: {zip_filename}")

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            arcname = path_to_drive_letter_dir(file)
            logging.debug(f"Adding: {arcname}")
            zipf.write(file, arcname)
        zipf.writestr("profile.json", json.dumps(profile.to_json()))

    return zip_filename
