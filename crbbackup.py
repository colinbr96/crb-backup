import argparse
import logging

from src.backup import backup
from src.initialize import initialize
from src.restore import restore


def configure_logger(verbose):
    handler = logging.StreamHandler()
    handler.setFormatter(fmt=logging.Formatter("%(levelname)s: %(message)s"))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(level=logging.DEBUG if verbose else logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(prog="crbbackup.py")
    parser.add_argument("-v", "--verbose", action="store_true")

    sub_parsers = parser.add_subparsers(dest="action", required=True)

    init_parser = sub_parsers.add_parser("init")

    backup_parser = sub_parsers.add_parser("backup")
    backup_parser.add_argument("-p", "--profile", required=True)

    restore_parser = sub_parsers.add_parser("restore")
    restore_parser.add_argument("-f", "--file", required=True)

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    configure_logger(args.verbose)

    match args.action:
        case "init":
            initialize()
        case "backup":
            backup(args.profile)
        case "restore":
            restore(args.file)


if __name__ == "__main__":
    main()
