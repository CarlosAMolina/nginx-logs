from pathlib import Path
import sys
import unittest

project_main_path = Path(__file__).parent.parent
sys.path.append(str(project_main_path.joinpath("src")))

import numpy as np

from src import plot_results


class TestRunCompletePlot(unittest.TestCase):
    def setUp(self):
        this_script_path = plot_results.Path(__file__).parent.absolute()
        self.files_path = this_script_path.joinpath("files")

    def test_plot_ps_metrics(self):
        df_column_names_axis = plot_results.DfColumnNamesAxis(
            "time_elapsed", "cpu_percentage"
        )
        legends = ["Execution 1", "Execution 2", "Execution 3"]
        figure = plot_results.Figure(
            axis_labels=plot_results.AxisLabels("Time (s)", "CPU (%)"),
            title="CPU",
        )
        x_axis_config = plot_results.AxisConfig(
            label=figure.axis_labels.x,
            label_values=np.arange(0, 0.08, 0.01),
            max_lim=0.07,
            min_lim=-0.001,
        )
        y_axis_config = plot_results.AxisConfig(
            label=figure.axis_labels.y,
            label_values=np.arange(0, 70, 10),
            max_lim=60,
            min_lim=-1,
        )
        annotate_configs = [
            plot_results.AnnotateConfig(
                xy=(0.05, 55),
                xytext=(0.55, 0.8),
            ),
        ]
        subplots_config = plot_results.SubplotsConfig(
            metrics_pathnames=[
                str(self.files_path.joinpath(filename))
                for filename in ["metrics-ps.txt"] * 3
            ],
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        plot_results.export_image(
            annotate_configs,
            "/tmp/metrics-ps.png",
            figure,
            plot_results.get_subplots(df_column_names_axis, subplots_config),
            plot_results.AxisConfigs(x_axis_config, y_axis_config),
        )

    def test_plot_massif_metrics(self):
        df_column_names_axis = plot_results.DfColumnNamesAxis("time", "mem_total")
        legends = ["Execution 1", "Execution 2", "Execution 3"]
        figure = plot_results.Figure(
            axis_labels=plot_results.AxisLabels("Time (s)", "Mem (B)"),
            title="Mem",
        )
        x_axis_config = plot_results.AxisConfig(
            label=figure.axis_labels.x,
            label_values=np.arange(0, 140_000, 20_000),
            max_lim=120_000,
            min_lim=-2_500,
        )
        y_axis_config = plot_results.AxisConfig(
            label=figure.axis_labels.y,
            label_values=np.arange(0, 1.8 * 10**6, 0.2 * 10**6),
            max_lim=1.6 * 10**6,
            min_lim=-50_000,
        )
        annotate_configs = [
            plot_results.AnnotateConfig(
                xy=(6_000, 1.55 * 10**6),
                xytext=(0.5, 0.8),
            ),
        ]
        subplots_config = plot_results.SubplotsConfig(
            metrics_pathnames=[
                str(self.files_path.joinpath(filename))
                for filename in ["massif.out.1"] * 3
            ],
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        plot_results.export_image(
            annotate_configs,
            "/tmp/metrics-massif.png",
            figure,
            plot_results.get_subplots(df_column_names_axis, subplots_config),
            plot_results.AxisConfigs(x_axis_config, y_axis_config),
        )


if __name__ == "__main__":
    unittest.main()
