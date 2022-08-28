from typing import Iterator, List
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
            "cpu_id": self._regex_result_values["cpu_id"],
            "cpu_percentage": self._regex_result_values["cpu"],
            "mem_percentage": self._regex_result_values["mem"],
            "time": self._regex_result_values["date"],
        }

    @property
    def _regex_result_values(self) -> re.Match:
        regex = re.compile(
            r"""
        \s*
        (?P<cpu_id>\d+)
        \s+
        (?P<cpu>\d+(\.\d+)?)
        \s+
        (?P<mem>\d+(\.\d+)?)
        \s+
        (?P<date>\d+:\d+:\d+\.\d+)
        """,
            re.VERBOSE,
        )
        result = re.match(regex, self._line)
        assert result is not None
        return result


class FileParser:
    def __init__(self, pathname: str):
        self._file_reader = FileReader(pathname)

    @property
    def df(self) -> pd.DataFrame:
        return pd.DataFrame(self._get_file_content_parsed())

    def _get_file_content_parsed(self) -> List[dict]:
        return [LineParser(line).as_dict for line in self._file_reader.lines]
