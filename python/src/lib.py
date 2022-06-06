class Log:
    def __init__(
        self,
        remote_addr: str,
        remote_user: str,
        time_local: str,
        request: str,
        status: str,
        body_bytes_sent: str,
        http_referer: str,
        http_user_agent: str,
    ):
        self.remote_addr = remote_addr
        self.remote_user = remote_user
        self.time_local = time_local
        self.request = request
        self.status = status
        self.body_bytes_sent = body_bytes_sent
        self.http_referer = http_referer
        self.http_user_agent = http_user_agent



# https://docs.nginx.com/nginx/admin-guide/monitoring/logging/
REGEX = re.complie(r"""
    ^
    ((\d{1,3}[\.]){3}\d{1,3}) # IPv4
    \s-\s
    (.+)                      # Remote user
    \s\[
    (.+)                      # Time local
    \]\s"
    (.*)                      # Request
    "\s
    (\d{1,3})                 # Status
    \s
    (\d+)                     # Body bytes sent
    \s"
    (.+)                      # HTTP referer
    "\s"
    (.+)                      # HTTP user agent
    "
""", re.VERBOSE)


def get_log(self, line: str) -> Log:
    self._match = re.search(REGEX, line)
    return None if self._match is None else Log(
        remote_addr=self._match.group(1),
        remote_user=self._match.group(3),
        time_local=self._match.group(4),
        request=self._match.group(5),
        status=self._match.group(6),
        body_bytes_sent=self._match.group(7),
        http_referer=self._match.group(8),
        http_user_agent=self._match.group(9),
    )

