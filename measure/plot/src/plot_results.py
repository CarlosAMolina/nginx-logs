import sys
from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from extractors import extractor
from transformers import transformer


LEGENDS = ["Execution 1", "Execution 2", "Execution 3"]


class AxisConfig(NamedTuple):
    label: str
    label_values: Optional[Union[list, np.ndarray]]
    max_lim: Union[int, float]
    min_lim: Union[int, float]


class AxisConfigs(NamedTuple):
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
    annotate_configs: Optional[AnnotateConfigs]
    subplots: Subplots
    axis_configs: Optional[AxisConfigs]
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
        if plot.axis_configs is not None:
            if plot.axis_configs.x is not None:
                ax.set_xlabel(plot.axis_configs.x.label)
                plt.xticks(plot.axis_configs.x.label_values)
                ax.set_xlim(plot.axis_configs.x.min_lim, plot.axis_configs.x.max_lim)
                ax.set_xbound(
                    lower=plot.axis_configs.x.min_lim, upper=plot.axis_configs.x.max_lim
                )
            if plot.axis_configs.y is not None:
                ax.set_ylabel(plot.axis_configs.y.label)
                plt.yticks(plot.axis_configs.y.label_values)
                ax.set_ylim(
                    bottom=plot.axis_configs.y.min_lim, top=plot.axis_configs.y.max_lim
                )
                ax.set_ybound(
                    lower=plot.axis_configs.y.min_lim, upper=plot.axis_configs.y.max_lim
                )
        subplots_y_axis_values = SubplotsAxisValues(
            [subplot.y_axis_values for subplot in plot.subplots]
        )
        if plot.annotate_configs is not None:
            for annotate_config in plot.annotate_configs:
                ax.annotate(
                    f"Max {subplots_y_axis_values.max_value}",
                    xy=annotate_config.xy,
                    xycoords="data",
                    xytext=annotate_config.xytext,
                    textcoords="axes fraction",
                    arrowprops=dict(
                        facecolor="black", shrink=0.05, width=2, headwidth=8
                    ),
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
        # print_top_memory(df)
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


def print_top_memory(df: pd.DataFrame):
    print(df.sort_values(by=["mem_total"], ascending=False).head(3))


def get_df_from_file(metrics_pathname: str) -> pd.DataFrame:
    result = extractor.get_df_from_pathname(metrics_pathname)
    return transformer.get_df_transformed(metrics_pathname, result)


def export_image(
    annotate_configs: Optional[AnnotateConfigs],
    image_filename: str,
    figure: Figure,
    subplots: Subplots,
    axis_configs: Optional[AxisConfigs] = None,
):
    ExportImage().export_image(
        str(ResultsPath().get_image_pathname(image_filename)),
        Plot(
            annotate_configs,
            subplots,
            axis_configs,
            figure.title,
        ),
    )


def export_execution_time():
    figure = Figure(
        axis_labels=AxisLabels("Language and function", "Time (s)"),
        title="Execution time (average)",
    )
    df = get_df_from_file(get_metrics_pathname(["execution-time.csv"])[0])
    # https://pythonguides.com/matplotlib-plot-bar-chart/
    bar_width = 0.5
    executions_count = 4
    x_pos = np.arange(1, 2 * executions_count, 2)
    values = df["time_average"]
    _, ax = plt.subplots()
    ax.bar(
        x_pos + bar_width / 3,
        values,
        color="b",
        width=bar_width,
        edgecolor="k",
    )
    # https://stackoverflow.com/questions/28931224/how-to-add-value-labels-on-a-bar-chart
    ax.bar_label(ax.containers[0], label_type="edge")
    TITLE_FONTSIZE = None
    LABEL_FONTSIZE = None
    TICKS_FONTSIZE = None
    x_grid_labels = df["description"]
    y_max = 13
    y_grid_labels = np.arange(0, y_max, 2)
    ax.set_ylim(bottom=0, top=y_max)
    plt.xticks(
        x_pos + bar_width / 2, x_grid_labels, fontsize=TICKS_FONTSIZE, rotation=0
    )
    plt.yticks(y_grid_labels, fontsize=TICKS_FONTSIZE)
    plt.title(figure.title, fontsize=TITLE_FONTSIZE)
    plt.xlabel(figure.axis_labels.x, fontsize=LABEL_FONTSIZE)
    plt.ylabel(figure.axis_labels.y, fontsize=LABEL_FONTSIZE)
    plt.grid(color="black", axis="y", linestyle="-", linewidth=0.1)
    path_name = "/tmp/execution-time.png"
    print(f"Init export to {path_name}")
    plt.savefig(path_name, dpi=300)


def get_metrics_pathname(metrics_filenames: List[str]) -> List[str]:
    this_script_path = Path(__file__).parent.absolute()
    metrics_path = this_script_path.joinpath("../../measure/results/")
    return [str(metrics_path.joinpath(filename)) for filename in metrics_filenames]


def export_cpu_rust():
    df_column_names_axis = DfColumnNamesAxis("time_elapsed", "cpu_percentage")
    figure = Figure(
        axis_labels=AxisLabels("Time (s)", "CPU (%)"),
        title="CPU Rust",
    )
    x_axis_config = AxisConfig(
        label=figure.axis_labels.x,
        label_values=np.arange(0, 0.7, 0.1),
        max_lim=0.4,
        min_lim=-0.01,
    )
    y_axis_config = AxisConfig(
        label=figure.axis_labels.y,
        label_values=np.arange(0, 70, 10),
        max_lim=60,
        min_lim=-1,
    )
    annotate_configs = [
        AnnotateConfig(
            xy=(0.39, 50),
            xytext=(0.8, 0.6),
        )
    ]
    subplots_config = SubplotsConfig(
        metrics_pathnames=get_metrics_pathname(
            [
                "metrics-cpu-rust-measure-1.txt",
                "metrics-cpu-rust-measure-2.txt",
                "metrics-cpu-rust-measure-3.txt",
            ]
        ),
        legends=LEGENDS,
        colors=["b", "limegreen", "r"],
        markers=["o", "o", "o"],
        markerssize=[4.5, 2.5, 0.7],
    )
    export_image(
        annotate_configs,
        "metrics-cpu-rust.png",
        figure,
        get_subplots(df_column_names_axis, subplots_config),
        AxisConfigs(x_axis_config, y_axis_config),
    )


def export_cpu_python():
    df_column_names_axis = DfColumnNamesAxis("time_elapsed", "cpu_percentage")
    figure = Figure(
        axis_labels=AxisLabels("Time (s)", "CPU (%)"),
        title="CPU Python",
    )
    x_axis_config = AxisConfig(
        label=figure.axis_labels.x,
        label_values=np.arange(0, 12, 1),
        max_lim=11,
        min_lim=-0.3,
    )
    y_axis_config = AxisConfig(
        label=figure.axis_labels.y,
        label_values=np.arange(0, 180, 20),
        max_lim=170,
        min_lim=-5,
    )
    annotate_configs = [
        AnnotateConfig(
            xy=(1.9, 165),
            xytext=(0.3, 0.9),
        )
    ]
    subplots_config = SubplotsConfig(
        metrics_pathnames=get_metrics_pathname(
            [
                "metrics-cpu-python-measure-1.txt",
                "metrics-cpu-python-measure-2.txt",
                "metrics-cpu-python-measure-3.txt",
            ]
        ),
        legends=LEGENDS,
        colors=["b", "limegreen", "r"],
        markers=["o", "o", "o"],
        markerssize=[4.5, 2.5, 0.7],
    )
    export_image(
        annotate_configs,
        "metrics-cpu-python.png",
        figure,
        get_subplots(df_column_names_axis, subplots_config),
        AxisConfigs(x_axis_config, y_axis_config),
    )


def export_memory_rust_heap_only():
    df_column_names_axis = DfColumnNamesAxis("time_s", "mem_total_kb")
    figure = Figure(
        axis_labels=AxisLabels("Time (s)", "Mem (kB)"),
        title="Memory heap Rust",
    )
    x_axis_config = AxisConfig(
        label=figure.axis_labels.x,
        label_values=np.arange(0, 11, 1),
        max_lim=10,
        min_lim=-0.5,
    )
    y_axis_config = AxisConfig(
        label=figure.axis_labels.y,
        label_values=np.arange(-10, 120, 10),
        max_lim=110,
        min_lim=-5,
    )
    annotate_configs = [
        AnnotateConfig(
            xy=(0.43, 99),
            xytext=(0.15, 0.8),
        )
    ]
    subplots_config = SubplotsConfig(
        metrics_pathnames=get_metrics_pathname(
            [
                "massif.out.measure-1.rust.heap-only",
                "massif.out.measure-2.rust.heap-only",
                "massif.out.measure-3.rust.heap-only",
            ]
        ),
        legends=LEGENDS,
        colors=["b", "limegreen", "r"],
        markers=["o", "o", "o"],
        markerssize=[4.5, 2.5, 0.7],
    )
    export_image(
        annotate_configs,
        "metrics-memory-massif-rust-heap-only.png",
        figure,
        get_subplots(df_column_names_axis, subplots_config),
        AxisConfigs(x_axis_config, y_axis_config),
    )


def export_memory_rust_add_stacks():
    df_column_names_axis = DfColumnNamesAxis("time_s", "mem_total_kb")
    figure = Figure(
        axis_labels=AxisLabels("Time (s)", "Mem (kB)"),
        title="Memory heap and stack Rust",
    )
    x_axis_config = AxisConfig(
        label=figure.axis_labels.x,
        label_values=np.arange(0, 270, 20),
        max_lim=260,
        min_lim=-5,
    )
    y_axis_config = AxisConfig(
        label=figure.axis_labels.y,
        label_values=np.arange(-10, 120, 10),
        max_lim=110,
        min_lim=-5,
    )
    annotate_configs = [
        AnnotateConfig(
            xy=(12.0, 100),
            xytext=(0.15, 0.8),
        ),
    ]
    subplots_config = SubplotsConfig(
        metrics_pathnames=get_metrics_pathname(
            [
                "massif.out.measure-1.rust.add-stacks",
                "massif.out.measure-2.rust.add-stacks",
                "massif.out.measure-3.rust.add-stacks",
            ]
        ),
        legends=LEGENDS,
        colors=["b", "limegreen", "r"],
        markers=["o", "o", "o"],
        markerssize=[4.5, 2.5, 0.7],
    )
    export_image(
        annotate_configs,
        "metrics-memory-massif-rust-add_stacks.png",
        figure,
        get_subplots(df_column_names_axis, subplots_config),
        AxisConfigs(x_axis_config, y_axis_config),
    )


def export_memory_rust_add_pages_as_heap():
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
            xy=(0.45, 5),
            xytext=(0.15, 0.8),
        ),
        AnnotateConfig(
            xy=(4, 5),
            xytext=(0.15, 0.8),
        ),
    ]
    subplots_config = SubplotsConfig(
        metrics_pathnames=get_metrics_pathname(
            [
                "massif.out.measure-1.rust.add-pages-as-heap",
                "massif.out.measure-2.rust.add-pages-as-heap",
                "massif.out.measure-3.rust.add-pages-as-heap",
            ]
        ),
        legends=LEGENDS,
        colors=["b", "limegreen", "r"],
        markers=["o", "o", "o"],
        markerssize=[4.5, 2.5, 0.7],
    )
    export_image(
        annotate_configs,
        "metrics-memory-massif-rust-add-pages-as-heap.png",
        figure,
        get_subplots(df_column_names_axis, subplots_config),
        AxisConfigs(x_axis_config, y_axis_config),
    )


