import os
import pwd
from pathlib import Path

from faker import Faker

from click.testing import CliRunner
from fs_cli.cli import signup, login, logout, whoami, upload, list, delete, download


def test_signup_success():
    fake = Faker()
    password = fake.password()
    runner = CliRunner()
    result = runner.invoke(
        signup,
        input=f"{fake.email()}\n"  # email
        f"{fake.user_name()}\n"  # username
        f"{password}\n"  # password
        f"{password}\n",  # password confirm
    )
    assert "Sign-up successful" in result.output


def test_signup_password_reenter():
    fake = Faker()
    password = fake.password()
    runner = CliRunner()
    result = runner.invoke(
        signup,
        input=f"{fake.email()}\n"  # email
        f"{fake.user_name()}\n"  # username
        f"{password}\n"  # password
        f"{password}abcd\n"  # password confirm
        f"{password}\n"  # re-attempt due to mismatch
        f"{password}\n",  # password confirm
    )
    assert "Sign-up successful" in result.output


def test_signup_fail_same_email():
    fake = Faker()
    email = fake.email()
    password = fake.password()
    runner = CliRunner()
    # register user
    runner.invoke(
        signup,
        input=f"{email}\n"  # email
        f"{fake.user_name()}\n"  # username
        f"{password}\n"  # password
        f"{password}\n",  # password confirm
    )
    # try registering again with the same email
    result = runner.invoke(
        signup,
        input=f"{email}\n"  # email
        f"{fake.user_name()}\n"  # username
        f"{password}\n"  # password
        f"{password}\n",  # password confirm
    )
    assert "ERROR!" in result.output


def test_signup_fail_invalid_email():
    fake = Faker()
    password = fake.password()
    runner = CliRunner()
    # register user
    result = runner.invoke(
        signup,
        input=f"invalid\n"  # email
        f"{fake.user_name()}\n"  # username
        f"{password}\n"  # password
        f"{password}\n",  # password confirm
    )
    assert "ERROR!" in result.output


def test_login_success(register_and_login):
    result = register_and_login
    token_file = Path("/home") / pwd.getpwuid(os.getuid()).pw_name / ".files"
    assert token_file.is_file()
    assert "Login successful!" in result.output
    token_file.unlink()


def test_login_fail():
    runner = CliRunner()
    # try non-existent account
    result = runner.invoke(login, input="email\n" "password\n")
    assert "ERROR!" in result.output


def test_logout_success(register_and_login):
    runner = CliRunner()
    result = register_and_login
    token_file = Path("/home") / pwd.getpwuid(os.getuid()).pw_name / ".files"
    assert token_file.is_file()
    assert "Login successful!" in result.output

    result = runner.invoke(logout)
    assert "Logout Successful!" in result.output


def test_logout_failed():
    runner = CliRunner()
    result = runner.invoke(logout)
    assert "Already logged out!" in result.output


def test_whoami_success(register_and_login):
    runner = CliRunner()
    result = runner.invoke(whoami)
    assert "Username" in result.output


def test_whoami_failed():
    runner = CliRunner()
    runner.invoke(logout)
    # fails due to absence of token
    result = runner.invoke(whoami)
    assert result


def test_file_upload(register_and_login):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test_file.txt", mode="w") as f:
            f.write("This is a test file" * 100)
        result = runner.invoke(upload, args="test_file.txt")
        assert result.exit_code == 0
        assert "uploaded successfully" in result.output


def test_file_upload_fail_no_file(register_and_login):
    runner = CliRunner()
    result = runner.invoke(upload, args="non-existent-file")
    assert result.exit_code == 2


def test_file_list(register_and_login):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test_file.txt", mode="w") as f:
            f.write("This is a test file" * 100)
        runner.invoke(upload, args="test_file.txt")
        result = runner.invoke(list)
        assert result.exit_code == 0
        assert "test_file.txt" in result.output


def test_file_delete_success(register_and_login):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test_file.txt", mode="w") as f:
            f.write("This is a test file" * 100)
        # upload first
        runner.invoke(upload, args="test_file.txt")
        # check the file is uploaded
        result = runner.invoke(list)
        assert "test_file.txt" in result.output
        # send delete request
        result = runner.invoke(delete, args="test_file.txt")
        assert result.exit_code == 0
        assert "test_file.txt" in result.output
        # check file is not there anymore
        result = runner.invoke(list)
        assert "test_file.txt" not in result.output


def test_file_delete_fail_no_file(register_and_login):
    runner = CliRunner()
    result = runner.invoke(delete, args="non-existent-file")
    assert "ERROR!" in result.output


def test_file_download_success(register_and_login):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test_file.txt", mode="w") as f:
            f.write("This is a test file" * 100)
        # upload first
        runner.invoke(upload, args="test_file.txt")
        # check the file is uploaded
        result = runner.invoke(list)
        assert "test_file.txt" in result.output
        # delete file from current dir
        Path("test_file.txt").unlink()
        # download file
        runner.invoke(download, args=["test_file.txt"])
        # check downloaded file content
        with open("test_file.txt", mode="r") as f:
            assert "This is a test file" in f.read()


def test_file_download_with_dest_option(register_and_login):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test_file.txt", mode="w") as f:
            f.write("This is a test file" * 100)
        # upload first
        runner.invoke(upload, args="test_file.txt")
        # check the file is uploaded
        result = runner.invoke(list)
        assert "test_file.txt" in result.output
        # download file
        result = runner.invoke(download, args=["--dest", "test_file_download.txt", "test_file.txt"])
        # check downloaded file content
        with open("test_file_download.txt", mode="r") as f:
            assert "This is a test file" in f.read()
