import pandas as pd


class DfToPlot:
    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        result = self._get_df_cast_values(df)
        result = self._get_df_set_total_mem(result)
        result["time_s"] = result["time"] / 1000
        result["time_minute"] = result["time_s"] / 60
        result["mem_total_kb"] = result["mem_total"] / 10**3
        result["mem_total_mb"] = result["mem_total"] / 10**6
        return result

    def _get_df_cast_values(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df
        result = result.astype(
            {
                "time": "int64",
                "mem_heap_B": "int64",
                "mem_heap_extra_B": "int64",
                "mem_stacks_B": "int64",
            }
        )
        return result

    def _get_df_set_total_mem(self, df: pd.DataFrame) -> pd.DataFrame:
        df["mem_total"] = df["mem_heap_B"] + df["mem_heap_extra_B"] + df["mem_stacks_B"]
        return df
