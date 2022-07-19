import unittest

from src import m_log


class TestFunctions(unittest.TestCase):
    def test_get_log_for_parsed_log(self):
        line = (
            '8.8.8.8 - abc [28/Nov/2021:00:18:22 +0100] "GET / HTTP/1.1" 200 77 "-"'
            ' "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"'
        )
        self.assertIsNotNone(m_log.get_log(line))

    def test_get_log_for_parsed_log_with_empty_http_user_agent(self):
        line = (
            '8.8.8.8 - abc [28/Nov/2021:00:18:22 +0100] "GET / HTTP/1.1" 200 77 "-" ""'
        )
        self.assertIsNotNone(m_log.get_log(line))

    def test_get_log_for_not_parsed_log(self):
        line = (
            '8.8.8.8 - abc [28/Nov/2021:00:18:22 +0100 "GET / HTTP/1.1" 200 77 "-"'
            ' "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"'
        )
        self.assertIsNone(m_log.get_log(line))


if __name__ == "__main__":
    unittest.main()
