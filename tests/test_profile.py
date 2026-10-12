import json
import logging
from pathlib import Path

import pytest

from src.profile import (
    SERIALIZATION_VERSION,
    Profile,
    _create_profile,
    _prompt_destination,
    _prompt_profile_name,
    profile_command,
)


@pytest.fixture
def sample_profile(tmp_path):
    return Profile(
        "my-backup",
        tmp_path / "dest",
        [tmp_path / "src1", tmp_path / "src2"],
        [tmp_path / "src1" / "cache"],
    )


class TestSerialization:
    def test_to_json(self, sample_profile, tmp_path):
        assert sample_profile.to_json() == {
            "version": SERIALIZATION_VERSION,
            "name": "my-backup",
            "sources": [str(tmp_path / "src1"), str(tmp_path / "src2")],
            "ignore_list": [str(tmp_path / "src1" / "cache")],
            "destination": str(tmp_path / "dest"),
        }

    def test_to_json_is_json_serializable(self, sample_profile):
        json.dumps(sample_profile.to_json())

    def test_from_json(self, sample_profile):
        restored = Profile.from_json(sample_profile.to_json())
        assert restored.name == sample_profile.name
        assert restored.destination == sample_profile.destination
        assert restored.sources == sample_profile.sources

    @pytest.mark.xfail(reason="Bug: Profile.from_json drops ignore_list", strict=True)
    def test_from_json_preserves_ignore_list(self, sample_profile):
        restored = Profile.from_json(sample_profile.to_json())
        assert restored.ignore_list == sample_profile.ignore_list

    def test_from_json_rejects_unsupported_version(self, sample_profile):
        data = sample_profile.to_json()
        data["version"] = SERIALIZATION_VERSION + 1
        with pytest.raises(ValueError, match="Unsupported serialization version"):
            Profile.from_json(data)


@pytest.mark.xfail(
    reason="Bug: mutable default arguments are shared between Profile instances",
    strict=True,
)
def test_default_lists_are_not_shared(tmp_path):
    first = Profile("a", tmp_path)
    try:
        first.sources.append(Path("x"))
        first.ignore_list.append(Path("y"))
        second = Profile("b", tmp_path)
        assert second.sources == []
        assert second.ignore_list == []
    finally:
        # While the bug exists, these are the shared defaults; don't leak into other tests.
        first.sources.clear()
        first.ignore_list.clear()


class TestPersistence:
    def test_save_writes_profile_file(self, in_tmp_cwd, sample_profile):
        filename = sample_profile.save()
        assert filename == "profiles/my-backup.json"
        saved = json.loads((in_tmp_cwd / filename).read_text())
        assert saved == sample_profile.to_json()

    def test_save_refuses_to_overwrite(self, in_tmp_cwd, sample_profile):
        sample_profile.save()
        with pytest.raises(FileExistsError):
            sample_profile.save()

    def test_load_round_trip(self, in_tmp_cwd, sample_profile):
        sample_profile.save()
        loaded = Profile.load("my-backup")
        assert loaded.to_json() == sample_profile.to_json()

    def test_load_missing_profile_exits(self, in_tmp_cwd, caplog):
        with pytest.raises(SystemExit) as exc_info:
            Profile.load("does-not-exist")
        assert exc_info.value.code == 1
        assert "Profile does-not-exist not found" in caplog.text

    @pytest.mark.xfail(
        reason="Bug: Profile.load requires ignore_list, but the README example omits it",
        raises=KeyError,
        strict=True,
    )
    def test_load_profile_without_ignore_list(self, in_tmp_cwd, tmp_path):
        (in_tmp_cwd / "profiles").mkdir()
        (in_tmp_cwd / "profiles" / "readme.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "name": "readme",
                    "sources": [str(tmp_path)],
                    "destination": str(tmp_path),
                }
            )
        )
        assert Profile.load("readme").ignore_list == []


class TestPrompts:
    def test_prompt_profile_name_accepts_valid_name(self, fake_input):
        fake_input("my_backup-1")
        assert _prompt_profile_name() == "my_backup-1"

    @pytest.mark.parametrize("bad_name", ["", "has space", "slash/name", "dot.name"])
    def test_prompt_profile_name_reprompts_on_invalid(self, fake_input, caplog, bad_name):
        fake_input(bad_name, "good")
        assert _prompt_profile_name() == "good"
        assert "Profile name must match" in caplog.text

    def test_prompt_profile_name_ctrl_c_exits_cleanly(self, fake_input):
        fake_input(KeyboardInterrupt())
        with pytest.raises(SystemExit) as exc_info:
            _prompt_profile_name()
        assert exc_info.value.code == 0

    def test_prompt_destination_reprompts_until_exists(self, fake_input, tmp_path, caplog):
        fake_input(str(tmp_path / "missing"), str(tmp_path))
        assert _prompt_destination() == tmp_path
        assert "That directory does not exist" in caplog.text

    def test_prompt_destination_expands_home(self, fake_input, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        fake_input("~")
        assert _prompt_destination() == tmp_path

    def test_prompt_destination_ctrl_c_exits_cleanly(self, fake_input):
        fake_input(KeyboardInterrupt())
        with pytest.raises(SystemExit) as exc_info:
            _prompt_destination()
        assert exc_info.value.code == 0


class TestCreateProfile:
    def test_create_profile(self, in_tmp_cwd, capsys):
        _create_profile("new", in_tmp_cwd)
        assert (in_tmp_cwd / "profiles" / "new.json").exists()
        assert "Profile created at: profiles/new.json" in capsys.readouterr().out

    def test_create_duplicate_profile_exits(self, in_tmp_cwd, capsys):
        _create_profile("dup", in_tmp_cwd)
        with pytest.raises(SystemExit) as exc_info:
            _create_profile("dup", in_tmp_cwd)
        assert exc_info.value.code == 1
        assert 'Profile named "dup" already exists' in capsys.readouterr().err

    def test_profile_command_add(self, in_tmp_cwd, fake_input):
        fake_input("added", str(in_tmp_cwd))
        profile_command("add")
        saved = json.loads((in_tmp_cwd / "profiles" / "added.json").read_text())
        assert saved["name"] == "added"
        assert saved["destination"] == str(in_tmp_cwd)
        assert saved["sources"] == []
