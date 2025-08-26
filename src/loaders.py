import io
import pandas as pd


def _normalize_missing(df: pd.DataFrame) -> pd.DataFrame:
	# Strip whitespace in object columns
	for col in df.columns:
		if df[col].dtype == object:
			df[col] = df[col].astype(str).str.strip()
	# Convert empty strings (or whitespace-only) to NA
	df = df.replace(r"^\s*$", pd.NA, regex=True)
	return df


def detect_and_load(file_like, filename: str):
	name = (filename or "").lower()
	if name.endswith(".csv"):
		df = pd.read_csv(file_like)
		meta = {"type": "csv"}
	elif name.endswith(".xlsx") or name.endswith(".xls"):
		df = pd.read_excel(file_like)
		meta = {"type": "excel"}
	elif name.endswith(".json"):
		df = pd.read_json(file_like)
		meta = {"type": "json"}
	else:
		# Try CSV fallback
		try:
			df = pd.read_csv(file_like)
			meta = {"type": "csv-fallback"}
		except Exception as exc:
			raise ValueError(f"Unsupported file type for {filename}: {exc}")
	# Normalize blanks/spaces to proper missing values
	df = _normalize_missing(df)
	return df, meta
