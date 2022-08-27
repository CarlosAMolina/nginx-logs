from pathlib import Path
import unittest

import pandas as pd

from src.extractors import massif


class TestFileParser(unittest.TestCase):
    def test_df(self):
        this_script_path = Path(__file__).parent.absolute()
        file_path = this_script_path.joinpath("files/massif.out.1")
        parser = massif.FileParser(str(file_path))
        df = parser.df
        result_expected = pd.DataFrame(
            {
                "time": {"0": "0", "1": "6394", "2": "111626"},
                "mem_heap_B": {"0": "0", "1": "1564632", "2": "1540817"},
                "mem_heap_extra_B": {"0": "0", "1": "14680", "2": "14615"},
                "mem_stacks_B": {"0": "0", "1": "5968", "2": "3280"},
                "heap_tree": {"0": "empty", "1": "peak", "2": "empty"},
            }
        )
        self.assertTrue(result_expected.equals(df))


if __name__ == "__main__":
    unittest.main()
