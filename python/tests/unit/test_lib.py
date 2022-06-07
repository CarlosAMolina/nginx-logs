import unittest

from src import lib


class TestFunctions(unittest.TestCase):
    def test_get_log_filenames_sort_reverse(self):
        filenames = [
            "foo.txt",
            "access.log",
            "access.log.5",
            "access.log.2",
            "access.log.10",
            "access.log.1",
        ]
        self.assertEqual(
            [
                "access.log.10",
                "access.log.5",
                "access.log.2",
                "access.log.1",
                "access.log",
            ],
            lib.get_log_filenames_sort_reverse(filenames),
        )

    def test_get_log_for_parsed_log(self):
        line = (
            '8.8.8.8 - abc [28/Nov/2021:00:18:22 +0100] "GET / HTTP/1.1" 200 77 "-"'
            ' "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"'
        )
        self.assertIsNotNone(lib.get_log(line))

    def test_get_log_for_not_parsed_log(self):
        line = (
            '8.8.8.8 - abc [28/Nov/2021:00:18:22 +0100 "GET / HTTP/1.1" 200 77 "-"'
            ' "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"'
        )
        self.assertIsNone(lib.get_log(line))


if __name__ == "__main__":
    unittest.main()
