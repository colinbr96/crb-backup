import sys

import pytest


windows_only = pytest.mark.skipif(
    sys.platform != "win32", reason="Drive-letter path conversion is Windows-specific"
)


@pytest.fixture
def in_tmp_cwd(tmp_path, monkeypatch):
    """Run the test with a temporary working directory so profiles/ is isolated."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def fake_input(monkeypatch):
    """Feed a sequence of responses to builtins.input."""

    def _install(*responses):
        answers = iter(responses)

        def _input(prompt=""):
            answer = next(answers)
            if isinstance(answer, BaseException):
                raise answer
            return answer

        monkeypatch.setattr("builtins.input", _input)

    return _install


@pytest.fixture
def no_input(monkeypatch):
    """Fail the test if anything prompts the user."""

    def _input(prompt=""):
        raise AssertionError(f"Unexpected prompt: {prompt}")

    monkeypatch.setattr("builtins.input", _input)
