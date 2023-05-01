import pandas as pd


class DfToPlot:
    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df
        result = self._get_df_set_average(result)
        return result

    def _get_df_set_average(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df
        result["time_average"] = result.mean(axis="columns", numeric_only=True)
        result["time_average"] = result["time_average"].round(decimals=3)
        return result
