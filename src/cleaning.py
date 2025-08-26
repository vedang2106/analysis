from typing import Dict, Tuple
import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype


def _coerce_dates(df: pd.DataFrame) -> pd.DataFrame:
	for col in df.columns:
		if df[col].dtype == object:
			try:
				df[col] = pd.to_datetime(df[col], errors="raise")
			except Exception:
				pass
	return df


def _impute_missing(df: pd.DataFrame) -> Dict[str, str]:
	report = {}
	for col in df.columns:
		if df[col].isna().any():
			if is_numeric_dtype(df[col]):
				median_val = df[col].median()
				df[col] = df[col].fillna(median_val)
				report[col] = f"filled {df[col].isna().sum()} NaNs with median {median_val}"
			elif is_datetime64_any_dtype(df[col]):
				mode_val = df[col].mode(dropna=True)
				fill_val = mode_val.iloc[0] if not mode_val.empty else pd.Timestamp("1970-01-01")
				df[col] = df[col].fillna(fill_val)
				report[col] = f"filled NaTs with mode {fill_val}"
			else:
				mode_val = df[col].mode(dropna=True)
				fill_val = mode_val.iloc[0] if not mode_val.empty else ""
				df[col] = df[col].fillna(fill_val)
				report[col] = f"filled NaNs with mode '{fill_val}'"
	return report


def auto_clean(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
	result = df.copy()
	initial_rows = result.shape[0]
	result = _coerce_dates(result)
	impute_report = _impute_missing(result)
	before_dedup = result.shape[0]
	result = result.drop_duplicates()
	deduped = before_dedup - result.shape[0]
	coercions = {}
	for col in result.columns:
		if is_numeric_dtype(result[col]):
			coercions[col] = "numeric"
		elif is_datetime64_any_dtype(result[col]):
			coercions[col] = "datetime"
		else:
			coercions[col] = "category/text"
	report = {
		"rows_before": int(initial_rows),
		"rows_after": int(result.shape[0]),
		"duplicates_removed": int(deduped),
		"imputations": impute_report,
		"inferred_types": coercions,
	}
	return result, report
