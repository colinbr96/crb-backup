import logging
import os
import re
import sys

from src.profile import create_profile

PROFILE_REGEX = "^[A-Za-z0-9_\-]+$"


def initialize():
    try:
        while True:
            profile_name = input("Create a profile name: ")
            if not re.fullmatch(PROFILE_REGEX, profile_name):
                logging.error(f"Profile name must match {PROFILE_REGEX}")
            else:
                break
        while True:
            destination = input("Destination directory: ")
            if not os.path.isdir(destination):
                logging.error(f"That directory does not exist")
            else:
                break
    except KeyboardInterrupt:
        sys.exit(0)
    try:
        profile_filename = create_profile(profile_name, destination)
    except FileExistsError:
        print(f'Error: Profile named "{profile_name}" already exists', file=sys.stderr)
        sys.exit(1)
    print(f"Profile created at: {profile_filename}")
    print("Edit it to add backup sources.")
