import re
from typing import Optional, Tuple, List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype


class QAResult:
	def __init__(self, table: Optional[pd.DataFrame] = None, figure: Optional[plt.Figure] = None, message: Optional[str] = None):
		self.table = table
		self.figure = figure
		self.message = message or ""


def _find_date_column(df: pd.DataFrame) -> Optional[str]:
	for col in df.columns:
		if is_datetime64_any_dtype(df[col]):
			return col
	return None


def _normalize_col(df: pd.DataFrame, name: str) -> Optional[str]:
	name_l = name.strip().lower()
	for col in df.columns:
		if col.lower() == name_l:
			return col
	return None


def answer_question(df: pd.DataFrame, question: str) -> QAResult:
	q = question.strip().lower()
	# 1) counts
	if re.search(r"(how many|count)\s+(rows|records)", q):
		return QAResult(message=f"Total rows: {len(df)}")
	if re.search(r"(how many|count)\s+(columns|features)", q):
		return QAResult(message=f"Total columns: {df.shape[1]}")

	# 2) unique values in a column
	m = re.search(r"(unique|distinct).*(in|of)\s+([a-zA-Z0-9_]+)", q)
	if m:
		col = _normalize_col(df, m.group(3))
		if col and col in df.columns:
			vc = df[col].astype(str).value_counts().reset_index()
			vc.columns = [col, "count"]
			fig, ax = plt.subplots(figsize=(6, 4))
			sns.barplot(y=vc[col].head(20), x=vc["count"].head(20), ax=ax)
			ax.set_title(f"Top {col}")
			return QAResult(table=vc.head(100), figure=fig, message=f"Top values in {col}")
		return QAResult(message="Column not found.")

	# 3) aggregations like avg/sum/min/max of column, optional filter 'where col = value'
	m = re.search(r"(avg|average|mean|sum|min|max)\s+(?:of\s+)?([a-zA-Z0-9_]+)(?:\s+where\s+([a-zA-Z0-9_]+)\s*(=|==|is|equals)\s*([\w\-\.]+))?", q)
	if m:
		op, col_name, fcol, _, fval = m.groups()
		col = _normalize_col(df, col_name)
		if not col:
			return QAResult(message="Target column not found.")
		res = df.copy()
		if fcol and fval is not None:
			fcol_real = _normalize_col(df, fcol)
			if fcol_real:
				res = res[res[fcol_real].astype(str).str.lower() == str(fval).lower()]
			else:
				return QAResult(message="Filter column not found.")
		if op in ["avg", "average", "mean"]:
			val = pd.to_numeric(res[col], errors="coerce").mean()
		elif op == "sum":
			val = pd.to_numeric(res[col], errors="coerce").sum()
		elif op == "min":
			val = pd.to_numeric(res[col], errors="coerce").min()
		else:
			val = pd.to_numeric(res[col], errors="coerce").max()
		return QAResult(message=f"{op} of {col}: {val}")

	# 4) top N categories in column
	m = re.search(r"(top|most common)\s*(\d+)?\s*(values|categories|items)?\s*(in|of)?\s*([a-zA-Z0-9_]+)", q)
	if m:
		n_str, col_name = m.group(2), m.group(5)
		n = int(n_str) if n_str else 10
		col = _normalize_col(df, col_name)
		if not col:
			return QAResult(message="Column not found.")
		vc = df[col].astype(str).value_counts().reset_index().head(n)
		vc.columns = [col, "count"]
		fig, ax = plt.subplots(figsize=(6, 4))
		sns.barplot(y=vc[col], x=vc["count"], ax=ax)
		ax.set_title(f"Top {n} {col}")
		return QAResult(table=vc, figure=fig, message=f"Top {n} values in {col}")

	# 5) counts by a categorical column
	m = re.search(r"(count|number)\s+(by|per)\s+([a-zA-Z0-9_]+)", q)
	if m:
		col = _normalize_col(df, m.group(3))
		if not col:
			return QAResult(message="Column not found.")
		vc = df.groupby(col).size().reset_index(name="count").sort_values("count", ascending=False)
		fig, ax = plt.subplots(figsize=(6, 4))
		sns.barplot(y=vc[col].head(20), x=vc["count"].head(20), ax=ax)
		ax.set_title(f"Count by {col}")
		return QAResult(table=vc, figure=fig, message=f"Counts by {col}")

	# 6) trend over time if asked
	if re.search(r"(trend|over time|by month|monthly)", q):
		date_col = _find_date_column(df)
		if not date_col:
			return QAResult(message="No datetime column found for trend.")
		counts = df[date_col].dropna().dt.to_period("M").value_counts().sort_index()
		res = counts.reset_index(); res.columns = ["month", "count"]
		fig, ax = plt.subplots(figsize=(6, 4))
		ax.plot(res["month"].astype(str), res["count"]) ; ax.set_title("Monthly counts") ; ax.tick_params(axis='x', rotation=45)
		return QAResult(table=res, figure=fig, message=f"Monthly counts by {date_col}")

	# Fallback
	return QAResult(message="Sorry, I couldn't parse the question. Try asking for counts, top categories, averages, or trends.")
