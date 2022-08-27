import pandas as pd

from extractors import ps as ps_extractor, massif as massif_extractor


def get_df_from_pathname(metrics_pathname: str) -> pd.DataFrame:
    if "massif" in metrics_pathname:
        return massif_extractor.FileParser(metrics_pathname).df
    return ps_extractor.FileParser(metrics_pathname).df
