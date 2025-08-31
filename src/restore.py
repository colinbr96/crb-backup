import hashlib
import json
import logging
import os
import tempfile
import zipfile
from pathlib import Path

from src.profile import Profile
from src.utils.paths import relative_path_to_absolute_path


def restore_command(zip_filename: str, overwrite: str):
    """
    Restore files from a backup zip file to their original locations.

    Args:
        zip_filename (str): The path to the backup zip file.
        overwrite (str): Overwrite behavior for existing files.
            "y" - Always overwrite
            "n" - Never overwrite
            "ask" - Ask before overwriting
    """
    assert overwrite in {"y", "n", "ask"}

    with tempfile.TemporaryDirectory(prefix="crb-restore_") as temp_dir:
        print(temp_dir)
        with zipfile.ZipFile(zip_filename, "r") as zipf:
            # Extract files from the zip to the temporary directory
            zipf.extractall(path=temp_dir)

            # Restore the profile from the zip
            profile_json = zipf.read("profile.json").decode("utf-8")
            profile_data = json.loads(profile_json)
            profile = Profile.from_json(profile_data)
            try:
                profile.save()
            except FileExistsError:
                logging.warning("Profile already exists, skipping its recovery")

            # Move files to their original locations
            for file_info in zipf.infolist():
                if not file_info.is_dir() and file_info.filename != "profile.json":
                    src_path = Path(temp_dir) / file_info.filename
                    dst_path = relative_path_to_absolute_path(Path(file_info.filename))

                    file_exists = os.path.exists(dst_path)
                    if file_exists:
                        if overwrite == "n":
                            logging.debug(f"Skipping existing file: {dst_path}")
                            continue

                        # Check if files are identical by comparing their hashes
                        src_hash = hashlib.sha256(src_path.read_bytes()).hexdigest()
                        dst_hash = hashlib.sha256(dst_path.read_bytes()).hexdigest()
                        if src_hash == dst_hash:
                            logging.debug(f"Skipping identical file: {dst_path}")
                            continue

                        # If overwrite is set to "ask", prompt the user for confirmation
                        if overwrite == "ask":
                            response = input(f"File {dst_path} already exists. Overwrite? (y/n): ").strip().lower()
                            if response != "y":
                                logging.debug(f"Declined to restore file: {dst_path}")
                                continue

                    file_status_str = "(new)" if not file_exists else "(overwritten)"
                    logging.debug(f"Restoring: {dst_path} {file_status_str}")
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    os.replace(src_path, dst_path)

    logging.info("Restore complete")
