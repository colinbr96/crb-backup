import csv
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
from src.utils.paths import absolute_path_to_relative_path, should_ignore_file


class BackupStats:
    sources = 0  # Number of sources seen
    ignored_sources = 0  # Number of ignored sources seen
    files = 0  # Number of files backed up
    ignored_files = 0  # Number of files backed up
    src_bytes = 0  # Number of source bytes backed up
    dst_bytes = 0  # Number of bytes backed up after compression
    warnings = 0  # Number of warnings
    errors = 0  # Number of errors

    def __str__(self):
        reduction = 0
        if self.src_bytes > 0:
            reduction = (1 - (self.dst_bytes / self.src_bytes)) * 100

        stats_msg = (
            f"Sources: {self.sources}\n"
            f"Ignore List: {self.ignored_sources}\n"
            f"Files: {self.files}\n"
            f"Ignored Files: {self.ignored_files}\n"
            f"Input Size: {format_bytes(self.src_bytes)}\n"
            f"Output Size: {format_bytes(self.dst_bytes)}\n"
            f"Reduction: {reduction:.2f}%\n"
            f"Warnings: {self.warnings}\n"
            f"Errors: {self.errors}"
        )
        return "Backup Stats:\n" + textwrap.indent(stats_msg, " " * 2)


def backup_command(profile_name: str, output_csv: bool):
    start_time = datetime.now()
    profile = Profile.load(profile_name)
    files_to_backup, stats = _get_files_to_backup(profile)

    if not files_to_backup:
        stats.errors += 1
        logging.info(stats)
        logging.error("No files to backup")
        sys.exit(1)

    zip_filename = _archive_files(start_time, files_to_backup, profile)
    stats.dst_bytes = os.path.getsize(zip_filename)
    logging.info(stats)

    if output_csv:
        _write_csv_output(start_time, files_to_backup, profile)


def _get_files_to_backup(profile: Profile) -> tuple[list[Path], BackupStats]:
    stats = BackupStats()
    files: list[Path] = []
    stats.ignored_sources = len(profile.ignore_list)

    for source in profile.sources:
        stats.sources += 1

        # Filter ignore list to only those that fall within this source
        relevant_ignore_list = [
            ignored
            for ignored in profile.ignore_list
            if source == ignored
            or source in ignored.parents
            or ignored in source.parents
            or not ignored.is_dir()
        ]

        if source.is_dir():
            source = source / "**/*"

        for glob_file in glob.iglob(str(source), recursive=True):
            glob_path = Path(glob_file)
            if glob_path.is_file():
                if should_ignore_file(glob_path, relevant_ignore_list):
                    logging.debug(f"Ignoring: {glob_path}")
                    stats.ignored_files += 1
                else:
                    files.append(glob_path)
                    stats.files += 1
                    stats.src_bytes += glob_path.stat().st_size

    return files, stats


def _archive_files(date: datetime, files: list[Path], profile: Profile):
    zip_filename = f'{profile.name}-{date.strftime("%Y-%m-%dT%H-%M-%S")}.zip'
    zip_filename = os.path.join(profile.destination, zip_filename)
    logging.info(f"Creating backup archive: {zip_filename}")

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as f:
        for file in files:
            dst_path = absolute_path_to_relative_path(file)
            logging.debug(f"Saving: {dst_path}")
            f.write(file, dst_path)
        f.writestr("profile.json", json.dumps(profile.to_json()))

    return zip_filename


def _write_csv_output(date: datetime, files: list[Path], profile: Profile):
    csv_filename = f'{profile.name}-{date.strftime("%Y-%m-%dT%H-%M-%S")}.csv'
    csv_filename = os.path.join(profile.destination, csv_filename)
    logging.info(f"Creating backup file list CSV: {csv_filename}")

    with open(csv_filename, "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["Source", "Bytes"])
        for file in files:
            csv_writer.writerow(
                [str(file), file.stat().st_size if not file.is_dir() else 0]
            )

    return csv_filename
