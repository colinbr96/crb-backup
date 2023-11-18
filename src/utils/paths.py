import os
from pathlib import Path


def absolute_path_to_relative_path(path: Path) -> Path:
    """
    Converts an absolute path into a relative path by converting the drive letter into a directory.
    This is useful for storing files from multiple drives in a single archive.

    E.g. the input "C:/Users/foo/bar.txt", returns "C/Users/foo/bar.txt"
    Notice the drive letter "C:" becomes the root directory "C"
    """
    return Path(path.drive.replace(":", "")) / path.relative_to(path.anchor)


def relative_path_to_absolute_path(path: Path):
    """
    Converts a relative path into an absolute path by converting the root directory into the drive letter.

    E.g. the input "C/Users/foo/bar.txt", returns "C:/Users/foo/bar.txt"
    Notice the root directory "C" becomes the drive letter "C:"
    """
    root, *rest_of_path = path.parts
    return Path(root + ":" + os.path.sep) / Path(*rest_of_path)
