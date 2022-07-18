from typing import Iterator
import gzip


class FileReader:
    def get_lines_in_pathname(self, pathname: str) -> Iterator[str]:
        print(f"Init file: {pathname}")
        for line in self._get_lines_in_pathname(pathname):
            yield line

    def _get_lines_in_pathname(self, pathname: str) -> Iterator[str]:
        return (
            self._get_lines_in_gz_file(pathname)
            if pathname.endswith(".gz")
            else self._get_lines_in_log_file(pathname)
        )

    def _get_lines_in_log_file(self, pathname: str) -> Iterator[str]:
        with open(pathname, "r") as file:
            for line in file.read().splitlines():
                yield line

    def _get_lines_in_gz_file(self, pathname: str) -> Iterator[str]:
        with gzip.open(pathname, mode="rt") as fp:
            for line in fp:
                yield line
