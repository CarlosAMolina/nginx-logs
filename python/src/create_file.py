from pathlib import Path
from typing import Tuple
import csv

import m_log


def get_pathnames_to_work_with(pathname: str) -> Tuple[str, str]:
    path = Path(pathname)
    path_without_filename = path.parent if path.is_file() else path
    result = (
        str(path_without_filename.joinpath("result.csv")),
        str(path_without_filename.joinpath("error.txt")),
    )
    print(f"File with logs as csv: {result[0]}")
    print(f"File with not parsed logs: {result[1]}")
    return result


def get_csv_writer(file_csv):
    return csv.DictWriter(file_csv, fieldnames=m_log.Log.DICT_KEYS)
