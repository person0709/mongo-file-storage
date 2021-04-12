import os
import pwd
from pathlib import Path

import click
from tqdm import tqdm

from .api_client import ApiClient
from urllib3.exceptions import HTTPError


class Environment:
    """
    Contains context that is shared among different commands
    """
    def __init__(self):
        self.api_base_url: str = "http://fs-service.localhost"
        self.token_file: Path = Path("/home") / pwd.getpwuid(os.getuid()).pw_name / ".files"
        self.token = None

        if self.token_file.exists():
            with self.token_file.open("r") as f:
                self.token = f.read()

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}


pass_environment = click.make_pass_decorator(Environment, ensure=True)


@click.group()
def cli():
    pass


@cli.command()
@pass_environment
def login(ctx: Environment):
    """
    Login to get authenticated
    """
    email = click.prompt("Enter your email address")
    password = click.prompt("Enter your password", hide_input=True)
    client = ApiClient()
    try:
        res = client.get_token(email, password)
        # save to a file for future requests
        with ctx.token_file.open("w") as f:
            f.write(res["access_token"])
        click.echo(f"Login successful!\n")
        click.echo("Now try `fs files upload` to upload your files.")
    except HTTPError as e:
        click.echo(f"ERROR! {e}")
        click.echo("If you don't have an account, sign up using `fs signup`")


@cli.command()
@pass_environment
def logout(ctx: Environment):
    """
    Logout and invalidate auth token
    """
    if ctx.token_file.is_file():
        ctx.token_file.unlink()
        click.echo("Logout Successful! Please login again to use the service.")
    else:
        click.echo("Already logged out!")


@cli.command()
def signup():
    """
    Sign up to create an account
    """
    email = click.prompt("Enter email address to register")
    username = click.prompt("Enter username to use")
    while True:
        password = click.prompt("Enter password", hide_input=True)
        confirm_password = click.prompt("Re-enter your password", hide_input=True)
        if password != confirm_password:
            click.echo("The passwords do not match. Try again")
            continue
        else:
            break

    client = ApiClient()
    try:
        response = client.create_user(email, username, password)
        click.echo(f"Sign-up successful. Welcome {response['username']}!\n")
        click.echo(f"Now please login using `fs login`.")
    except HTTPError as e:
        click.echo(f"ERROR! {e}")


@cli.command()
@pass_environment
def whoami(ctx: Environment):
    """
    Get my info
    """
    client = ApiClient()
    try:
        info = client.get_my_info(ctx.get_headers())
        res = client.get_storage_used(ctx.get_headers())
        click.echo(f"Username: {info['username']}")
        click.echo(f"Email: {info['email']}")
        click.echo(f"Role: {info['role']}")
        click.echo(f"Storage status: {res['storage_used'] / 1000 / 1000}MB/{info['storage_allowance'] / 1000 / 1000}MB")
    except HTTPError as e:
        click.echo(f"ERROR! {e}")


@cli.group()
def file():
    """
    Subcommand for file related operations.
    """
    pass


@file.command()
@click.option("-l", "--limit", default=10, type=int, help="Max number of file meta to get")
@click.option("-s", "--sort-by", default="uploaded_at", type=click.Choice(["uploaded_at", "filename", "size"], case_sensitive=False))
@click.option("--desc/--asc", default=True)
@pass_environment
def list(ctx: Environment, limit: int, sort_by: str, desc: bool):
    """
    Get list of files saved in the storage
    """
    client = ApiClient()
    try:
        res = client.get_file_list(limit, sort_by, desc, ctx.get_headers())
        for file in res["files"]:
            click.echo(file)
    except HTTPError as e:
        click.echo(f"ERROR! {e}")


@file.command()
@click.argument("file", type=click.Path(exists=True))
@pass_environment
def upload(ctx: Environment, file: str):
    """
    Uploads a file to the storage
    """
    client = ApiClient()
    with tqdm(total=Path(file).stat().st_size, unit_scale=True, unit="B", dynamic_ncols=True, delay=1) as bar:
        try:
            res = client.upload_file(Path(file), ctx.get_headers(), lambda x: bar.update(x.bytes_read - bar.n))
            click.echo(f"File {res['filename']} uploaded successfully")
        except HTTPError as e:
            click.echo(f"ERROR! {e}")


@file.command()
@click.argument("filename", type=str)
@pass_environment
def delete(ctx: Environment, filename: str):
    """
    Delete a file from the storage
    """
    client = ApiClient()
    try:
        res = client.delete_file(filename, ctx.get_headers())
        click.echo(f"File {res['filename']} deleted successfully")
    except HTTPError as e:
        click.echo(f"ERROR! {e}")


@file.command()
@click.argument("filename", type=str)
@click.option("-d", "--dest", type=click.Path(exists=False, dir_okay=True, file_okay=True, writable=True))
@pass_environment
def download(ctx: Environment, filename: str, dest: str):
    """
    Download a file from the storage
    """
    if not dest:
        dest = Path(os.getcwd()) / filename
    else:
        dest = Path(dest)
        if dest.is_dir():
            dest = dest / filename

    if dest.is_file():
        click.confirm(f"This will overwrite the existing file at {dest}. Continue?", abort=True)
    client = ApiClient()
    try:
        client.download_file(filename, dest, ctx.get_headers())
        click.echo(f"File {filename} downloaded at {dest.absolute()} successfully")
    except HTTPError as e:
        click.echo(f"ERROR! {e}")
