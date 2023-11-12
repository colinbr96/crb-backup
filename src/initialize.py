import re
import sys

from src.profile import create_profile


PROFILE_REGEX = "^[A-Za-z0-9_\-]+$"


def initialize():
    try:
        while True:
            profile = input("Create a profile name: ")
            if not re.fullmatch(PROFILE_REGEX, profile):
                print(f"Profile name must match {PROFILE_REGEX}")
            else:
                break
    except KeyboardInterrupt:
        sys.exit(0)
    try:
        profile_filename = create_profile(profile)
    except FileExistsError:
        print(f'Error: Profile named "{profile}" already exists', file=sys.stderr)
        sys.exit(1)
    print(f"Profile created at: {profile_filename}")
    print("Edit it to configure your backups.")
