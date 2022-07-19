import unittest

from src import filter_file


class TestFilenamesFilter(unittest.TestCase):
    def setUp(self):
        self._class = filter_file.FilenamesFilter()

    def test_get_log_filenames_sort_reverse(self):
        filenames = [
            "foo.txt",
            "error.log.111",
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
            self._class._get_log_filenames_sort_reverse(filenames),
        )

    def test_get_numbers_and_filenames(self):
        filenames = [
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
            self._class._get_numbers_and_filenames(filenames),
        )

    def test_get_filename_possible_number(self):
        self.assertEqual("0", self._class._get_filename_possible_number("access.log"))
        self.assertEqual("2", self._class._get_filename_possible_number("access.log.2"))
        self.assertEqual(
            "2", self._class._get_filename_possible_number("access.log.2.gz")
        )


if __name__ == "__main__":
    unittest.main()
