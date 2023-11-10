from zipfile import ZipFile
import glob
import sys
from pathlib import Path
from datetime import datetime
import json

from src.profile import load_profile


def backup(profile_name):
    profile = load_profile(profile_name)
    now = datetime.now()

    files_to_backup = []
    for source in profile['sources']:
        path = Path(source)
        if path.is_dir():
            print(f'D: {path}')
            path = Path(source + '/**/*')
        for glob_file in glob.iglob(str(path), recursive=True):
            path = Path(glob_file)
            if path.is_file():
                print(f'F: {path}')
                files_to_backup.append(path)

    if not files_to_backup:
        print('Error: No files to backup', file=sys.stderr)
        sys.exit(1)

    zip_filename = f'{profile["name"]}-{now.strftime("%Y-%m-%d-%H-%M-%S")}.zip'
    print(f'Writing backup archive: {zip_filename}')
    zip_file = ZipFile(zip_filename, 'w')
    for file in files_to_backup:
        zip_file.write(file)
    zip_file.writestr('profile.json', json.dumps(profile, indent=2))
