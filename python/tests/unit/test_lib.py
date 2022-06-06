import datetime
import unittest

from src import lib


class TestFunctions(unittest.TestCase):
    def test_get_log(self):
        line = (
            '8.8.8.8 - abc [28/Nov/2021:00:18:22 +0100] "GET / HTTP/1.1" 200 77 "-"'
            ' "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"'
        )
        self.assertIsNotNone(lib.get_log(line))


if __name__ == "__main__":
    unittest.main()
