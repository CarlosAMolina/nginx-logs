import pandas as pd


class DfToPlot:
    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df
        result = self._get_df_set_average(result)
        return result

    def _get_df_set_average(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df
        result["average_s"] = result.mean(axis='columns', numeric_only=True)
        breakpoint()
        return result

