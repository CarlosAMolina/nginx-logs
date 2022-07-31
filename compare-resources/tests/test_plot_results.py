import unittest

from src import plot_results


class TestFileParser(unittest.TestCase):
    def test_get_regex_result_cpu_mem_line_starts_with_blank_space(self):
        line = " 0.0  0.1"
        result = plot_results.FileParser("")._get_regex_result_cpu_mem(line)
        self.assertEqual("0.0", result["cpu"])
        self.assertEqual("0.1", result["mem"])

    def test_get_regex_result_cpu_mem_line_does_not_start_with_blank_space(self):
        line = "11.0  1.6"
        result = plot_results.FileParser("")._get_regex_result_cpu_mem(line)
        self.assertEqual("11.0", result["cpu"])
        self.assertEqual("1.6", result["mem"])

    def test_get_regex_result_cpu_mem_line_if_cpu_does_not_have_decimals(self):
        line = " 100 2.3"
        result = plot_results.FileParser("")._get_regex_result_cpu_mem(line)
        self.assertEqual("100", result["cpu"])
        self.assertEqual("2.3", result["mem"])

    def test_get_regex_result_cpu_mem_line_if_mem_does_not_have_decimals(self):
        line = " 2.3 100"
        result = plot_results.FileParser("")._get_regex_result_cpu_mem(line)
        self.assertEqual("2.3", result["cpu"])
        self.assertEqual("100", result["mem"])

    def test_get_regex_result_cpu_mem_line_if_no_decimals(self):
        line = " 100 100"
        result = plot_results.FileParser("")._get_regex_result_cpu_mem(line)
        self.assertEqual("100", result["cpu"])
        self.assertEqual("100", result["mem"])

    def test_get_regex_result_date(self):
        line = "20:36:58.908305938"
        result = plot_results.FileParser("")._get_regex_result_date(line)
        self.assertEqual("20", result["hour"])
        self.assertEqual("36", result["minute"])
        self.assertEqual("58", result["second"])
        self.assertEqual("908305938", result["microsecond"])


if __name__ == "__main__":
    unittest.main()
