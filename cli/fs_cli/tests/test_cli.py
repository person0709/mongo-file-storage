import os
import pwd
from pathlib import Path

from urllib3.exceptions import HTTPError

from click.testing import CliRunner
from fs_cli.api_client import ApiClient
from fs_cli.cli import signup, login, logout


def test_signup_success(monkeypatch):
    monkeypatch.setattr(ApiClient, "create_user", lambda *args, **kwargs: {"username": "user"})
    runner = CliRunner()
    result = runner.invoke(
        signup,
        input="aaaa\n"  # email
              "aaaa\n"  # username
              "aaaa\n"  # password
              "aaaa\n"  # password confirm
    )
    assert "Sign-up successful" in result.output


def test_signup_password_reenter(monkeypatch):
    monkeypatch.setattr(ApiClient, "create_user", lambda *args, **kwargs: {"username": "user"})
    runner = CliRunner()
    result = runner.invoke(
        signup,
        input="aaaa\n"  # email
              "aaaa\n"  # username
              "aaaa\n"  # password
              "aaaaa\n"  # password confirm
              "aaaa\n"  # re-attempt due to mismatch
              "aaaa\n"  # password confirm
    )
    assert "Sign-up successful" in result.output


def test_signup_fail(monkeypatch):
    def error(*args, **kwargs):
        raise HTTPError("Something horrible happened")

    monkeypatch.setattr(ApiClient, "create_user", error)
    runner = CliRunner()
    result = runner.invoke(
        signup,
        input="aaaa\n"  # email
              "aaaa\n"  # username
              "aaaa\n"  # password
              "aaaa\n"  # password confirm
    )
    assert "ERROR!" in result.output


def test_login_success(monkeypatch):
    monkeypatch.setattr(ApiClient, "get_token", lambda *args, **kwargs: {"access_token": "jwt_token"})
    runner = CliRunner()
    result = runner.invoke(
        login,
        input="email\n"
              "password\n"
    )
    token_file = Path("/home") / pwd.getpwuid(os.getuid()).pw_name / ".files"
    assert token_file.is_file()
    assert "Login successful!" in result.output
    token_file.unlink()


def test_login_fail(monkeypatch):
    def error(*args, **kwargs):
        raise HTTPError("Something horrible happened")

    monkeypatch.setattr(ApiClient, "get_token", error)
    runner = CliRunner()
    result = runner.invoke(
        login,
        input="email\n"
              "password\n"
    )
    assert "ERROR!" in result.output


def test_logout_success(monkeypatch):
    monkeypatch.setattr(ApiClient, "get_token", lambda *args, **kwargs: {"access_token": "jwt_token"})
    runner = CliRunner()
    result = runner.invoke(
        login,
        input="email\n"
              "password\n"
    )
    token_file = Path("/home") / pwd.getpwuid(os.getuid()).pw_name / ".files"
    assert token_file.is_file()
    assert "Login successful!" in result.output

    result = runner.invoke(logout)
    assert "Logout Successful!" in result.output


def test_logout_failed(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(logout)
    assert "Already logged out!" in result.output
