# from datetime import datetime
#
# import pytest
# from click.testing import CliRunner
# from jose import jwt
#
# def pytest_adoption(parser):
#     parser.addoption("--secret-key", action="store", default="super_secret_key")
#
#
# @pytest.fixture(scope="function")
# def viewer_claim():
#     return {
#         "sub": "viewer_id",
#         "exp": datetime.now(),
#         "role": "VIEWER",
#         "username": "viewer_name",
#         "email": "view@email.com"
#     }
#
#
# @pytest.fixture(scope="function")
# def login(pytestconfig, viewer_claim):
#     runner = CliRunner()
#     with runner.isolated_filesystem():
#         jwt.encode(viewer_claim, key=pytestconfig.getoption("secret-key"))