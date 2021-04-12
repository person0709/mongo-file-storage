import functools
from pathlib import Path
from typing import Optional, List, Callable, Dict

import requests
from requests import Response
from requests.adapters import HTTPAdapter

from requests.packages.urllib3.util.retry import Retry
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from tqdm import tqdm
from urllib3.exceptions import HTTPError


def request_wrapper(func):
    """
    Wrapper for the requests. Handles the response depending on the response code
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response: Response = func(*args, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            detail = response.json()["detail"]
            if isinstance(detail, list):
                raise HTTPError(detail[0].get("msg"))
            raise HTTPError(detail)
    return wrapper


class ApiClient:
    def __init__(self):
        self.base_url = "http://fs-service.localhost/api"

        retry = Retry(total=3, status_forcelist=[500, 502, 504], backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        self.session = session

    @request_wrapper
    def create_user(self, email: str, username: str, password: str) -> Optional[Dict]:
        """
        Send create user request to user service
        Args:
            email: creating user's email
            username: creating users' username
            password: password to use for the account

        Returns:
            created user info in dict (parsed by request wrapper)
        """
        body = {
            "email": email,
            "username": username,
            "password": password
        }
        return self.session.post(url=self.base_url + "/users", json=body)

    @request_wrapper
    def get_token(self, email: str, password: str) -> Optional[Dict]:
        """
        Send token request to user service.
        Args:
            email: email to use for authentication
            password: password to use for authentication

        Returns:
            JWT token in a dict if authentication successful
            eg. {token_type: Bearer, access_token: <jwt_token>}
        """
        return self.session.post(url=self.base_url + "/auth/token", data={"username": email, "password": password})

    @request_wrapper
    def get_my_info(self, headers: dict) -> Optional[Dict]:
        """
        Get current user info from user service
        Args:
            headers: Authorization headers with JWT

        Returns:
            user info in a dict (parsed by request wrapper)
        """
        return self.session.get(url=self.base_url + "/users/my", headers=headers)

    @request_wrapper
    def get_file_list(self, limit: int, sort_by: str, desc: bool, headers: dict) -> Optional[Dict[str, List[Dict]]]:
        """
        Get a list of file metadata from user service
        Args:
            limit: max number of items to fetch
            sort_by: field to sort the list by
            desc: whether to sort the list in descending order
            headers: Authorization headers with JWT

        Returns:
            a list of file meta in a dict (parsed by request wrapper)
        """
        return self.session.get(url=self.base_url + "/files/list/", params={"limit": limit, "sort_by": sort_by, "desc": desc}, headers=headers)

    @request_wrapper
    def get_storage_used(self, headers: dict) -> Optional[Dict]:
        """
        Get the total storage usage of the current user
        Args:
            headers: Authorization headers with JWT

        Returns:
            Storage being used in bytes in dict (parsed by request wrapper) {storage_used: <num_in_bytes>}
        """
        return self.session.get(url=self.base_url + "/files/usage", headers=headers)

    @request_wrapper
    def upload_file(self, file: Path, headers: dict, progress_callback: Callable) -> Optional[Dict]:
        """
        Upload a file to file service
        Args:
            file: file in Path object
            headers: Authorization headers with JWT
            progress_callback: callback that prints the upload progress

        Returns:
            Uploaded file metadata in dict if successful (parsed by request wrapper)
        """
        encoder = MultipartEncoder(fields={"file": (file.name, file.open("rb"), None)})
        monitor = MultipartEncoderMonitor(encoder, progress_callback)
        headers["Content-Type"] = encoder.content_type
        return self.session.post(url=self.base_url + "/files/upload", data=monitor, headers=headers)

    @request_wrapper
    def delete_file(self, filename: str, headers: dict) -> Optional[Dict]:
        """
        Send a file delete request to file service
        Args:
            filename: name of the file to delete
            headers: Authorization headers with JWT

        Returns:
            Name of the file in dict if successful (parsed by request wrapper)
        """
        return self.session.delete(url=self.base_url + "/files", params={"filename": filename}, headers=headers)

    def download_file(self, filename: str, download_path: Path, headers: dict) -> None:
        response = self.session.get(url=self.base_url + "/files", params={"filename": filename}, headers=headers)
        if response.status_code == 404:
            raise HTTPError("File does not exist!")
        with self.session.get(url=self.base_url + "/files/download", params={"filename": filename}, headers=headers, stream=True) as r:
            with tqdm(total=int(r.headers.get("content-length")), unit_scale=True, unit="B", dynamic_ncols=True) as bar:
                with download_path.open("wb") as f:
                    for chunk in r.iter_content(1000):
                        f.write(chunk)
                        bar.update(len(chunk))
