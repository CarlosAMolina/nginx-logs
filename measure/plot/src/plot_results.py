from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple, Union
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from extractors import extractor
from transformers import transformer


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


if __name__ == "__main__":
    legends = ["Execution 1", "Execution 2", "Execution 3"]

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
            max_lim=0.6,
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
                xy=(0.54, 55),
                xytext=(0.545, 0.95),
            )
        ]
        subplots_config = SubplotsConfig(
            metrics_pathnames=get_metrics_pathname(
                [
                    "metrics-cpu-nginx_logs-20220828-182401.txt",
                    "metrics-cpu-nginx_logs-20220828-182501.txt",
                    "metrics-cpu-nginx_logs-20220828-182514.txt",
                ]
            ),
            legends=legends,
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
                    "metrics-cpu-python-20220828-182326.txt",
                    "metrics-cpu-python-20220828-182337.txt",
                    "metrics-cpu-python-20220828-182348.txt",
                ]
            ),
            legends=legends,
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
            label_values=np.arange(0, 10, 1),
            max_lim=9,
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
                xy=(0.85, 100),
                xytext=(0.15, 0.8),
            )
        ]
        subplots_config = SubplotsConfig(
            metrics_pathnames=get_metrics_pathname(
                [
                    "massif.out.1616.rust.heap-only",
                    "massif.out.1827.rust.heap-only",
                    "massif.out.1984.rust.heap-only",
                ]
            ),
            legends=legends,
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
            label_values=np.arange(0, 170, 10),
            max_lim=155,
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
                xy=(0.85, 100),
                xytext=(0.15, 0.8),
            ),
        ]
        subplots_config = SubplotsConfig(
            metrics_pathnames=get_metrics_pathname(
                [
                    "massif.out.1624.rust.add-stacks",
                    "massif.out.1832.rust.add-stacks",
                    "massif.out.1990.rust.add-stacks",
                ]
            ),
            legends=legends,
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
                xy=(0.4, 5),
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
                    "massif.out.1638.rust.add-pages-as-heap",
                    "massif.out.1842.rust.add-pages-as-heap",
                    "massif.out.1998.rust.add-pages-as-heap",
                ]
            ),
            legends=legends,
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
            metrics_pathnames=get_metrics_pathname(
                [
                    "massif.out.1645.python.heap-only",
                    "massif.out.1849.python.heap-only",
                    "massif.out.2008.python.heap-only",
                ]
            ),
            legends=legends,
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
            metrics_pathnames=get_metrics_pathname(
                [
                    "massif.out.1654.python.add-stacks",
                    "massif.out.1858.python.add-stacks",
                    "massif.out.2015.python.add-stacks",
                ]
            ),
            legends=legends,
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
                xy=(74, 52),
                xytext=(0.5, 0.8),
            ),
        ]
        subplots_config = SubplotsConfig(
            metrics_pathnames=get_metrics_pathname(
                [
                    "massif.out.1814.python.add-pages-as-heap",
                    "massif.out.1975.python.add-pages-as-heap",
                    "massif.out.2125.python.add-pages-as-heap",
                ]
            ),
            legends=legends,
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

    def export_execution_time():
        df = pd.DataFrame(
            {
                "language": ["Rust", "Python"],
                "time": [4, 54],
            }
        )

        # TODO remove below
        plt.figure(figsize=(9,6))
        plt.bar(
            x=df['language'],
            height=df['time'],
            color='midnightblue'
        )
        plt.title('Execution time')
        plt.savefig('/tmp/foo')
        return
        # TODO remove above
        # TODO complete code below

        df_column_names_axis = DfColumnNamesAxis("language", "time")
        figure = Figure(
            axis_labels=AxisLabels("Language", "Time (ms)"),
            title="Execution time",
        )
        x_axis_config = AxisConfig(
            label=figure.axis_labels.x,
            label_values=np.arange(0, 2, 1),
            max_lim=2,
            min_lim=-1,
        )
        y_axis_config = AxisConfig(
            label=figure.axis_labels.y,
            label_values=np.arange(0, 60, 10),
            max_lim=60,
            min_lim=0,
        )
        subplots_config = SubplotsConfig(
            metrics_pathnames=get_metrics_pathname(
                [
                    "massif.out.1814.python.add-pages-as-heap",
                    "massif.out.1975.python.add-pages-as-heap",
                    "massif.out.2125.python.add-pages-as-heap",
                ]
            ),
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        export_image(
            None,
            "metrics-memory-massif-python-add-pages-as-heap.png",
            figure,
            get_subplots(df_column_names_axis, subplots_config),
            AxisConfigs(x_axis_config, y_axis_config),
        )

    # TODO export_cpu_rust()
    # TODO export_cpu_python()
    # TODO export_memory_rust_heap_only()
    # TODO export_memory_rust_add_stacks()
    # TODO export_memory_rust_add_pages_as_heap()
    # TODO export_memory_python_heap_only()
    # TODO export_memory_python_add_stacks()
    # TODO export_memory_python_add_pages_as_heap()
    export_execution_time()
