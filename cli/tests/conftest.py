import pytest
from click.testing import CliRunner
from faker import Faker

from fs_cli.cli import signup, login


@pytest.fixture(scope="function")
def register_and_login():
    fake = Faker()
    email = fake.email()
    username = fake.user_name()
    password = fake.password()
    runner = CliRunner()
    # register user
    runner.invoke(
        signup,
        input=f"{email}\n"  # email
        f"{username}\n"  # username
        f"{password}\n"  # password
        f"{password}\n",  # password confirm
    )
    # login
    result = runner.invoke(login, input=f"{email}\n" f"{password}\n")
    yield result
