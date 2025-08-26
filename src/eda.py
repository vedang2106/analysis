from typing import List, Tuple, Dict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype


plt.switch_backend("Agg")


def _plot_distributions(df: pd.DataFrame) -> List[Tuple[str, plt.Figure]]:
	figures = []
	for col in df.columns[:10]:
		fig, ax = plt.subplots(figsize=(6, 4))
		if is_numeric_dtype(df[col]):
			sns.histplot(df[col].dropna(), kde=True, ax=ax)
			ax.set_title(f"Distribution: {col}")
		elif is_datetime64_any_dtype(df[col]):
			counts = df[col].dropna().dt.to_period('M').value_counts().sort_index()
			ax.plot(counts.index.to_timestamp(), counts.values)
			ax.set_title(f"Time Trend (counts): {col}")
			ax.set_xlabel("Date")
			ax.set_ylabel("Count")
		else:
			vc = df[col].astype(str).value_counts().head(10)
			sns.barplot(x=vc.values, y=vc.index, ax=ax)
			ax.set_title(f"Top Categories: {col}")
		figures.append((f"{col}", fig))
	return figures


def _plot_boxplots(df: pd.DataFrame) -> List[Tuple[str, plt.Figure]]:
	figures = []
	for col in df.columns:
		if is_numeric_dtype(df[col]):
			fig, ax = plt.subplots(figsize=(6, 3))
			sns.boxplot(x=df[col], ax=ax)
			ax.set_title(f"Boxplot: {col}")
			figures.append((f"Boxplot: {col}", fig))
	return figures[:5]


def _plot_correlation(df: pd.DataFrame) -> List[Tuple[str, plt.Figure]]:
	num_df = df.select_dtypes(include=[np.number])
	if num_df.shape[1] < 2:
		return []
	corr = num_df.corr(numeric_only=True)
	fig, ax = plt.subplots(figsize=(6, 5))
	sns.heatmap(corr, cmap="coolwarm", annot=False, ax=ax)
	ax.set_title("Correlation Heatmap")
	return [("Correlation Heatmap", fig)]


def generate_eda(df: pd.DataFrame):
	figs = []
	figs.extend(_plot_distributions(df))
	figs.extend(_plot_boxplots(df))
	figs.extend(_plot_correlation(df))
	meta = {"num_figures": len(figs)}
	return figs, meta
