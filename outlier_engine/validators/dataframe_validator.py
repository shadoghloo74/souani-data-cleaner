"""DataFrame validator module for Outlier Engine."""

import pandas as pd
from outlier_engine.exceptions import OutlierEngineError


class DataFrameValidator:
    """Validator responsible for verifying DataFrame integrity."""

    @staticmethod
    def validate(df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise OutlierEngineError("Input must be a valid pandas DataFrame.")
        if df.empty:
            raise OutlierEngineError("DataFrame is empty.")
