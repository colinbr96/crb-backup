from pathlib import Path


def path_to_drive_letter_dir(path: Path) -> str:
    """
    Converts an absolute path into a relative path by converting the drive letter into a containing directory. This is
    useful for storing files from multiple drives in a single archive.

    E.g. the input "C:/Users/foo/bar.txt", returns "C/Users/foo/bar.txt"
    Notice the drive letter "C:" becomes the containing directory "C"
    """
    return path.drive[:-1] + str(path)[len(path.drive) :]
