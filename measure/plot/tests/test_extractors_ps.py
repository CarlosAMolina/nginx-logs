from pathlib import Path
import unittest

import pandas as pd

from src.extractors import ps


class TestLineParser(unittest.TestCase):
    def test_regex_result_values_line_starts_with_blank_space(self):
        line = " 0.0  0.1 20:36:58.908305938"
        result = ps.LineParser(line)._regex_result_values
        self.assertEqual("0.0", result["cpu"])
        self.assertEqual("0.1", result["mem"])
        self.assertEqual("20:36:58.908305938", result["date"])

    def test_regex_result_values_line_does_not_start_with_blank_space(self):
        line = "11.0  1.6 20:36:58.908305938"
        result = ps.LineParser(line)._regex_result_values
        self.assertEqual("11.0", result["cpu"])
        self.assertEqual("1.6", result["mem"])
        self.assertEqual("20:36:58.908305938", result["date"])

    def test_regex_result_values_line_if_cpu_does_not_have_decimals(self):
        line = " 100 2.3 20:36:58.908305938"
        result = ps.LineParser(line)._regex_result_values
        self.assertEqual("100", result["cpu"])
        self.assertEqual("2.3", result["mem"])
        self.assertEqual("20:36:58.908305938", result["date"])

    def test_regex_result_values_line_if_mem_does_not_have_decimals(self):
        line = " 2.3 100 20:36:58.908305938"
        result = ps.LineParser(line)._regex_result_values
        self.assertEqual("2.3", result["cpu"])
        self.assertEqual("100", result["mem"])
        self.assertEqual("20:36:58.908305938", result["date"])

    def test_regex_result_values_line_if_no_decimals(self):
        line = " 100 100 20:36:58.908305938"
        result = ps.LineParser(line)._regex_result_values
        self.assertEqual("100", result["cpu"])
        self.assertEqual("100", result["mem"])
        self.assertEqual("20:36:58.908305938", result["date"])


class TestFileParser(unittest.TestCase):
    def test_df(self):
        this_script_path = Path(__file__).parent.absolute()
        file_path = this_script_path.joinpath("files/metrics-ps.txt")
        parser = ps.FileParser(str(file_path))
        df = parser.df
        result_expected = pd.DataFrame(
            {
                "cpu_percentage": {
                    0: "0.0",
                    1: "0.0",
                    2: "0.0",
                    3: "57.0",
                    4: "58.0",
                    5: "55.0",
                },
                "mem_percentage": {
                    0: "0.0",
                    1: "0.0",
                    2: "0.0",
                    3: "0.0",
                    4: "0.0",
                    5: "0.0",
                },
                "time": {
                    0: "08:19:52.307366485",
                    1: "08:19:52.319993490",
                    2: "08:19:52.332874018",
                    3: "08:19:52.345512395",
                    4: "08:19:52.358329883",
                    5: "08:19:52.371161090",
                },
            }
        )
        self.assertTrue(result_expected.equals(df))


if __name__ == "__main__":
    unittest.main()
