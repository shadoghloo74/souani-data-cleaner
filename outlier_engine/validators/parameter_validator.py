"""Parameter validator module for Outlier Engine."""

from outlier_engine.exceptions import OutlierEngineError


class ParameterValidator:
    """Validator responsible for verifying method parameters and thresholds."""

    @staticmethod
    def validate_positive(value: float, param_name: str) -> None:
        if value <= 0:
            raise OutlierEngineError(
                f"Parameter '{param_name}' must be strictly positive (> 0).")

    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float, param_name: str) -> None:
        if not (min_val <= value <= max_val):
            raise OutlierEngineError(
                f"Parameter '{param_name}' must be between {min_val} and {max_val}.")
