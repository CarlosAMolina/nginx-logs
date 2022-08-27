from pathlib import Path
import sys
import unittest

project_main_path = Path(__file__).parent.parent
sys.path.append(str(project_main_path.joinpath("src")))

import pandas as pd

from src import plot_results


class TestRound(unittest.TestCase):
    def test_get_round_up_to_nearest_ten(self):
        self.assertEqual(20, plot_results.Round().get_round_up_to_nearest_ten(11))

    def test_get_round_up_to_nearest_integer(self) -> int:
        self.assertEqual(2, plot_results.Round().get_round_up_to_nearest_integer(1.1))

    def test_get_round_up_to_nearest_decimal(self) -> float:
        self.assertEqual(
            1.2, plot_results.Round().get_round_up_to_nearest_decimal(1.12)
        )
        self.assertEqual(0.9, plot_results.Round().get_round_up_to_nearest_decimal(0.8))


class TestXAxisConfigCalculator(unittest.TestCase):
    def test_max_lim_for_max_value_lower_than_1(self):
        values = [pd.Series([0, 0.8])]
        xlims = plot_results.XAxisConfigCalculator("", values)
        self.assertEqual(0.9, xlims._max_lim)

    def test_min_lim_for_max_value_higher_than_1(self):
        values = [pd.Series([0, 16.5])]
        xlims = plot_results.XAxisConfigCalculator("", values)
        self.assertEqual(17, xlims._max_lim)


class TestYAxisConfigCalculator(unittest.TestCase):
    def test_max_and_min_for_float_values_between_0_dot_02_and_100(self):
        values = [pd.Series([0, 76.5])]
        ylims = plot_results.YAxisConfigCalculator("", values)
        self.assertEqual(-10, ylims._min_lim)
        self.assertEqual(80, ylims._max_lim)

    def test_max_and_min_for_float_values_higher_than_100_and_label_step_remainder(
        self,
    ):
        values = [pd.Series([0, 124.5])]
        ylims = plot_results.YAxisConfigCalculator("", values)
        self.assertEqual(-20, ylims._min_lim)
        self.assertEqual(140, ylims._max_lim)

    def test_max_and_min_for_float_values_higher_than_100_and_not_label_step_remainder(
        self,
    ):
        values = [pd.Series([0, 134.5])]
        ylims = plot_results.YAxisConfigCalculator("", values)
        self.assertEqual(-20, ylims._min_lim)
        self.assertEqual(140, ylims._max_lim)

    def test_max_and_min_for_float_values_lower_than_0_dot_02(self):
        values = [pd.Series([0, 0.01])]
        ylims = plot_results.YAxisConfigCalculator("", values)
        self.assertEqual(-0.02, ylims._min_lim)
        self.assertEqual(0.02, ylims._max_lim)


class TestRunCompletePlot(unittest.TestCase):
    def test_plot_ps_metrics(self):
        df_column_names_axis = plot_results.DfColumnNamesAxis(
            "time_elapsed", "cpu_percentage"
        )
        legends = ["Execution 1", "Execution 2", "Execution 3"]
        this_script_path = plot_results.Path(__file__).parent.absolute()
        files_path = this_script_path.joinpath("files")
        subplots_config = plot_results.SubplotsConfig(
            metrics_pathnames=[
                str(files_path.joinpath(filename))
                for filename in ["metrics-ps.txt"] * 3
            ],
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        plot_results.export_image(
            "/tmp/metrics-ps.png",
            plot_results.Figure(plot_results.AxisLabels("Time (s)", "CPU (%)")),
            plot_results.get_subplots(df_column_names_axis, subplots_config),
        )

    def test_plot_massif_metrics(self):
        df_column_names_axis = plot_results.DfColumnNamesAxis("time", "mem_total")
        legends = ["Execution 1", "Execution 2", "Execution 3"]
        this_script_path = plot_results.Path(__file__).parent.absolute()
        files_path = this_script_path.joinpath("files")
        subplots_config = plot_results.SubplotsConfig(
            metrics_pathnames=[
                str(files_path.joinpath(filename)) for filename in ["massif.out.1"] * 3
            ],
            legends=legends,
            colors=["b", "limegreen", "r"],
            markers=["o", "o", "o"],
            markerssize=[4.5, 2.5, 0.7],
        )
        plot_results.export_image(
            "/tmp/metrics-massif.png",
            plot_results.Figure(plot_results.AxisLabels("Time (s)", "Mem (B)")),
            plot_results.get_subplots(df_column_names_axis, subplots_config),
        )


if __name__ == "__main__":
    unittest.main()
