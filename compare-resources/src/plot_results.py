from typing import Iterator, List, Optional
import collections
import datetime
import os
import re

import matplotlib.pyplot as plt
import matplotlib as mpl

Metric = collections.namedtuple("Metric", ["cpu", "mem", "date"])


class FileParser:
    def __init__(self, pathname: str):
        self._pathname = pathname

    @property
    def metrics(self) -> List[Metric]:
        return self._get_file_content_parsed()

    def _get_file_content_parsed(self) -> List[Metric]:
        result = list()
        regex_result_cpu_mem = None
        for line in self._get_metric_lines_in_file():
            if regex_result_cpu_mem is None:
                regex_result_cpu_mem = self._get_regex_result_cpu_mem(line)
                self._assert_regex_result_has_value(regex_result_cpu_mem, line)
                continue
            regex_result_date = self._get_regex_result_date(line)
            self._assert_regex_result_has_value(regex_result_date, line)
            result.append(
                self._get_metric_from_regex_results(
                    regex_result_cpu_mem,
                    regex_result_date,
                )
            )
            regex_result_cpu_mem = None
        return result

    def _get_metric_lines_in_file(self) -> Iterator[str]:
        with open(self._pathname, "r") as f:
            f.readline()  # Omit first line
            for line in f.read().splitlines():
                if len(line) != 0:
                    yield (line)

    def _get_regex_result_cpu_mem(self, line: str) -> Optional[re.Match]:
        regex = r"\s*(?P<cpu>\d+(\.\d+)?)\s+(?P<mem>\d+(\.\d+)?)"
        return re.match(regex, line)

    def _get_regex_result_date(self, line: str) -> Optional[re.Match]:
        regex = r"(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)\.(?P<microsecond>\d+)"
        return re.match(regex, line)

    def _assert_regex_result_has_value(
        self, regex_result: Optional[re.Match], line: str
    ):
        if regex_result is None:
            raise ValueError(line)

    def _get_metric_from_regex_results(
        self, regex_result_cpu_mem: re.Match, regex_result_date: re.Match
    ) -> Metric:
        return Metric(
            float(regex_result_cpu_mem["cpu"]),
            float(regex_result_cpu_mem["mem"]),
            self._get_time_from_regex_result_date(regex_result_date),
        )

    def _get_time_from_regex_result_date(
        self, regex_result_date: re.Match
    ) -> datetime.date:
        max_microseconds_digits = 6
        return datetime.time(
            hour=int(regex_result_date["hour"]),
            minute=int(regex_result_date["minute"]),
            second=int(regex_result_date["second"]),
            microsecond=int(regex_result_date["microsecond"][:max_microseconds_digits]),
        )


def export_image():
    mpl.rcParams["lines.linewidth"] = 2
    mpl.rcParams["lines.linestyle"] = "--"
    x = [0, 1, 2, 3, 4, 5]
    y = [2, 3, 4, 8, 1, 2.3]
    fig, ax = plt.subplots()
    ax.plot(x, y)
    fig.savefig("result.png")


if __name__ == "__main__":
    pathname = "{dir_pathname}/results-python.txt".format(
        dir_pathname=os.path.dirname(os.path.realpath(__file__))
    )
    print("Init", pathname)
    metrics = FileParser(pathname).metrics
    print(metrics)
