import argparse

from src.backup import backup
from src.initialize import initialize


def parse_args():
    parser = argparse.ArgumentParser(prog='CRB Backup')
    sub_parsers = parser.add_subparsers(dest='action')

    init_parser = sub_parsers.add_parser('init')

    backup_parser = sub_parsers.add_parser('backup')
    backup_parser.add_argument('-p', '--profile', required=True)

    restore_parser = sub_parsers.add_parser('restore')
    restore_parser.add_argument('-p', '--profile', required=True)

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    match args.action:
        case 'init':
            initialize()
        case 'backup':
            backup(args.profile)
        case 'restore':
            print('Restore is not currently implemented. Please check back later.')


if __name__ == '__main__':
    main()