def export_memory_python_heap_only():
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
        label_values=np.arange(0, 29, 2),
        max_lim=28.0,
        min_lim=-0.5,
    )
    annotate_configs = [
        AnnotateConfig(
            xy=(74, 26),
            xytext=(0.5, 0.84),
        ),
    ]
    subplots_config = SubplotsConfig(
        metrics_pathnames=get_metrics_pathname(
            [
                "massif.out.measure-1.python.heap-only",
                "massif.out.measure-2.python.heap-only",
                "massif.out.measure-3.python.heap-only",
            ]
        ),
        legends=LEGENDS,
        colors=["b", "limegreen", "r"],
        markers=["o", "o", "o"],
        markerssize=[4.5, 2.5, 0.7],
    )
    export_image(
        annotate_configs,
        "metrics-memory-massif-python-heap-only.png",
        figure,
        get_subplots(df_column_names_axis, subplots_config),
        AxisConfigs(x_axis_config, y_axis_config),
    )


def export_memory_python_add_stacks():
    df_column_names_axis = DfColumnNamesAxis("time_minute", "mem_total_mb")
    figure = Figure(
        axis_labels=AxisLabels("Time (min)", "Mem (MB)"),
        title="Memory heap and stack Python",
    )
    x_axis_config = AxisConfig(
        label=figure.axis_labels.x,
        label_values=np.arange(0, 105, 10),
        max_lim=100,
        min_lim=-0.5,
    )
    y_axis_config = AxisConfig(
        label=figure.axis_labels.y,
        label_values=np.arange(0, 30, 2),
        max_lim=28.0,
        min_lim=-0.5,
    )
    annotate_configs = [
        AnnotateConfig(
            xy=(83, 26),
            xytext=(0.5, 0.84),
        ),
    ]
    subplots_config = SubplotsConfig(
        metrics_pathnames=get_metrics_pathname(
            [
                "massif.out.measure-1.python.add-stacks",
                "massif.out.measure-2.python.add-stacks",
                "massif.out.measure-3.python.add-stacks",
            ]
        ),
        legends=LEGENDS,
        colors=["b", "limegreen", "r"],
        markers=["o", "o", "o"],
        markerssize=[4.5, 2.5, 0.7],
    )
    export_image(
        annotate_configs,
        "metrics-memory-massif-python-add_stacks.png",
        figure,
        get_subplots(df_column_names_axis, subplots_config),
        AxisConfigs(x_axis_config, y_axis_config),
    )


