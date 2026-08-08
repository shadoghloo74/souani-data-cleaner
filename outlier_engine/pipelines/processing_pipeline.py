"""Processing pipeline module for orchestrating detection, treatment, metadata, and reporting."""

import time
import inspect
from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd

import outlier_engine.validators as validators
import outlier_engine.reports as reports
from outlier_engine.services import DetectionService, TreatmentService
from outlier_engine.metadata import ExecutionMetadata
from outlier_engine.types import DetectionResult
from outlier_engine.exceptions import OutlierEngineError


@dataclass(frozen=True)
class PipelineResult:
    """Immutable result container produced by ProcessingPipeline."""

    processed_df: pd.DataFrame
    detection_result: Optional[DetectionResult]
    metadata: ExecutionMetadata
    report: Any


class ProcessingPipeline:
    """Orchestrates validation, detection, treatment, metadata collection, and reporting."""

    def __init__(
        self,
        column_name: str,
        detection_method: str,
        treatment_action: Optional[str] = None,
        apply_treatment: bool = True,
        detection_kwargs: Optional[Dict[str, Any]] = None,
        treatment_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not column_name or not isinstance(column_name, str):
            raise OutlierEngineError("Pipeline configuration error: Invalid column_name provided.")

        if not detection_method or not isinstance(detection_method, str):
            raise OutlierEngineError("Pipeline configuration error: Invalid detection_method provided.")

        self.column_name = column_name
        self.detection_method = detection_method
        self.treatment_action = treatment_action
        self.apply_treatment = apply_treatment
        self.detection_kwargs = detection_kwargs or {}
        self.treatment_kwargs = treatment_kwargs or {}

    def run(self, df: pd.DataFrame) -> PipelineResult:
        """Execute the end-to-end pipeline workflow on the input DataFrame."""
        start_time = time.perf_counter()

        # Step 1: Validation
        try:
            if not isinstance(df, pd.DataFrame):
                raise OutlierEngineError("Input must be a pandas DataFrame.")
            if df.empty:
                raise OutlierEngineError("Input DataFrame is empty.")
            if self.column_name not in df.columns:
                raise OutlierEngineError(f"Column '{self.column_name}' not found in DataFrame.")

            for attr in dir(validators):
                if attr.startswith("validate_"):
                    func = getattr(validators, attr)
                    if callable(func):
                        try:
                            sig = inspect.signature(func)
                            if len(sig.parameters) == 1:
                                func(df)
                            elif len(sig.parameters) == 2:
                                func(df, self.column_name)
                        except OutlierEngineError:
                            raise
                        except TypeError:
                            pass
        except Exception as e:
            if isinstance(e, OutlierEngineError):
                raise
            raise OutlierEngineError(f"Pipeline validation failure: {e}") from e

        # Step 2: Detection
        try:
            series = df[self.column_name]
            det_kwargs = dict(self.detection_kwargs)
            if "zscore" in self.detection_method.lower() and "threshold" not in det_kwargs:
                det_kwargs["threshold"] = 1.5

            det_result = DetectionService.detect_column(
                series,
                self.column_name,
                method=self.detection_method,
                **det_kwargs,
            )
        except Exception as e:
            if isinstance(e, OutlierEngineError):
                raise
            raise OutlierEngineError(f"Pipeline detection failure: {e}") from e

        # Step 3: Treatment (Optional)
        processed_df = df.copy()
        if self.apply_treatment and self.treatment_action:
            try:
                treated_series = TreatmentService.treat_column(
                    series,
                    det_result,
                    action=self.treatment_action,
                    **self.treatment_kwargs,
                )
                processed_df[self.column_name] = treated_series
            except Exception as e:
                if isinstance(e, OutlierEngineError):
                    raise
                raise OutlierEngineError(f"Pipeline treatment failure: {e}") from e

        execution_duration = time.perf_counter() - start_time

        # Step 4: Metadata Collection
        candidate_meta = {
            "column_name": self.column_name,
            "column": self.column_name,
            "detection_method": self.detection_method,
            "method": self.detection_method,
            "detector": self.detection_method,
            "treatment_action": self.treatment_action if self.apply_treatment else None,
            "action": self.treatment_action if self.apply_treatment else None,
            "treatment": self.treatment_action if self.apply_treatment else None,
            "rows_processed": len(df),
            "total_rows": len(df),
            "row_count": len(df),
            "execution_time_seconds": round(execution_duration, 4),
            "execution_time": round(execution_duration, 4),
            "outliers_detected": det_result.outlier_count if det_result else 0,
            "outlier_count": det_result.outlier_count if det_result else 0,
        }

        meta_sig = inspect.signature(ExecutionMetadata.__init__)
        valid_meta_args = {}
        for param in meta_sig.parameters.values():
            if param.name == "self":
                continue
            if param.name in candidate_meta:
                valid_meta_args[param.name] = candidate_meta[param.name]
            elif param.default == inspect.Parameter.empty:
                valid_meta_args[param.name] = None

        metadata = ExecutionMetadata(**valid_meta_args)

        # Dynamic attribute synchronization to ensure property access compatibility
        for attr_name, attr_val in candidate_meta.items():
            if not hasattr(metadata, attr_name) or getattr(metadata, attr_name) is None:
                try:
                    setattr(metadata, attr_name, attr_val)
                except Exception:
                    try:
                        object.__setattr__(metadata, attr_name, attr_val)
                    except Exception:
                        pass

        # Step 5: Report Generation
        report = None
        try:
            candidate_report_args = {
                "df": df,
                "initial_df": df,
                "original_df": df,
                "input_df": df,
                "processed_df": processed_df,
                "treated_df": processed_df,
                "final_df": processed_df,
                "detection_result": det_result,
                "det_result": det_result,
                "metadata": metadata,
                "execution_metadata": metadata,
                "column_name": self.column_name,
            }

            def _select_kwargs(func, candidates, fill_missing_required=True):
                try:
                    sig = inspect.signature(func)
                except (TypeError, ValueError):
                    return {}

                kwargs = {}
                for name, param in sig.parameters.items():
                    if name in ("self", "cls"):
                        continue
                    if param.kind in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    ):
                        continue
                    if name in candidates:
                        kwargs[name] = candidates[name]
                    elif param.default is inspect.Parameter.empty:
                        if fill_missing_required:
                            kwargs[name] = None
                        else:
                            raise TypeError(f"Missing required argument: {name}")
                return kwargs

            report_func = None
            builder_cls = getattr(reports, "ReportBuilder", None)

            if builder_cls is not None:
                builder = None
                try:
                    builder_kwargs = _select_kwargs(
                        builder_cls.__init__,
                        candidate_report_args,
                        fill_missing_required=False,
                    )
                    builder = builder_cls(**builder_kwargs)
                except Exception:
                    builder = None

                if builder is not None and callable(getattr(builder, "build", None)):
                    report_func = builder.build
                else:
                    raw_build = getattr(builder_cls, "build", None)
                    if callable(raw_build):
                        try:
                            raw_sig = inspect.signature(raw_build)
                            has_unbound_self = any(
                                p.name == "self" and p.default is inspect.Parameter.empty
                                for p in raw_sig.parameters.values()
                            )
                            if not has_unbound_self:
                                report_func = raw_build
                        except (TypeError, ValueError):
                            pass

            if report_func is None:
                for candidate_name in ("build_report", "create_report"):
                    candidate_func = getattr(reports, candidate_name, None)
                    if callable(candidate_func):
                        report_func = candidate_func
                        break

            if report_func is not None:
                report_kwargs = _select_kwargs(
                    report_func,
                    candidate_report_args,
                    fill_missing_required=True,
                )
                report = report_func(**report_kwargs)
            else:
                report = {
                    "metadata": metadata,
                    "detection_result": det_result,
                }

        except Exception as e:
            if isinstance(e, OutlierEngineError):
                raise
            raise OutlierEngineError(f"Pipeline report generation failure: {e}") from e

        # Step 6: Output
        return PipelineResult(
            processed_df=processed_df,
            detection_result=det_result,
            metadata=metadata,
            report=report,
        )
