from typing import Iterator, List, Optional
import re

import pandas as pd


class FileReader:
    def __init__(self, pathname: str):
        self._pathname = pathname

    @property
    def lines(self) -> Iterator[str]:
        with open(self._pathname, "r") as f:
            f.readline()  # Omit first line
            for line in f.read().splitlines():
                if len(line) != 0:
                    yield (line)


class LineParser:
    def __init__(self, line: str):
        self._line = line

    @property
    def as_dict(self) -> dict:
        return {
            "cpu_percentage": self._regex_result_values["cpu"],
            "mem_percentage": self._regex_result_values["mem"],
            "time": self._regex_result_values["date"],
        }

    @property
    def _regex_result_values(self) -> Optional[re.Match]:
        regex = re.compile(
            r"""
        \s*
        (?P<cpu>\d+(\.\d+)?)
        \s+
        (?P<mem>\d+(\.\d+)?)
        \s+
        (?P<date>\d+:\d+:\d+\.\d+)
        """,
            re.VERBOSE,
        )
        return re.match(regex, self._line)


class FileParser:
    def __init__(self, pathname: str):
        self._file_reader = FileReader(pathname)

    @property
    def df(self) -> pd.DataFrame:
        return pd.DataFrame(self._get_file_content_parsed())

    def _get_file_content_parsed(self) -> List[dict]:
        return [LineParser(line).as_dict for line in self._file_reader.lines]
