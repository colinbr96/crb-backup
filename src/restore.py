import json
import logging
import os
import tempfile
import zipfile
from pathlib import Path

from src.profile import Profile
from src.utils.paths import relative_path_to_absolute_path


def restore_command(zip_filename: str):
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
                    exists_msg = (
                        "(overwrite)" if os.path.exists(dst_path) else "(missing)"
                    )
                    logging.debug(f"Restoring: {dst_path} {exists_msg}")
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    os.replace(src_path, dst_path)

    logging.info("Restore complete")
