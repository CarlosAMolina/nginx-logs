from typing import Iterator, List, Optional

import pandas as pd


class FileReader:
    def __init__(self, pathname: str):
        self._pathname = pathname

    @property
    def lines(self) -> Iterator[str]:
        with open(self._pathname, "r") as f:
            for line in f.read().splitlines():
                if len(line) != 0:
                    yield (line)


class LineParser:
    def __init__(self, line: str):
        self._line = line
        self.names_with_value = [
            "snapshot",
            "time",
            "mem_heap_B",
            "mem_heap_extra_B",
            "mem_stacks_B",
            "heap_tree",
        ]

    @property
    def name_with_value(self) -> Optional[str]:
        for name in self.names_with_value:
            if self._line.startswith(f"{name}="):
                return name
        return None

    @property
    def value(self) -> str:
        return self._line.split("=")[-1]


class FileParser:
    def __init__(self, pathname: str):
        self._file_reader = FileReader(pathname)

    @property
    def df(self) -> pd.DataFrame:
        result = pd.DataFrame(self._get_file_content_parsed())
        result.set_index("snapshot", inplace=True)
        return result

    def _get_file_content_parsed(self) -> List[dict]:
        result = []
        snapshot = {}
        for line in self._file_reader.lines:
            line_parsed = LineParser(line)
            name_with_value = line_parsed.name_with_value
            if name_with_value is not None:
                if name_with_value == "snapshot":
                    snapshot = {}
                snapshot[name_with_value] = line_parsed.value
                if len(snapshot) == len(line_parsed.names_with_value):
                    result.append(snapshot)
        return result
