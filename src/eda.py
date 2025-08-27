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


def _plot_violin_plots(df: pd.DataFrame) -> List[Tuple[str, plt.Figure]]:
	figures = []
	for col in df.columns:
		if is_numeric_dtype(df[col]):
			fig, ax = plt.subplots(figsize=(6, 4))
			sns.violinplot(x=df[col], ax=ax)
			ax.set_title(f"Violin Plot: {col}")
			figures.append((f"Violin Plot: {col}", fig))
	return figures[:5]


def _plot_scatter_plots(df: pd.DataFrame) -> List[Tuple[str, plt.Figure]]:
	figures = []
	numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
	
	if len(numeric_cols) >= 2:
		# Create scatter plot matrix for first 4 numeric columns
		cols_to_plot = numeric_cols[:4]
		if len(cols_to_plot) >= 2:
			fig, axes = plt.subplots(len(cols_to_plot)-1, len(cols_to_plot)-1, figsize=(12, 10))
			if len(cols_to_plot) == 2:
				axes = np.array([[axes]])
			
			plot_idx = 0
			for i in range(len(cols_to_plot)):
				for j in range(i+1, len(cols_to_plot)):
					row = plot_idx // (len(cols_to_plot)-1)
					col = plot_idx % (len(cols_to_plot)-1)
					
					axes[row, col].scatter(df[cols_to_plot[i]], df[cols_to_plot[j]], alpha=0.6)
					axes[row, col].set_xlabel(cols_to_plot[i])
					axes[row, col].set_ylabel(cols_to_plot[j])
					axes[row, col].set_title(f"{cols_to_plot[i]} vs {cols_to_plot[j]}")
					plot_idx += 1
			
			plt.tight_layout()
			figures.append(("Scatter Matrix", fig))
	
	return figures


def _plot_time_series(df: pd.DataFrame) -> List[Tuple[str, plt.Figure]]:
	figures = []
	date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
	
	for date_col in date_cols[:3]:  # Limit to 3 date columns
		# Find numeric columns for time series
		numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
		
		for num_col in numeric_cols[:3]:  # Limit to 3 numeric columns
			fig, ax = plt.subplots(figsize=(10, 4))
			
			# Group by date and calculate mean
			time_series = df.groupby(df[date_col].dt.to_period('D'))[num_col].mean()
			
			ax.plot(time_series.index.to_timestamp(), time_series.values, marker='o', linewidth=2)
			ax.set_title(f"Time Series: {num_col} over {date_col}")
			ax.set_xlabel("Date")
			ax.set_ylabel(num_col)
			ax.tick_params(axis='x', rotation=45)
			
			figures.append((f"Time Series: {num_col}", fig))
	
	return figures


def _plot_correlation(df: pd.DataFrame) -> List[Tuple[str, plt.Figure]]:
	num_df = df.select_dtypes(include=[np.number])
	if num_df.shape[1] < 2:
		return []
	corr = num_df.corr(numeric_only=True)
	fig, ax = plt.subplots(figsize=(6, 5))
	sns.heatmap(corr, cmap="coolwarm", annot=False, ax=ax)
	ax.set_title("Correlation Heatmap")
	return [("Correlation Heatmap", fig)]


def _plot_pair_plot(df: pd.DataFrame) -> List[Tuple[str, plt.Figure]]:
	numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
	
	if len(numeric_cols) >= 2 and len(numeric_cols) <= 6:  # Limit to prevent too many subplots
		fig = sns.pairplot(df[numeric_cols], diag_kind='kde', height=2)
		fig.fig.suptitle("Pair Plot Matrix", y=1.02)
		fig.fig.set_size_inches(12, 10)
		return [("Pair Plot Matrix", fig.fig)]
	
	return []


def _plot_categorical_analysis(df: pd.DataFrame) -> List[Tuple[str, plt.Figure]]:
	figures = []
	categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
	
	for col in categorical_cols[:5]:  # Limit to 5 categorical columns
		# Value counts with percentage
		vc = df[col].value_counts().head(15)
		percentages = (vc / len(df) * 100).round(1)
		
		fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
		
		# Bar chart
		sns.barplot(x=vc.values, y=vc.index, ax=ax1)
		ax1.set_title(f"Top Categories: {col}")
		ax1.set_xlabel("Count")
		
		# Pie chart for top 10
		top_10 = vc.head(10)
		ax2.pie(top_10.values, labels=top_10.index, autopct='%1.1f%%', startangle=90)
		ax2.set_title(f"Distribution: {col}")
		
		plt.tight_layout()
		figures.append((f"Categorical Analysis: {col}", fig))
	
	return figures


def generate_eda(df: pd.DataFrame):
	figs = []
	
	# Basic plots
	figs.extend(_plot_distributions(df))
	figs.extend(_plot_boxplots(df))
	figs.extend(_plot_violin_plots(df))
	
	# Advanced plots
	figs.extend(_plot_scatter_plots(df))
	figs.extend(_plot_time_series(df))
	figs.extend(_plot_correlation(df))
	figs.extend(_plot_pair_plot(df))
	figs.extend(_plot_categorical_analysis(df))
	
	meta = {"num_figures": len(figs)}
	return figs, meta
