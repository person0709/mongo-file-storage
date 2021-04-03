from enum import Enum
from typing import Tuple

import pymongo


class SortType(str, Enum):
    FILENAME_DESC = "filename_desc"
    FILENAME_ASC = "filename_asc"
    UPLOADED_DATE_DESC = "uploaded_date_desc"
    UPLOADED_DATE_ASC = "uploaded_date_asc"
    FILE_SIZE_DESC = "size_desc"
    FILE_SIZE_ASC = "size_asc"

    @classmethod
    def parse_sort_type(cls, sort_by: str) -> Tuple[str, int]:
        sort_by_parse = sort_by.split("_")
        if sort_by_parse[-1] == "desc":
            sort_dir = pymongo.DESCENDING
        else:
            sort_dir = pymongo.ASCENDING

        if sort_by_parse[-2] == "filename":
            sort_field = "filename"
        elif sort_by_parse[-2] == "date":
            sort_field = "uploadDate"
        else:
            sort_field = "length"

        return sort_field, sort_dir