def export_memory_python_add_pages_as_heap():
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
            xy=(73, 52),
            xytext=(0.5, 0.87),
        ),
    ]
    subplots_config = SubplotsConfig(
        metrics_pathnames=get_metrics_pathname(
            [
                "massif.out.measure-1.python.add-pages-as-heap",
                "massif.out.measure-2.python.add-pages-as-heap",
                "massif.out.measure-3.python.add-pages-as-heap",
            ]
        ),
        legends=LEGENDS,
        colors=["b", "limegreen", "r"],
        markers=["o", "o", "o"],
        markerssize=[4.5, 2.5, 0.7],
    )
    export_image(
        annotate_configs,
        "metrics-memory-massif-python-add-pages-as-heap.png",
        figure,
        get_subplots(df_column_names_axis, subplots_config),
        AxisConfigs(x_axis_config, y_axis_config),
    )


if __name__ == "__main__":
    what_to_plot = "" if len(sys.argv) == 1 else sys.argv[1]
    if what_to_plot == "time":
        print("[DEBUG] Init execution time")
        export_execution_time()
    elif what_to_plot == "memory":
        print("[DEBUG] Init memory")
        export_memory_rust_heap_only()
        export_memory_rust_add_stacks()
        export_memory_rust_add_pages_as_heap()
        export_memory_python_heap_only()
        export_memory_python_add_stacks()
        export_memory_python_add_pages_as_heap()
    elif what_to_plot == "cpu":
        print("[DEBUG] Init CPU")
        export_cpu_rust()
        export_cpu_python()
    else:
        if len(sys.argv) == 1:
            error_msg = "No arguments supplied"
        else:
            error_msg = f"Invalid argument: {what_to_plot}"
        error_msg += ". Valid arguments: time, memory, cpu"
        raise ValueError(error_msg)
