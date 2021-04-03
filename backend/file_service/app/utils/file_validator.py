import os

from fastapi import UploadFile

from config import settings
from utils.exceptions import FileValidationError


def check_file(file: UploadFile) -> bool:
    """
    Check file to see if it passes all the validations.
    Args:
        file: file to check

    Returns:
        True if the file passes all validations, False if any fails
    """
    # only accept whitelisted file types
    ext = os.path.splitext(file.filename)[1]
    if ext not in settings.FILE_EXTENSION_WHITELIST:
        raise FileValidationError(f"{file.filename} is an invalid file type")
    return True
