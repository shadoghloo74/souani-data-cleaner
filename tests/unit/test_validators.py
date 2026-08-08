import pytest
import pandas as pd
from outlier_engine.validators import DataFrameValidator, ColumnValidator, ParameterValidator
from outlier_engine.exceptions import OutlierEngineError


def test_dataframe_validator():
    valid_df = pd.DataFrame({"a": [1, 2, 3]})
    DataFrameValidator.validate(valid_df)  # Should pass without error

    with pytest.raises(OutlierEngineError, match="Input must be a valid pandas DataFrame"):
        DataFrameValidator.validate("not_a_df")  # type: ignore

    with pytest.raises(OutlierEngineError, match="DataFrame is empty"):
        DataFrameValidator.validate(pd.DataFrame())


def test_column_validator():
    df = pd.DataFrame({"num": [1, 2, 3], "str": ["a", "b", "c"]})

    ColumnValidator.validate_exists(df, "num")  # Should pass

    with pytest.raises(OutlierEngineError, match="does not exist"):
        ColumnValidator.validate_exists(df, "non_existing")

    ColumnValidator.validate_numeric(df["num"], "num")  # Should pass

    with pytest.raises(OutlierEngineError, match="must be numeric"):
        ColumnValidator.validate_numeric(df["str"], "str")


def test_parameter_validator():
    ParameterValidator.validate_positive(1.5, "multiplier")  # Should pass

    with pytest.raises(OutlierEngineError, match="strictly positive"):
        ParameterValidator.validate_positive(-0.5, "multiplier")

    ParameterValidator.validate_range(0.5, 0.0, 1.0, "quantile")  # Should pass

    with pytest.raises(OutlierEngineError, match="must be between"):
        ParameterValidator.validate_range(1.5, 0.0, 1.0, "quantile")
