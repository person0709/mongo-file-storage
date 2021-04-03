from enum import Enum


class Role(str, Enum):
    """
    Enum for representing the permission level of a user
    """
    ADMIN = "ADMIN"  # can view, upload and delete any files
    UPLOADER = "UPLOADER"  # can view, upload and delete only their files
    VIEWER = "VIEWER"  # can view only
