import pandas as pd

from transformers import ps as ps_transformer, massif as massif_transformer, execution_time as execution_time_extractor


def get_df_transformed(metrics_pathname: str, df: pd.DataFrame) -> pd.DataFrame:
    if "massif" in metrics_pathname:
        return massif_transformer.DfToPlot()(df)
    elif "execution-time" in metrics_pathname:
        return execution_time_extractor.DfToPlot()(df)
    return ps_transformer.DfToPlot()(df)
