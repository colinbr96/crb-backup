import logging
import re
import sys
from pathlib import Path

from src.profile import Profile

PROFILE_REGEX = "^[A-Za-z0-9_\-]+$"


def prompt_profile_name() -> str:
    try:
        while True:
            profile_name = input("Create a profile name: ")
            if not re.fullmatch(PROFILE_REGEX, profile_name):
                logging.error(f"Profile name must match {PROFILE_REGEX}")
            else:
                break
    except KeyboardInterrupt:
        sys.exit(0)
    return profile_name


def prompt_destination() -> Path:
    try:
        while True:
            destination = Path(input("Destination directory: "))
            if not destination.exists():
                logging.error(f"That directory does not exist")
            else:
                break
    except KeyboardInterrupt:
        sys.exit(0)
    return destination


def create_profile(profile_name: str, destination: Path):
    try:
        profile = Profile(profile_name, destination)
        profile_filename = profile.save()
    except FileExistsError:
        print(f'Error: Profile named "{profile_name}" already exists', file=sys.stderr)
        sys.exit(1)
    print(f"Profile created at: {profile_filename}")
    print("Edit it to add backup sources.")


def initialize():
    profile_name = prompt_profile_name()
    destination = prompt_destination()
    create_profile(profile_name, destination)
