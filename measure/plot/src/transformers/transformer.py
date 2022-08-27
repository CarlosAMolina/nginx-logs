import pandas as pd

from transformers import ps as ps_transformer, massif as massif_transformer


def get_df_transformed(metrics_pathname: str, df: pd.DataFrame) -> pd.DataFrame:
    if "massif" in metrics_pathname:
        return massif_transformer.DfToPlot()(df)
    return ps_transformer.DfToPlot()(df)
