"""Column validator module for Outlier Engine."""

import pandas as pd
from outlier_engine.exceptions import OutlierEngineError


class ColumnValidator:
    """Validator responsible for verifying columns existence and data types."""

    @staticmethod
    def validate_exists(df: pd.DataFrame, column_name: str) -> None:
        if column_name not in df.columns:
            raise OutlierEngineError(f"Column '{column_name}' does not exist in DataFrame.")

    @staticmethod
    def validate_numeric(series: pd.Series, column_name: str) -> None:
        if not pd.api.types.is_numeric_dtype(series):
            raise OutlierEngineError(f"Column '{column_name}' must be numeric for outlier operations.")
