import copy
import json
import os
import sys


DEFAULT_PROFILE = {"version": "1", "name": "", "sources": []}


def create_profile(name):
    profile = copy.deepcopy(DEFAULT_PROFILE)
    profile["name"] = name

    os.makedirs("profiles", exist_ok=True)
    filename = f"profiles/{name}.json"
    if os.path.exists(filename):
        raise FileExistsError(f"Profile {name} already exists")
    with open(filename, "w") as f:
        json.dump(profile, f, indent=2)
    return filename


def load_profile(name):
    filename = f"profiles/{name}.json"
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f'Error: Profile "{name}" not found', file=sys.stderr)
        sys.exit(1)
