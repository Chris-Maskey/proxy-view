"""Smoke test — verify test infrastructure works."""

from proxy_view import __version__


def test_version():
    assert __version__ == "0.1.0"
