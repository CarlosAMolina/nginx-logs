import pandas as pd


class FileParser:
    def __init__(self, pathname: str):
        self._pathname = pathname

    @property
    def df(self) -> pd.DataFrame:
        return pd.read_csv(self._pathname)  

