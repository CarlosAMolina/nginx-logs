import unittest

from src import lib


class TestFunctions(unittest.TestCase):
    def test_get_log_filenames_sort_reverse(self):
        filenames = [
            "foo.txt",
            "access.log",
            "access.log.5.gz",
            "access.log.2",
            "access.log.10.gz",
            "access.log.1.gz",
        ]
        self.assertEqual(
            [
                "access.log.10.gz",
                "access.log.5.gz",
                "access.log.2",
                "access.log.1.gz",
                "access.log",
            ],
            lib.get_log_filenames_sort_reverse(filenames),
        )

    def test_get_filenames_and_numbers(self):
        filenames = [
            "foo.txt",
            "access.log",
            "access.log.5.gz",
            "access.log.2",
            "access.log.10.gz",
            "access.log.1.gz",
        ]
        self.assertEqual(
            {
                10: "access.log.10.gz",
                5: "access.log.5.gz",
                2: "access.log.2",
                1: "access.log.1.gz",
                0: "access.log",
            },
            lib.get_filenames_and_numbers(filenames),
        )

    def test_get_filename_possible_number(self):
        self.assertEqual("0", lib.get_filename_possible_number("access.log"))
        self.assertEqual("2", lib.get_filename_possible_number("access.log.2"))
        self.assertEqual("2", lib.get_filename_possible_number("access.log.2.gz"))

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
