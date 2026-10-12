import json
from datetime import datetime
from unittest import mock

import pytest

from src.backup import _archive_files
from src.profile import Profile
from src.restore import restore_command
from tests.conftest import windows_only

pytestmark = windows_only


@pytest.fixture
def backup(in_tmp_cwd, tmp_path):
    """
    Create a backup archive of two files, returning (zip_filename, files).
    Restore extracts files back to their original absolute paths, which are under tmp_path.
    """
    data = tmp_path / "data"
    (data / "sub").mkdir(parents=True)
    a = data / "a.txt"
    b = data / "sub" / "b.txt"
    a.write_text("original a")
    b.write_text("original b")

    dest = tmp_path / "dest"
    dest.mkdir()
    profile = Profile("restore-me", dest, [data], [])
    zip_filename = _archive_files(datetime(2026, 1, 1), [a, b], profile)
    return zip_filename, (a, b)


def test_restores_missing_files(backup, tmp_path, no_input):
    zip_filename, (a, b) = backup
    a.unlink()
    (tmp_path / "data" / "sub" / "b.txt").unlink()
    (tmp_path / "data" / "sub").rmdir()

    restore_command(zip_filename, "n")

    assert a.read_text() == "original a"
    assert b.read_text() == "original b"


def test_overwrite_n_keeps_existing_files(backup, no_input):
    zip_filename, (a, b) = backup
    a.write_text("modified a")

    restore_command(zip_filename, "n")

    assert a.read_text() == "modified a"
    assert b.read_text() == "original b"


def test_overwrite_y_replaces_existing_files(backup, no_input):
    zip_filename, (a, _) = backup
    a.write_text("modified a")

    restore_command(zip_filename, "y")

    assert a.read_text() == "original a"


def test_overwrite_ask_accepted(backup, fake_input):
    zip_filename, (a, _) = backup
    a.write_text("modified a")
    fake_input("y")

    restore_command(zip_filename, "ask")

    assert a.read_text() == "original a"


def test_overwrite_ask_declined(backup, fake_input):
    zip_filename, (a, _) = backup
    a.write_text("modified a")
    fake_input("n")

    restore_command(zip_filename, "ask")

    assert a.read_text() == "modified a"


def test_identical_files_are_not_prompted(backup, no_input):
    zip_filename, (a, b) = backup

    restore_command(zip_filename, "ask")

    assert a.read_text() == "original a"
    assert b.read_text() == "original b"


def test_overwrite_diff_shows_diff_then_asks(backup, fake_input):
    zip_filename, (a, _) = backup
    a.write_text("modified a")
    fake_input("y")

    with mock.patch("src.restore.subprocess.run") as run:
        restore_command(zip_filename, "diff")

    run.assert_called_once()
    args = run.call_args.args[0]
    assert args[:3] == ["diff", "--unified", "--color"]
    assert args[3] == a
    assert a.read_text() == "original a"


def test_restores_profile_when_missing(backup, in_tmp_cwd):
    zip_filename, _ = backup

    restore_command(zip_filename, "n")

    saved = json.loads((in_tmp_cwd / "profiles" / "restore-me.json").read_text())
    assert saved["name"] == "restore-me"


def test_keeps_existing_profile(backup, in_tmp_cwd, caplog):
    zip_filename, _ = backup
    profile_file = in_tmp_cwd / "profiles" / "restore-me.json"
    profile_file.parent.mkdir()
    profile_file.write_text("existing")

    restore_command(zip_filename, "n")

    assert profile_file.read_text() == "existing"
    assert "Profile already exists" in caplog.text


def test_rejects_invalid_overwrite_mode(backup):
    zip_filename, _ = backup
    with pytest.raises(AssertionError):
        restore_command(zip_filename, "maybe")
