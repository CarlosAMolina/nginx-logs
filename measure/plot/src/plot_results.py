from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple, Union
import math
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from extractors import extractor
from transformers import transformer


class Round:
    def get_round_up_to_nearest_ten(self, value: float) -> int:
        """
        https://stackoverflow.com/questions/26454649/python-round-up-to-the-nearest-ten
        """
        return int(math.ceil(value / 10.0)) * 10

    def get_round_up_to_nearest_integer(self, value: float) -> int:
        return int(value + 1)

    def get_round_up_to_nearest_decimal(
        self, value: float, decimal_position: int = 1
    ) -> float:
        return int(value * 10**decimal_position + 1) / 10**decimal_position


class AxisConfig(NamedTuple):
    label: str
    label_values: Optional[Union[list, np.ndarray]]
    max_lim: Union[int, float]
    min_lim: Union[int, float]


class AxisConfigs(NamedTuple):
    x: AxisConfig
    y: AxisConfig


class AxisConfigsCustom(NamedTuple):
    x: Optional[AxisConfig]
    y: Optional[AxisConfig]


class SubplotsAxisValues:
    def __init__(self, subplots_axis_values: List[pd.Series]):
        self._subplots_axis_values = subplots_axis_values

    @property
    def max_value(self):
        return self._get_value(max)

    @property
    def min_value(self):
        return self._get_value(min)

    def _get_value(self, func: Union[max, min]):
        return func(
            func(subplot_y_axis_values)
            for subplot_y_axis_values in self._subplots_axis_values
        )


class XAxisConfigCalculator:
    def __init__(self, axis_label: str, subplots_x_axis_values: List[pd.Series]):
        self._axis_label = axis_label
        self._subplots_x_axis_values = SubplotsAxisValues(subplots_x_axis_values)
        self._round = Round()

    @property
    def config(self) -> AxisConfig:
        return AxisConfig(
            self._axis_label,
            self._label_values,
            self._max_lim,
            self._min_lim,
        )

    @property
    def _label_step(self) -> Union[int, float]:
        if self._subplots_x_axis_values.max_value >= 100_000:
            return 20_000
        elif self._subplots_x_axis_values.max_value <= 1:
            return 0.01
        return 1

    @property
    def _label_values(self) -> list:
        return list(
            np.arange(
                self._min_lim, self._max_lim + self._label_step, step=self._label_step
            )
        )

    @property
    def _max_lim(self) -> Union[float, int]:
        if self._subplots_x_axis_values.max_value <= 0.1:
            return self._round.get_round_up_to_nearest_decimal(
                self._subplots_x_axis_values.max_value, decimal_position=2
            )
        if self._subplots_x_axis_values.max_value < 1:
            return self._round.get_round_up_to_nearest_decimal(
                self._subplots_x_axis_values.max_value
            )
        return self._round.get_round_up_to_nearest_integer(
            self._subplots_x_axis_values.max_value
        )

    @property
    def _min_lim(self) -> int:
        return 0


class YAxisConfigCalculator:
    def __init__(self, axis_label: str, subplots_y_axis_values: List[pd.Series]):
        self._axis_label = axis_label
        self._subplots_y_axis_values = SubplotsAxisValues(subplots_y_axis_values)
        self._round = Round()

    @property
    def config(self) -> AxisConfig:
        return AxisConfig(
            self._axis_label,
            self._label_values,
            self._max_lim,
            self._min_lim,
        )

    @property
    def _label_values(self) -> list:
        return list(
            np.arange(
                self._min_lim, self._max_lim + self._label_step, step=self._label_step
            )
        )

    @property
    def _max_lim(self) -> Union[int, float]:
        if self._subplots_y_axis_values.max_value > 1_500_000:
            return 1_700_000
        if self._label_step >= 10:
            result = self._round.get_round_up_to_nearest_ten(
                self._subplots_y_axis_values.max_value
            )
            if result % self._label_step == 0:
                return result
            return self._round.get_round_up_to_nearest_ten(
                self._subplots_y_axis_values.max_value + 10
            )
        return self._label_step

    @property
    def _min_lim(self) -> Union[int, float]:
        if self._label_step >= 10:
            return -1 * self._label_step
        return -1 * self._label_step

    @property
    def _diff_max_min_value(self) -> float:
        return (
            self._subplots_y_axis_values.max_value
            - self._subplots_y_axis_values.min_value
        )

    @property
    def _label_step(self) -> Union[int, float]:
        if self._diff_max_min_value < 0.02:
            return 0.02
        elif self._diff_max_min_value <= 100:
            return 10
        elif self._diff_max_min_value <= 1000:
            return 20
        return 500_000


