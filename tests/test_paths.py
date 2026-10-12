from pathlib import Path

from src.utils.paths import (
    absolute_path_to_relative_path,
    relative_path_to_absolute_path,
    should_ignore_file,
)
from tests.conftest import windows_only


@windows_only
def test_absolute_path_to_relative_path():
    assert absolute_path_to_relative_path(Path("C:/Users/foo/bar.txt")) == Path(
        "C/Users/foo/bar.txt"
    )


@windows_only
def test_relative_path_to_absolute_path():
    assert relative_path_to_absolute_path(Path("D/Documents/a.pdf")) == Path(
        "D:/Documents/a.pdf"
    )


@windows_only
def test_path_conversion_round_trip(tmp_path):
    original = tmp_path / "nested" / "file.txt"
    relative = absolute_path_to_relative_path(original)
    assert not relative.is_absolute()
    assert relative_path_to_absolute_path(relative) == original


def test_should_ignore_file_empty_ignore_list(tmp_path):
    assert should_ignore_file(tmp_path / "a.txt", []) is False


def test_should_ignore_file_inside_ignored_directory(tmp_path):
    ignored_dir = tmp_path / "cache"
    ignored_dir.mkdir()
    assert should_ignore_file(ignored_dir / "deep" / "a.txt", [ignored_dir]) is True


def test_should_not_ignore_file_outside_ignored_directory(tmp_path):
    ignored_dir = tmp_path / "cache"
    ignored_dir.mkdir()
    assert should_ignore_file(tmp_path / "a.txt", [ignored_dir]) is False


def test_should_ignore_file_by_name(tmp_path):
    assert should_ignore_file(tmp_path / "sub" / "Thumbs.db", [Path("Thumbs.db")])


def test_should_not_ignore_file_with_different_name(tmp_path):
    assert should_ignore_file(tmp_path / "a.txt", [Path("b.txt")]) is False


def test_should_ignore_file_first_match_wins(tmp_path):
    ignored_dir = tmp_path / "cache"
    ignored_dir.mkdir()
    ignore_list = [ignored_dir, Path("other.txt")]
    assert should_ignore_file(ignored_dir / "a.txt", ignore_list) is True


def test_should_ignore_file_later_entry_matches(tmp_path):
    ignore_list = [Path("other.txt"), Path("a.txt")]
    assert should_ignore_file(tmp_path / "a.txt", ignore_list) is True
