import unittest

import pandas as pd

from src.transformers import ps


class TestDfToPlot(unittest.TestCase):
    def test_df(self):
        df = pd.DataFrame(
            {
                "cpu_percentage": {
                    0: "0.0",
                    1: "0.0",
                    2: "0.0",
                    3: "57.0",
                    4: "58.0",
                    5: "58.0",
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
                    5: "08:19:54.371161090",
                },
            }
        )
        result_expected = pd.DataFrame(
            {
                "cpu_percentage": {
                    0: 0.0,
                    1: 0.0,
                    2: 0.0,
                    3: 57.0,
                    4: 58.0,
                    5: 58.0,
                },
                "mem_percentage": {
                    0: 0.0,
                    1: 0.0,
                    2: 0.0,
                    3: 0.0,
                    4: 0.0,
                    5: 0.0,
                },
                "time": {
                    0: "08:19:52.307366485",
                    1: "08:19:52.319993490",
                    2: "08:19:52.332874018",
                    3: "08:19:52.345512395",
                    4: "08:19:52.358329883",
                    5: "08:19:54.371161090",
                },
                "time_elapsed": {
                    0: 0.0,
                    1: 0.012627004999999998,
                    2: 0.025507533,
                    3: 0.038145910000000005,
                    4: 0.050963398,
                    5: 2.063794605,
                },
            }
        )
        result_expected["time"] = pd.to_timedelta(result_expected["time"])
        get_df_to_plot = ps.DfToPlot()
        df = get_df_to_plot(df)
        self.assertTrue(
            result_expected.drop(columns="time").equals(df.drop(columns="time"))
        )


if __name__ == "__main__":
    unittest.main()