class SubplotValues:
    def __init__(self, x_axis_values: list, y_axis_values: list):
        assert len(x_axis_values) == len(y_axis_values)
        self._len = len(x_axis_values)
        self._x_axis_values = x_axis_values
        self._y_axis_values = y_axis_values

    def __len__(self):
        return self._len

    @property
    def x_axis_values(self) -> list:
        return self._x_axis_values

    @property
    def y_axis_values(self) -> list:
        return self._y_axis_values


class SubplotRepresentationConfig(NamedTuple):
    color: str
    marker: str
    markersize: float
    linewidth: float = 0.5


class Subplot(NamedTuple):
    legend: str
    x_axis_values: pd.Series
    y_axis_values: pd.Series
    representation_config: SubplotRepresentationConfig


class AxisLabels(NamedTuple):
    x: str
    y: str


class Figure(NamedTuple):
    axis_labels: AxisLabels
    title: Optional[str] = None


Subplots = List[Subplot]


class AnnotateConfig(NamedTuple):
    xy: Tuple[Union[float, int], Union[float, int]]
    xytext: Tuple[Union[float, int], Union[float, int]]


AnnotateConfigs = List[AnnotateConfig]


class Plot(NamedTuple):
    annotate_configs: AnnotateConfigs
    subplots: Subplots
    axis_configs: AxisConfigs
    title: Optional[str]


class ExportImage:
    def export_image(
        self,
        image_pathname: str,
        plot: Plot,
    ):
        print(f"Init plot. File: {image_pathname}")
        fig, ax = plt.subplots()
        for subplot in plot.subplots:
            ax.plot(
                subplot.x_axis_values,
                subplot.y_axis_values,
                color=subplot.representation_config.color,
                marker=subplot.representation_config.marker,
                markersize=subplot.representation_config.markersize,
                label=subplot.legend,
                linewidth=subplot.representation_config.linewidth,
            )
        ax.legend()
        ax.set_xlabel(plot.axis_configs.x.label)
        ax.set_ylabel(plot.axis_configs.y.label)
        plt.xticks(plot.axis_configs.x.label_values)
        plt.yticks(plot.axis_configs.y.label_values)
        ax.set_xlim(plot.axis_configs.x.min_lim, plot.axis_configs.x.max_lim)
        ax.set_ylim(bottom=plot.axis_configs.y.min_lim, top=plot.axis_configs.y.max_lim)
        ax.set_ybound(
            lower=plot.axis_configs.y.min_lim, upper=plot.axis_configs.y.max_lim
        )
        subplots_y_axis_values = SubplotsAxisValues(
            [subplot.y_axis_values for subplot in plot.subplots]
        )
        for annotate_config in plot.annotate_configs:
            ax.annotate(
                f"Max {subplots_y_axis_values.max_value}",
                xy=annotate_config.xy,
                xycoords="data",
                xytext=annotate_config.xytext,
                textcoords="axes fraction",
                arrowprops=dict(facecolor="black", shrink=0.05, width=2, headwidth=8),
                horizontalalignment="left",
                verticalalignment="top",
            )
        if plot.title is not None:
            plt.title(plot.title)
        plt.grid(color="black", linestyle="-", linewidth=0.1)
        plt.subplots_adjust(left=0.15, bottom=0.15, right=0.95, top=0.90)
        fig.savefig(image_pathname, dpi=300)


class ResultsPath:
    def get_metrics_path(self, metrics_pathname: str) -> Path:
        return self._results_path.joinpath(metrics_pathname)

    @property
    def _results_path(self) -> Path:
        this_script_path = Path(__file__).parent.absolute()
        return this_script_path.joinpath("results")

    def get_image_pathname(self, image_pathname: str) -> Path:
        return self._results_path.joinpath(image_pathname)


