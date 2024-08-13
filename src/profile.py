import json
import logging
import os
import re
import sys
from pathlib import Path


PROFILE_REGEX = "^[A-Za-z0-9_\-]+$"
SERIALIZATION_VERSION = 1


class Profile:
    def __init__(self, name: str, destination: Path, sources: list[Path] = []):
        self.name = name
        self.destination: Path = destination
        self.sources: list[Path] = sources

    def save(self) -> str:
        obj = self.to_json()
        os.makedirs("profiles", exist_ok=True)
        filename = f"profiles/{self.name}.json"
        if os.path.exists(filename):
            raise FileExistsError(f"Profile {self.name} already exists")
        with open(filename, "w") as f:
            json.dump(obj, f, indent=2)
        return filename

    def to_json(self):
        return {
            "version": SERIALIZATION_VERSION,
            "name": self.name,
            "sources": [str(source) for source in self.sources],
            "destination": str(self.destination),
        }

    @classmethod
    def from_json(cls, data: dict):
        version = data["version"]

        # TODO: Check version # and alter serialization behavior
        if version != SERIALIZATION_VERSION:
            raise ValueError(f"Unsupported serialization version: {version}")

        name = data["name"]
        destination = Path(data["destination"])
        sources = [Path(source) for source in data["sources"]]
        return cls(name, destination, sources)

    @classmethod
    def load(cls, name: str) -> "Profile":
        filename = f"profiles/{name}.json"
        try:
            with open(filename, "r") as f:
                obj = json.load(f)
        except FileNotFoundError:
            logging.error(f"Profile {name} not found")
            sys.exit(1)

        # TODO: Check version # and alter deserialization behavior
        profile = cls(
            obj["name"],
            Path(obj["destination"]),
            [Path(source) for source in obj["sources"]],
        )
        return profile


def _prompt_profile_name() -> str:
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


def _prompt_destination() -> Path:
    try:
        while True:
            destination = Path(input("Destination directory: "))
            if str(destination).startswith('~'):
                destination = destination.expanduser()
            if not destination.exists():
                logging.error(f"That directory does not exist")
            else:
                break
    except KeyboardInterrupt:
        sys.exit(0)
    return destination


def _create_profile(profile_name: str, destination: Path):
    try:
        profile = Profile(profile_name, destination)
        profile_filename = profile.save()
    except FileExistsError:
        print(f'Error: Profile named "{profile_name}" already exists', file=sys.stderr)
        sys.exit(1)
    print(f"Profile created at: {profile_filename}")
    print("Edit it to add backup sources.")


def _add_profile():
    profile_name = _prompt_profile_name()
    destination = _prompt_destination()
    _create_profile(profile_name, destination)


def profile_command(args):
    match args.profile_action:
        case "add":
            _add_profile()
        # TODO handle edit/remove
