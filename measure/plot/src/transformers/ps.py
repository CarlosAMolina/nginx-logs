import datetime

import pandas as pd


class DfToPlot:
    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        result = self._get_df_cast_values(df)
        result = self._get_df_set_time_elapsed(result)
        return result

    def _get_df_cast_values(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df
        result = result.astype(
            {
                "cpu_percentage": "float64",
                "mem_percentage": "float64",
            }
        )
        result["time"] = pd.to_timedelta(result["time"])
        return result

    def _get_df_set_time_elapsed(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        https://docs.python.org/3/library/datetime.html#datetime.timedelta.total_seconds
        """
        df["time_elapsed"] = df["time"] - df["time"].min()
        df["time_elapsed"] = df["time_elapsed"] / datetime.timedelta(microseconds=1)
        df["time_elapsed"] = df["time_elapsed"] / 10**6
        return df
