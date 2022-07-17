from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple
import argparse
import csv
import gzip
import re


def get_args_parsed():
    # https://docs.python.org/3/library/argparse.html#the-add-argument-method
    parser = argparse.ArgumentParser(description="Export Nginx logs to a csv file.")
    parser.add_argument(
        "pathname",
        type=str,
        help="path to a folder with the log files or to an specific file",
    )
    return parser.parse_args()


class Log:

    DICT_KEYS = [
        "remote_addr",
        "remote_user",
        "time_local",
        "request",
        "status",
        "body_bytes_sent",
        "http_referer",
        "http_user_agent",
    ]

    def __init__(
        self,
        remote_addr: str,
        remote_user: str,
        time_local: str,
        request: str,
        status: str,
        body_bytes_sent: str,
        http_referer: str,
        http_user_agent: str,
    ):
        self.remote_addr = remote_addr
        self.remote_user = remote_user
        self.time_local = time_local
        self.request = request
        self.status = status
        self.body_bytes_sent = body_bytes_sent
        self.http_referer = http_referer
        self.http_user_agent = http_user_agent

    def __repr__(self):
        return "{},{},{},{},{},{},{},{}".format(
            self.remote_addr,
            self.remote_user,
            self.time_local,
            self.request,
            self.status,
            self.body_bytes_sent,
            self.http_referer,
            self.http_user_agent,
        )

    def asdict(self) -> dict:
        return {
            "remote_addr": self.remote_addr,
            "remote_user": self.remote_user,
            "time_local": self.time_local,
            "request": self.request,
            "status": self.status,
            "body_bytes_sent": self.body_bytes_sent,
            "http_referer": self.http_referer,
            "http_user_agent": self.http_user_agent,
        }


# https://docs.nginx.com/nginx/admin-guide/monitoring/logging/
REGEX = re.compile(
    r"""
    ^
    ((\d{1,3}[\.]){3}\d{1,3}) # IPv4
    \s-\s
    (.+)                      # Remote user
    \s\[
    (.+)                      # Time local
    \]\s"
    (.*)                      # Request
    "\s
    (\d{1,3})                 # Status
    \s
    (\d+)                     # Body bytes sent
    \s"
    (.+)                      # HTTP referer
    "\s"
    (.*)                      # HTTP user agent
    "
""",
    re.VERBOSE,
)


def get_log(line: str) -> Optional[Log]:
    match = re.match(REGEX, line)
    return (
        None
        if match is None
        else Log(
            remote_addr=match.group(1),
            remote_user=match.group(3),
            time_local=match.group(4),
            request=match.group(5),
            status=match.group(6),
            body_bytes_sent=match.group(7),
            http_referer=match.group(8),
            http_user_agent=match.group(9),
        )
    )


def get_paths_to_work_with(path_without_filename: Path) -> Tuple[Path, Path]:
    return [
        path_without_filename.joinpath("result.csv"),
        path_without_filename.joinpath("error.txt"),
    ]


def run(args):
    print(f"Checking: {args.pathname}")
    path = Path(args.pathname)
    path_without_filename = path.parent if path.is_file() else path
    path_csv, path_error = get_paths_to_work_with(path_without_filename)
    print(f"File with logs as csv: {path_csv}")
    print(f"File with not parsed logs: {path_error}")
    with open(path_csv, "w") as file_csv, open(path_error, "w") as file_error:
        writer_csv = csv.DictWriter(file_csv, fieldnames=Log.DICT_KEYS)
        writer_csv.writeheader()
        for pathname in get_pathnames_to_analyze(path):
            for line in FileReader().get_lines_in_file(pathname):
                if len(line) != 0:
                    log = get_log(line)
                    if log is None:
                        write_to_file_error(line, file_error)
                    else:
                        write_to_file_result(log, writer_csv)


def get_pathnames_to_analyze(path: Path) -> Iterator[str]:
    if path.is_file():
        yield str(path)
    elif path.is_dir():
        for filename in FilenamesFilter().get_filenames_to_analyze_in_path(path):
            yield str(path.joinpath(filename))


class FileReader:
    def get_lines_in_file(self, pathname: str) -> Iterator[str]:
        print(f"Init file: {pathname}")
        for line in self._get_lines_in_file(pathname):
            yield line

    def _get_lines_in_file(self, pathname: str) -> Iterator[str]:
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


class FilenamesFilter:
    def get_filenames_to_analyze_in_path(self, path: Path) -> List[str]:
        filenames = [file_path.name for file_path in path.glob("*")]
        return self._get_log_filenames_sort_reverse(filenames)

    def _get_log_filenames_sort_reverse(self, filenames: List[str]) -> List[str]:
        filenames_with_logs = self._get_filenames_with_logs(filenames)
        numbers_and_log_filenames = self._get_numbers_and_filenames(filenames_with_logs)
        return self._get_filenames_sorted(numbers_and_log_filenames)

    def _get_filenames_with_logs(self, filenames: List[str]) -> List[str]:
        return [filename for filename in filenames if filename.startswith("access.log")]

    def _get_numbers_and_filenames(self, filenames: List[str]) -> Dict[int, str]:
        result = {}
        for filename in filenames:
            possible_number = self._get_filename_possible_number(filename)
            try:
                number = int(possible_number)
                result.update({number: filename})
            except ValueError:
                pass
        return result

    def _get_filename_possible_number(self, filename: str) -> str:
        if filename == "access.log":
            return "0"
        else:
            number_index = -2 if filename.endswith(".gz") else -1
            return filename.split(".")[number_index]

    def _get_filenames_sorted(self, numbers_and_filenames: Dict[int, str]) -> List[str]:
        numbers_and_log_filenames_sorted: List[Tuple[int, str]] = sorted(
            numbers_and_filenames.items(), reverse=True
        )
        return [
            number_and_filename[1]
            for number_and_filename in numbers_and_log_filenames_sorted
        ]


def write_to_file_result(log: Log, writer):
    writer.writerow(log.asdict())


def write_to_file_error(line: str, writer):
    print(f"Not parsed: {line}")
    writer.write(f"{line}\n")