class SubplotsConfig(NamedTuple):
    metrics_pathnames: List[str]
    legends: List[str]
    colors: List[str]
    markers: List[str]
    markerssize: List[Union[float, int]]


class DfColumnNamesAxis(NamedTuple):
    x: str
    y: str


def get_subplots(
    df_column_names_axis: DfColumnNamesAxis, subplots_config: SubplotsConfig
) -> Subplots:
    result = []
    for (metrics_pathname, legend, color, marker, markersize,) in zip(
        subplots_config.metrics_pathnames,
        subplots_config.legends,
        subplots_config.colors,
        subplots_config.markers,
        subplots_config.markerssize,
    ):
        print(f"Init {metrics_pathname}")
        df = get_df_from_file(metrics_pathname)
        # print(df.sort_values(by=['mem_total'], ascending=False).head())
        result.append(
            Subplot(
                legend,
                df[df_column_names_axis.x],
                df[df_column_names_axis.y],
                SubplotRepresentationConfig(
                    color,
                    marker,
                    markersize,
                ),
            )
        )
    return result


def get_df_from_file(metrics_pathname: str) -> pd.DataFrame:
    result = extractor.get_df_from_pathname(metrics_pathname)
    return transformer.get_df_transformed(metrics_pathname, result)


def export_image(
    annotate_configs: AnnotateConfigs,
    image_filename: str,
    figure: Figure,
    subplots: Subplots,
    axis_configs_custom: Optional[AxisConfigsCustom] = None,
):
    ExportImage().export_image(
        str(ResultsPath().get_image_pathname(image_filename)),
        get_plot(annotate_configs, figure, subplots, axis_configs_custom),
    )


def get_plot(
    annotate_configs: AnnotateConfigs,
    figure: Figure,
    subplots: Subplots,
    axis_configs_custom: Optional[AxisConfigsCustom] = None,
) -> Plot:
    x_axis_config = (
        XAxisConfigCalculator(
            figure.axis_labels.x, [subplot.x_axis_values for subplot in subplots]
        ).config
        if axis_configs_custom is None or axis_configs_custom.x is None
        else axis_configs_custom.x
    )
    y_axis_config = (
        YAxisConfigCalculator(
            figure.axis_labels.y, [subplot.y_axis_values for subplot in subplots]
        ).config
        if axis_configs_custom is None or axis_configs_custom.y is None
        else axis_configs_custom.y
    )
    return Plot(
        annotate_configs,
        subplots,
        AxisConfigs(x_axis_config, y_axis_config),
        figure.title,
    )


