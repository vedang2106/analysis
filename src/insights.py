from typing import List
import pandas as pd
import numpy as np


def _find_outliers(df: pd.DataFrame) -> List[str]:
	messages = []
	num_df = df.select_dtypes(include=[np.number])
	for col in num_df.columns:
		series = num_df[col].dropna()
		if series.std(ddof=0) == 0 or series.shape[0] < 5:
			continue
		z = (series - series.mean()) / series.std(ddof=0)
		outlier_ratio = (np.abs(z) > 3).mean()
		if outlier_ratio > 0.02:
			messages.append(f"{col}: {outlier_ratio:.1%} potential outliers (>|3σ|)")
	return messages


def _top_correlations(df: pd.DataFrame) -> List[str]:
	num_df = df.select_dtypes(include=[np.number])
	if num_df.shape[1] < 2:
		return []
	corr = num_df.corr(numeric_only=True).abs()
	pairs = []
	cols = corr.columns.tolist()
	for i in range(len(cols)):
		for j in range(i + 1, len(cols)):
			pairs.append((cols[i], cols[j], corr.iloc[i, j]))
	pairs.sort(key=lambda x: x[2], reverse=True)
	return [f"{a} ~ {b}: corr={c:.2f}" for a, b, c in pairs[:5] if c >= 0.5]


def generate_insights(df: pd.DataFrame) -> str:
	outliers = _find_outliers(df)
	correls = _top_correlations(df)
	lines = []
	if outliers:
		lines.append("Outliers detected:")
		for m in outliers:
			lines.append(f"- {m}")
	if correls:
		lines.append("Strong numeric correlations:")
		for m in correls:
			lines.append(f"- {m}")
	if not lines:
		lines.append("No significant anomalies or strong correlations detected.")
	return "\n".join(lines)
