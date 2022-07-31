from typing import Iterator, List, Optional
import collections
import datetime
import os
import re

import matplotlib.pyplot as plt
import matplotlib as mpl

Metric = collections.namedtuple("Metric", ["cpu", "mem", "time"])


# TODO
def get_seconds_elapsed():
    """https://stackoverflow.com/questions/35241643/convert-datetime-time-into-datetime-timedelta-in-python-3-4"""
    a = datetime.datetime(2022, 7, 31, 23, 50, 1)
    b = datetime.datetime(2022, 7, 31, 23, 54, 11)
    a2 = a - datetime.datetime.min
    b2 = b - datetime.datetime.min
    b2 - a2  # datetime.timedelta(seconds=250)


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
            regex_result_time = self._get_regex_result_time(line)
            self._assert_regex_result_has_value(regex_result_time, line)
            result.append(
                self._get_metric_from_regex_results(
                    regex_result_cpu_mem,
                    regex_result_time,
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

    def _get_regex_result_time(self, line: str) -> Optional[re.Match]:
        regex = r"(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)\.(?P<microsecond>\d+)"
        return re.match(regex, line)

    def _assert_regex_result_has_value(
        self, regex_result: Optional[re.Match], line: str
    ):
        if regex_result is None:
            raise ValueError(line)

    def _get_metric_from_regex_results(
        self, regex_result_cpu_mem: re.Match, regex_result_time: re.Match
    ) -> Metric:
        return Metric(
            float(regex_result_cpu_mem["cpu"]),
            float(regex_result_cpu_mem["mem"]),
            self._get_time_from_regex_result_time(regex_result_time),
        )

    def _get_time_from_regex_result_time(
        self, regex_result_time: re.Match
    ) -> datetime.time:
        max_microseconds_digits = 6
        return datetime.time(
            hour=int(regex_result_time["hour"]),
            minute=int(regex_result_time["minute"]),
            second=int(regex_result_time["second"]),
            microsecond=int(regex_result_time["microsecond"][:max_microseconds_digits]),
        )


def export_image(metrics: List[Metric]):
    print(f"Init plot {len(metrics)} points")
    mpl.rcParams["lines.linewidth"] = 0.5
    x = [str(metric.time) for metric in metrics]
    y = [metric.cpu for metric in metrics]
    fig, ax = plt.subplots()
    ax.plot(x, y, marker=".", markersize=2)
    ax.set_xlabel("Time")
    ax.set_ylabel("CPU%")
    plt.grid(color="black", linestyle="-", linewidth=0.1)
    plt.xticks(range(0, 2020, 100), rotation="vertical")
    plt.subplots_adjust(bottom=0.4)

    fig.savefig("result.png", dpi=300)
    # fig.savefig("result.pdf")


if __name__ == "__main__":
    pathname = "{dir_pathname}/results-python.txt".format(
        dir_pathname=os.path.dirname(os.path.realpath(__file__))
    )
    print("Init", pathname)
    metrics = FileParser(pathname).metrics
    export_image(metrics)
