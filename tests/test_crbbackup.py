from unittest import mock

import pytest

import crbbackup


@pytest.fixture
def argv(monkeypatch):
    def _set(*args):
        monkeypatch.setattr("sys.argv", ["crbbackup.py", *args])

    return _set


class TestParseArgs:
    def test_backup(self, argv):
        argv("backup", "-p", "mine")
        args = crbbackup.parse_args()
        assert args.action == "backup"
        assert args.profile == "mine"
        assert args.output_csv is False

    def test_backup_with_csv(self, argv):
        argv("backup", "--profile", "mine", "--output-csv")
        assert crbbackup.parse_args().output_csv is True

    def test_restore(self, argv):
        argv("restore", "-f", "file.zip", "--overwrite", "ask")
        args = crbbackup.parse_args()
        assert args.action == "restore"
        assert args.file == "file.zip"
        assert args.overwrite == "ask"

    def test_profile_add(self, argv):
        argv("profile", "add")
        args = crbbackup.parse_args()
        assert args.action == "profile"
        assert args.profile_action == "add"

    @pytest.mark.parametrize(
        "args",
        [
            [],
            ["backup"],
            ["restore", "-f", "file.zip"],
            ["restore", "-f", "file.zip", "--overwrite", "maybe"],
            ["profile"],
            ["unknown"],
        ],
    )
    def test_invalid_args_exit(self, argv, args):
        argv(*args)
        with pytest.raises(SystemExit) as exc_info:
            crbbackup.parse_args()
        assert exc_info.value.code == 2

    def test_version(self, argv, capsys):
        argv("--version")
        with pytest.raises(SystemExit) as exc_info:
            crbbackup.parse_args()
        assert exc_info.value.code == 0
        assert f"crbbackup.py {crbbackup.APP_VERSION}" in capsys.readouterr().out


class TestMain:
    @pytest.fixture(autouse=True)
    def no_logger_config(self, monkeypatch):
        monkeypatch.setattr(crbbackup, "configure_logger", lambda: None)

    def test_dispatches_backup(self, argv):
        argv("backup", "-p", "mine", "--output-csv")
        with mock.patch.object(crbbackup, "backup_command") as cmd:
            crbbackup.main()
        cmd.assert_called_once_with("mine", True)

    def test_dispatches_restore(self, argv):
        argv("restore", "-f", "file.zip", "--overwrite", "y")
        with mock.patch.object(crbbackup, "restore_command") as cmd:
            crbbackup.main()
        cmd.assert_called_once_with("file.zip", "y")

    def test_dispatches_profile(self, argv):
        argv("profile", "add")
        with mock.patch.object(crbbackup, "profile_command") as cmd:
            crbbackup.main()
        cmd.assert_called_once_with("add")

    def test_keyboard_interrupt_exits_with_1(self, argv):
        argv("profile", "add")
        with mock.patch.object(
            crbbackup, "profile_command", side_effect=KeyboardInterrupt
        ):
            with pytest.raises(SystemExit) as exc_info:
                crbbackup.main()
        assert exc_info.value.code == 1
