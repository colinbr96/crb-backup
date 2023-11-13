import json
import logging
import os
import sys
from pathlib import Path

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
