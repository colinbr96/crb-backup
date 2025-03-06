import argparse
import logging

from src.backup import backup_command
from src.profile import profile_command
from src.restore import restore_command


APP_VERSION = "0.2"


def configure_logger(verbose):
    handler = logging.StreamHandler()
    handler.setFormatter(fmt=logging.Formatter("%(levelname)s: %(message)s"))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(level=logging.DEBUG if verbose else logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(prog="crbbackup.py")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {APP_VERSION}")
    parser.add_argument("-vv", "--verbose", action="store_true")

    action_parsers = parser.add_subparsers(dest="action", required=True)

    backup_parser = action_parsers.add_parser("backup")
    backup_parser.add_argument("-p", "--profile", required=True)

    restore_parser = action_parsers.add_parser("restore")
    restore_parser.add_argument("-f", "--file", required=True)

    profile_parser = action_parsers.add_parser("profile")
    profile_action_parsers = profile_parser.add_subparsers(dest="profile_action", required=True)

    profile_action_parsers.add_parser("add")
    # profile_edit_parser = profile_action_parsers.add_parser("edit")
    # profile_remove_parser = profile_action_parsers.add_parser("remove")

    # profile_edit_parser.add_argument("-p", "--profile", required=True)
    # profile_remove_parser.add_argument("-p", "--profile", required=True)

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    configure_logger(args.verbose)

    match args.action:
        case "backup":
            backup_command(args.profile)
        case "restore":
            restore_command(args.file)
        case "profile":
            profile_command(args.profile_action)


if __name__ == "__main__":
    main()
