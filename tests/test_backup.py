import csv
import json
import zipfile
from datetime import datetime
from pathlib import Path

import pytest

from src.backup import (
    BackupStats,
    _archive_files,
    _check_dest_exists,
    _get_files_to_backup,
    _write_csv_output,
    backup_command,
)
from src.profile import Profile
from src.utils.paths import absolute_path_to_relative_path


@pytest.fixture
def source_tree(tmp_path):
    """
    src/
      a.txt
      d.log
      sub/b.txt
      skip/c.txt
    """
    src = tmp_path / "src"
    (src / "sub").mkdir(parents=True)
    (src / "skip").mkdir()
    (src / "a.txt").write_text("aaaa")
    (src / "d.log").write_text("dd")
    (src / "sub" / "b.txt").write_text("bbbbbb")
    (src / "skip" / "c.txt").write_text("c")
    return src


@pytest.fixture
def dest(tmp_path):
    path = tmp_path / "dest"
    path.mkdir()
    return path


def relative_names(paths, root):
    return sorted(p.relative_to(root).as_posix() for p in paths)


class TestBackupStats:
    def test_str_includes_reduction(self):
        stats = BackupStats()
        stats.sources = 2
        stats.files = 3
        stats.src_bytes = 1000
        stats.dst_bytes = 250
        text = str(stats)
        assert text.startswith("Backup Stats:\n")
        assert "  Sources: 2" in text
        assert "  Files: 3" in text
        assert "Reduction: 75.00%" in text

    def test_str_with_no_input_bytes(self):
        assert "Reduction: 0.00%" in str(BackupStats())

    def test_instances_do_not_share_counts(self):
        first = BackupStats()
        first.files += 5
        assert BackupStats().files == 0


def test_check_dest_exists_passes(dest):
    _check_dest_exists(Profile("p", dest))


def test_check_dest_exists_exits_when_missing(tmp_path, caplog):
    with pytest.raises(SystemExit) as exc_info:
        _check_dest_exists(Profile("p", tmp_path / "missing"))
    assert exc_info.value.code == 1
    assert "Destination folder does not exist" in caplog.text


class TestGetFilesToBackup:
    def test_directory_source_is_recursive(self, source_tree, dest):
        files, stats = _get_files_to_backup(Profile("p", dest, [source_tree], []))
        assert relative_names(files, source_tree) == [
            "a.txt",
            "d.log",
            "skip/c.txt",
            "sub/b.txt",
        ]
        assert stats.sources == 1
        assert stats.files == 4
        assert stats.ignored_files == 0
        assert stats.src_bytes == 4 + 2 + 6 + 1

    def test_ignored_directory_is_skipped(self, source_tree, dest):
        profile = Profile("p", dest, [source_tree], [source_tree / "skip"])
        files, stats = _get_files_to_backup(profile)
        assert relative_names(files, source_tree) == ["a.txt", "d.log", "sub/b.txt"]
        assert stats.ignored_sources == 1
        assert stats.ignored_files == 1

    def test_ignored_filename_is_skipped(self, source_tree, dest):
        profile = Profile("p", dest, [source_tree], [Path("d.log")])
        files, stats = _get_files_to_backup(profile)
        assert "d.log" not in relative_names(files, source_tree)
        assert stats.ignored_files == 1

    def test_ignored_directory_outside_source_has_no_effect(self, source_tree, tmp_path, dest):
        unrelated = tmp_path / "unrelated"
        unrelated.mkdir()
        files, stats = _get_files_to_backup(
            Profile("p", dest, [source_tree], [unrelated])
        )
        assert stats.files == 4
        assert stats.ignored_files == 0

    def test_glob_source(self, source_tree, dest):
        files, _ = _get_files_to_backup(
            Profile("p", dest, [source_tree / "**" / "*.txt"], [])
        )
        assert relative_names(files, source_tree) == ["a.txt", "skip/c.txt", "sub/b.txt"]

    def test_single_file_source(self, source_tree, dest):
        files, stats = _get_files_to_backup(
            Profile("p", dest, [source_tree / "a.txt"], [])
        )
        assert files == [source_tree / "a.txt"]
        assert stats.src_bytes == 4

    def test_multiple_sources(self, source_tree, dest):
        profile = Profile("p", dest, [source_tree / "a.txt", source_tree / "sub"], [])
        files, stats = _get_files_to_backup(profile)
        assert relative_names(files, source_tree) == ["a.txt", "sub/b.txt"]
        assert stats.sources == 2

    def test_missing_source_yields_nothing(self, tmp_path, dest):
        files, stats = _get_files_to_backup(Profile("p", dest, [tmp_path / "nope"], []))
        assert files == []
        assert stats.files == 0


def test_archive_files(source_tree, dest):
    profile = Profile("my-backup", dest, [source_tree], [])
    files = [source_tree / "a.txt", source_tree / "sub" / "b.txt"]
    date = datetime(2026, 1, 2, 3, 4, 5)

    zip_filename = _archive_files(date, files, profile)

    assert Path(zip_filename) == dest / "my-backup-2026-01-02T03-04-05.zip"
    with zipfile.ZipFile(zip_filename) as zf:
        expected = {absolute_path_to_relative_path(f).as_posix() for f in files}
        assert set(zf.namelist()) == expected | {"profile.json"}
        assert json.loads(zf.read("profile.json")) == profile.to_json()
        a_name = absolute_path_to_relative_path(files[0]).as_posix()
        assert zf.read(a_name) == b"aaaa"


def test_write_csv_output(source_tree, dest):
    profile = Profile("my-backup", dest, [source_tree], [])
    files = [source_tree / "a.txt", source_tree / "sub" / "b.txt"]
    date = datetime(2026, 1, 2, 3, 4, 5)

    csv_filename = _write_csv_output(date, files, profile)

    assert Path(csv_filename) == dest / "my-backup-2026-01-02T03-04-05.csv"
    with open(csv_filename, newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["Source", "Bytes", "Last Modified"]
    assert [row[:2] for row in rows[1:]] == [
        [str(files[0]), "4"],
        [str(files[1]), "6"],
    ]
    datetime.fromisoformat(rows[1][2])


class TestBackupCommand:
    def test_creates_archive(self, in_tmp_cwd, source_tree, dest):
        Profile("full", dest, [source_tree], []).save()
        backup_command("full", output_csv=False)
        assert len(list(dest.glob("full-*.zip"))) == 1
        assert list(dest.glob("*.csv")) == []

    def test_creates_csv_when_requested(self, in_tmp_cwd, source_tree, dest):
        Profile("full", dest, [source_tree], []).save()
        backup_command("full", output_csv=True)
        assert len(list(dest.glob("full-*.zip"))) == 1
        assert len(list(dest.glob("full-*.csv"))) == 1

    def test_exits_when_no_files(self, in_tmp_cwd, tmp_path, dest, caplog):
        empty = tmp_path / "empty"
        empty.mkdir()
        Profile("empty", dest, [empty], []).save()
        with pytest.raises(SystemExit) as exc_info:
            backup_command("empty", output_csv=False)
        assert exc_info.value.code == 1
        assert "No files to backup" in caplog.text
        assert list(dest.iterdir()) == []

    def test_exits_when_destination_missing(self, in_tmp_cwd, source_tree, tmp_path):
        Profile("nodest", tmp_path / "missing", [source_tree], []).save()
        with pytest.raises(SystemExit) as exc_info:
            backup_command("nodest", output_csv=False)
        assert exc_info.value.code == 1
