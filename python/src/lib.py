from pathlib import Path
from typing import List, Optional
import argparse
import re


def get_args_parsed():
    # https://docs.python.org/3/library/argparse.html#the-add-argument-method
    parser = argparse.ArgumentParser(description="Export Nginx logs to a csv file.")
    parser.add_argument(
        "file_or_path",
        type=str,
        help="path to a folder with the log files or to an specific file",
    )
    return parser.parse_args()


class Log:
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
    (.+)                      # HTTP user agent
    "
""",
    re.VERBOSE,
)


def get_log(line: str) -> Optional[Log]:
    match = re.search(REGEX, line)
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


def run(args):
    print(f"Checking: {args.file_or_path}")
    file_or_path_to_check = Path(args.file_or_path)
    path_to_check = (
        file_or_path_to_check.parent
        if file_or_path_to_check.is_file()
        else file_or_path_to_check
    )
    path_csv = path_to_check.joinpath("result.csv")
    print(f"File with logs as csv: {path_csv}")
    path_error = path_to_check.joinpath("error.txt")
    print(f"File with not parsed logs: {path_error}")
    if file_or_path_to_check.is_file():
        export_file_to_csv(file_or_path_to_check, path_csv, path_error)
    elif file_or_path_to_check.is_dir():
        for filename in get_filenames_to_analyze_in_path(file_or_path_to_check):
            pass  # TODO delete


def get_filenames_to_analyze_in_path(path: Path) -> List[str]:
    filenames = [file_path.name for file_path in path.glob("*")]
    result = get_log_filenames_sort_reverse(filenames)
    print(result)
    return result


def get_log_filenames_sort_reverse(filenames: List[str]) -> List[str]:
    regex_file_number = r"^access\.log\.(?P<file_number>\d+)"
    search_results = [
        re.search(regex_file_number, str(filename)) for filename in filenames
    ]
    numbers = [
        int(search_result.group("file_number"))
        for search_result in search_results
        if search_result is not None
    ]
    numbers.sort(reverse=True)
    result = [f"access.log.{number}" for number in numbers]
    if "access.log" in filenames:
        result.append("access.log")
    return result


def export_file_to_csv(path_to_check: str, path_result: str, path_errors: str):
    print(f"Init file: {path_to_check}")
    with open(path_to_check, "r") as path_to_check_:
        with open(path_result, "a") as path_result_, open(
            path_errors, "a"
        ) as path_errors_:
            for line in path_to_check_.read().splitlines():
                if len(line) != 0:
                    log = get_log(line)
                    if log is None:
                        print(f"Not parsed {line}")
                        path_errors_.write(line)
                        path_errors_.write("\n")
                    else:
                        path_result_.write(str(log))
                        path_result_.write("\n")