if __name__ == "__main__":
    # df_column_names_axis = DfColumnNamesAxis("time_elapsed", "cpu_percentage")
    # legends = ["Execution 1", "Execution 2", "Execution 3"]
    # axis_label = AxisLabels("Time (s)", "CPU (%)")
    # metrics_pathname = "/tmp/metricas/metrics-python/"
    # subplots_config = SubplotsConfig(
    #    metrics_pathnames=[
    #        f"{metrics_pathname}metrics-python-1.txt",
    #        f"{metrics_pathname}metrics-python-2.txt",
    #        f"{metrics_pathname}metrics-python-3.txt",
    #    ],
    #    legends=legends,
    #    colors=["b", "limegreen", "r"],
    #    markers=["o", "o", "o"],
    #    markerssize=[4.5, 2.5, 0.7],
    # )
    # export_image(
    #    "metrics-rust.png",
    #    axis_label,
    #    get_subplots(df_column_names_axis, subplots_config),
    # )

    # metrics_pathname = "/tmp/metricas/metrics-rust/"
    # subplots_config = SubplotsConfig(
    #    metrics_pathnames=[
    #        f"{metrics_pathname}metrics-nginx_logs-1.txt",
    #        f"{metrics_pathname}metrics-nginx_logs-2.txt",
    #        f"{metrics_pathname}metrics-nginx_logs-3.txt",
    #    ],
    #    legends=legends,
    #    colors=["b", "limegreen", "r"],
    #    markers=["o", "o", "o"],
    #    markerssize=[4.5, 3, 2],
    # )
    # export_image(
    #    "metrics-rust.png",
    #    axis_label,
    #    get_subplots(df_column_names_axis, subplots_config),
    # )

    legends = ["Execution 1", "Execution 2", "Execution 3"]
    metrics_pathname = "/tmp/20220825-massif/"

    def export_rust_heap_only():
        df_column_names_axis = DfColumnNamesAxis("time_s", "mem_total_kb")
        figure = Figure(
            axis_labels=AxisLabels("Time (s)", "Mem (kB)"),
            title="Memory heap Rust",
        )
        y_axis_config = AxisConfig(
            label=figure.axis_labels.y,
            label_values=[i for i in range(-10, 120, 10)],
            max_lim=110,
            min_lim=-5,
        )
        annotate_configs = [
            AnnotateConfig(
                xy=(0.85, 100),
                xytext=(0.15, 0.8),
            )
        ]
        subplots_config = SubplotsConfig(
            metrics_pathnames=[
                f"{metrics_pathname}massif.out.1616.rust.heap-only",
                f"{metrics_pathname}massif.out.1827.rust.heap-only",
                f"{metrics_pathname}massif.out.1984.rust.heap-only",
            ],
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        export_image(
            annotate_configs,
            "/tmp/metrics-massif-rust-heap-only.png",
            figure,
            get_subplots(df_column_names_axis, subplots_config),
            AxisConfigsCustom(None, y_axis_config),
        )

    def export_rust_add_stacks():
        df_column_names_axis = DfColumnNamesAxis("time_s", "mem_total_kb")
        figure = Figure(
            axis_labels=AxisLabels("Time (s)", "Mem (kB)"),
            title="Memory heap and stack Rust",
        )
        x_axis_config = AxisConfig(
            label=figure.axis_labels.x,
            label_values=[i for i in range(0, 170, 10)],
            max_lim=155,
            min_lim=-5,
        )
        y_axis_config = AxisConfig(
            label=figure.axis_labels.y,
            label_values=[i for i in range(-10, 120, 10)],
            max_lim=110,
            min_lim=-5,
        )
        annotate_configs = [
            AnnotateConfig(
                xy=(0.85, 100),
                xytext=(0.15, 0.8),
            ),
        ]
        subplots_config = SubplotsConfig(
            metrics_pathnames=[
                f"{metrics_pathname}massif.out.1624.rust.add-stacks",
                f"{metrics_pathname}massif.out.1832.rust.add-stacks",
                f"{metrics_pathname}massif.out.1990.rust.add-stacks",
            ],
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        export_image(
            annotate_configs,
            "/tmp/metrics-massif-rust-add_stacks.png",
            figure,
            get_subplots(df_column_names_axis, subplots_config),
            AxisConfigsCustom(x_axis_config, y_axis_config),
        )

    def export_rust_add_pages_as_heap():
        df_column_names_axis = DfColumnNamesAxis("time_s", "mem_total_mb")
        figure = Figure(
            axis_labels=AxisLabels("Time (s)", "Mem (MB)"),
            title="Memory page level Rust",
        )
        x_axis_config = AxisConfig(
            label=figure.axis_labels.x,
            label_values=np.arange(0, 5, 0.5),
            max_lim=4.1,
            min_lim=-0.1,
        )
        y_axis_config = AxisConfig(
            label=figure.axis_labels.y,
            label_values=np.arange(0, 6, 0.5),
            max_lim=5.5,
            min_lim=0,
        )
        annotate_configs = [
            AnnotateConfig(
                xy=(0.4, 5),
                xytext=(0.15, 0.8),
            ),
            AnnotateConfig(
                xy=(4, 5),
                xytext=(0.15, 0.8),
            ),
        ]
        subplots_config = SubplotsConfig(
            metrics_pathnames=[
                f"{metrics_pathname}massif.out.1638.rust.add-pages-as-heap",
                f"{metrics_pathname}massif.out.1842.rust.add-pages-as-heap",
                f"{metrics_pathname}massif.out.1998.rust.add-pages-as-heap",
            ],
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        export_image(
            annotate_configs,
            "/tmp/metrics-massif-rust-add-pages-as-heap.png",
            figure,
            get_subplots(df_column_names_axis, subplots_config),
            AxisConfigsCustom(x_axis_config, y_axis_config),
        )

    def export_python_heap_only():
        df_column_names_axis = DfColumnNamesAxis("time_s", "mem_total_mb")
        figure = Figure(
            axis_labels=AxisLabels("Time (s)", "Mem (MB)"),
            title="Memory heap Python",
        )
        x_axis_config = AxisConfig(
            label=figure.axis_labels.x,
            label_values=np.arange(0, 100, 10),
            max_lim=90,
            min_lim=-1,
        )
        y_axis_config = AxisConfig(
            label=figure.axis_labels.y,
            label_values=np.arange(0, 27, 2),
            max_lim=26.5,
            min_lim=-0.5,
        )
        annotate_configs = [
            AnnotateConfig(
                xy=(75, 26),
                xytext=(0.5, 0.8),
            ),
        ]
        subplots_config = SubplotsConfig(
            metrics_pathnames=[
                f"{metrics_pathname}massif.out.1645.python.heap-only",
                f"{metrics_pathname}massif.out.1849.python.heap-only",
                f"{metrics_pathname}massif.out.2008.python.heap-only",
            ],
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        export_image(
            annotate_configs,
            "/tmp/metrics-massif-python-heap-only.png",
            figure,
            get_subplots(df_column_names_axis, subplots_config),
            AxisConfigsCustom(x_axis_config, y_axis_config),
        )

    def export_python_add_stacks():
        df_column_names_axis = DfColumnNamesAxis("time_minute", "mem_total_mb")
        figure = Figure(
            axis_labels=AxisLabels("Time (min)", "Mem (MB)"),
            title="Memory heap and stack Python",
        )
        x_axis_config = AxisConfig(
            label=figure.axis_labels.x,
            label_values=np.arange(0, 44, 2),
            max_lim=42,
            min_lim=-0.5,
        )
        y_axis_config = AxisConfig(
            label=figure.axis_labels.y,
            label_values=np.arange(0, 27, 2),
            max_lim=26.5,
            min_lim=-0.5,
        )
        annotate_configs = [
            AnnotateConfig(
                xy=(36, 26),
                xytext=(0.5, 0.8),
            ),
        ]
        subplots_config = SubplotsConfig(
            metrics_pathnames=[
                f"{metrics_pathname}massif.out.1654.python.add-stacks",
                f"{metrics_pathname}massif.out.1858.python.add-stacks",
                f"{metrics_pathname}massif.out.2015.python.add-stacks",
            ],
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        export_image(
            annotate_configs,
            "/tmp/metrics-massif-python-add_stacks.png",
            figure,
            get_subplots(df_column_names_axis, subplots_config),
            AxisConfigsCustom(x_axis_config, y_axis_config),
        )

    def export_python_add_pages_as_heap():
        df_column_names_axis = DfColumnNamesAxis("time_s", "mem_total_mb")
        figure = Figure(
            axis_labels=AxisLabels("Time (s)", "Mem (MB)"),
            title="Memory page level Python",
        )
        x_axis_config = AxisConfig(
            label=figure.axis_labels.x,
            label_values=np.arange(0, 100, 10),
            max_lim=90,
            min_lim=-1,
        )
        y_axis_config = AxisConfig(
            label=figure.axis_labels.y,
            label_values=np.arange(0, 56, 4),
            max_lim=54,
            min_lim=-1,
        )
        annotate_configs = [
            AnnotateConfig(
                xy=(74, 52),
                xytext=(0.5, 0.8),
            ),
        ]
        subplots_config = SubplotsConfig(
            metrics_pathnames=[
                f"{metrics_pathname}massif.out.1814.python.add-pages-as-heap",
                f"{metrics_pathname}massif.out.1975.python.add-pages-as-heap",
                f"{metrics_pathname}massif.out.2125.python.add-pages-as-heap",
            ],
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        export_image(
            annotate_configs,
            "/tmp/metrics-massif-python-add-pages-as-heap.png",
            figure,
            get_subplots(df_column_names_axis, subplots_config),
            AxisConfigsCustom(x_axis_config, y_axis_config),
        )

    export_rust_heap_only()
    export_rust_add_stacks()
    export_rust_add_pages_as_heap()
    export_python_heap_only()
    export_python_add_stacks()
    export_python_add_pages_as_heap()
