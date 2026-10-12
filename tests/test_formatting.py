import pytest

from src.utils.formatting import format_bytes


@pytest.mark.parametrize(
    "num_bytes, expected",
    [
        (0, "0.0 B"),
        (1, "1.0 B"),
        (1023, "1023.0 B"),
        (1024, "1.0 KiB"),
        (1536, "1.5 KiB"),
        (1024**2, "1.0 MiB"),
        (1024**3 * 5, "5.0 GiB"),
        (1024**4, "1.0 TiB"),
        (-2048, "-2.0 KiB"),
    ],
)
def test_format_bytes(num_bytes, expected):
    assert format_bytes(num_bytes) == expected


def test_format_bytes_beyond_zebibytes_uses_yobibytes():
    assert format_bytes(1024**8) == "1.0 YiB"


def test_format_bytes_custom_suffix():
    assert format_bytes(2048, suffix="b") == "2.0 Kib"
