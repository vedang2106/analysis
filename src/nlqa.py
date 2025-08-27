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


def _find_sales_column(df: pd.DataFrame) -> Optional[str]:
	# Look for common sales-related column names
	sales_keywords = ['sale', 'sales', 'revenue', 'amount', 'price', 'cost', 'value', 'total', 'income']
	for col in df.columns:
		col_lower = col.lower()
		if any(keyword in col_lower for keyword in sales_keywords):
			return col
	return None


def _normalize_col(df: pd.DataFrame, name: str) -> Optional[str]:
	name_l = name.strip().lower()
	for col in df.columns:
		if col.lower() == name_l:
			return col
	return None


def _parse_date_filter(question: str) -> Optional[Tuple[str, str]]:
	# Extract month names and years
	months = {
		'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
		'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8,
		'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
		'november': 11, 'nov': 11, 'december': 12, 'dec': 12
	}
	
	question_lower = question.lower()
	
	# Look for month patterns
	for month_name, month_num in months.items():
		if month_name in question_lower:
			# Look for year
			year_match = re.search(r'20\d{2}', question)
			year = year_match.group() if year_match else None
			return month_num, year
	
	# Look for "this month", "last month", etc.
	if 'this month' in question_lower:
		from datetime import datetime
		now = datetime.now()
		return now.month, str(now.year)
	elif 'last month' in question_lower:
		from datetime import datetime
		now = datetime.now()
		last_month = now.month - 1 if now.month > 1 else 12
		last_year = now.year if now.month > 1 else now.year - 1
		return last_month, str(last_year)
	
	return None


def _create_comparison_chart(df: pd.DataFrame, col1: str, col2: str, title: str) -> plt.Figure:
	fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
	
	# First column
	if is_numeric_dtype(df[col1]):
		ax1.hist(df[col1].dropna(), bins=20, alpha=0.7)
		ax1.set_title(f'Distribution of {col1}')
		ax1.set_xlabel(col1)
		ax1.set_ylabel('Frequency')
	else:
		vc1 = df[col1].value_counts().head(10)
		ax1.bar(range(len(vc1)), vc1.values)
		ax1.set_title(f'Top {col1}')
		ax1.set_xticks(range(len(vc1)))
		ax1.set_xticklabels(vc1.index, rotation=45)
	
	# Second column
	if is_numeric_dtype(df[col2]):
		ax2.hist(df[col2].dropna(), bins=20, alpha=0.7)
		ax2.set_title(f'Distribution of {col2}')
		ax2.set_xlabel(col2)
		ax2.set_ylabel('Frequency')
	else:
		vc2 = df[col2].value_counts().head(10)
		ax2.bar(range(len(vc2)), vc2.values)
		ax2.set_title(f'Top {col2}')
		ax2.set_xticks(range(len(vc2)))
		ax2.set_xticklabels(vc2.index, rotation=45)
	
	plt.tight_layout()
	return fig


def answer_question(df: pd.DataFrame, question: str) -> QAResult:
	q = question.strip().lower()
	
	# 1) Basic counts and info
	if re.search(r"(how many|count)\s+(rows|records)", q):
		return QAResult(message=f"Total rows: {len(df)}")
	if re.search(r"(how many|count)\s+(columns|features)", q):
		return QAResult(message=f"Total columns: {df.shape[1]}")
	if re.search(r"(what|show)\s+(columns|features)", q):
		cols_df = pd.DataFrame({'Column': df.columns, 'Type': df.dtypes.astype(str), 'Non-Null': df.count()})
		return QAResult(table=cols_df, message=f"Dataset has {len(df.columns)} columns")
	
	# 2) Sales queries with date filtering
	if re.search(r"(sale|sales|revenue|amount|income)", q):
		date_filter = _parse_date_filter(question)
		sales_col = _find_sales_column(df)
		date_col = _find_date_column(df)
		
		if not sales_col:
			return QAResult(message="No sales/revenue column found. Look for columns like 'sales', 'revenue', 'amount', 'price'.")
		
		if date_filter and date_col:
			month, year = date_filter
			# Filter by month and year
			filtered_df = df.copy()
			if year:
				filtered_df = filtered_df[filtered_df[date_col].dt.year == int(year)]
			filtered_df = filtered_df[filtered_df[date_col].dt.month == month]
			
			if filtered_df.empty:
				return QAResult(message=f"No data found for {pd.Timestamp(year=int(year), month=month, day=1).strftime('%B %Y')}")
			
			total_sales = pd.to_numeric(filtered_df[sales_col], errors='coerce').sum()
			avg_sales = pd.to_numeric(filtered_df[sales_col], errors='coerce').mean()
			
			# Create chart
			fig, ax = plt.subplots(figsize=(8, 5))
			# Group by day if possible
			if len(filtered_df) > 1:
				daily_sales = filtered_df.groupby(filtered_df[date_col].dt.day)[sales_col].sum()
				ax.bar(daily_sales.index, daily_sales.values)
				ax.set_xlabel('Day of Month')
				ax.set_ylabel('Sales')
				ax.set_title(f'Daily Sales - {pd.Timestamp(year=int(year), month=month, day=1).strftime("%B %Y")}')
			else:
				ax.bar([1], [total_sales])
				ax.set_xlabel('Period')
				ax.set_ylabel('Sales')
				ax.set_title(f'Sales - {pd.Timestamp(year=int(year), month=month, day=1).strftime("%B %Y")}')
			
			return QAResult(
				table=filtered_df[[date_col, sales_col]].head(20),
				figure=fig,
				message=f"Sales in {pd.Timestamp(year=int(year), month=month, day=1).strftime('%B %Y')}: Total: {total_sales:.2f}, Average: {avg_sales:.2f}"
			)
		else:
			# No date filter, show overall sales
			total_sales = pd.to_numeric(df[sales_col], errors='coerce').sum()
			avg_sales = pd.to_numeric(df[sales_col], errors='coerce').mean()
			
			# Create chart
			fig, ax = plt.subplots(figsize=(8, 5))
			if _find_date_column(df):
				date_col = _find_date_column(df)
				monthly_sales = df.groupby(df[date_col].dt.to_period('M'))[sales_col].sum()
				ax.plot(monthly_sales.index.astype(str), monthly_sales.values)
				ax.set_xlabel('Month')
				ax.set_ylabel('Sales')
				ax.set_title('Monthly Sales Trend')
				ax.tick_params(axis='x', rotation=45)
			else:
				ax.bar([1], [total_sales])
				ax.set_xlabel('Overall')
				ax.set_ylabel('Sales')
				ax.set_title('Total Sales')
			
			return QAResult(
				table=df[[sales_col]].describe(),
				figure=fig,
				message=f"Overall sales: Total: {total_sales:.2f}, Average: {avg_sales:.2f}"
			)
	
	# 3) Minimum/Maximum values
	if re.search(r"(minimum|min|lowest|smallest)\s+(?:value\s+)?(?:in|of)?\s*([a-zA-Z0-9_]+)", q):
		col = _normalize_col(df, re.search(r"(minimum|min|lowest|smallest)\s+(?:value\s+)?(?:in|of)?\s*([a-zA-Z0-9_]+)", q).group(2))
		if col and col in df.columns:
			if is_numeric_dtype(df[col]):
				min_val = df[col].min()
				min_rows = df[df[col] == min_val]
				fig, ax = plt.subplots(figsize=(8, 5))
				ax.hist(df[col].dropna(), bins=30, alpha=0.7)
				ax.axvline(min_val, color='red', linestyle='--', label=f'Min: {min_val}')
				ax.set_title(f'Distribution of {col} (Min highlighted)')
				ax.legend()
				return QAResult(table=min_rows, figure=fig, message=f"Minimum value in {col}: {min_val}")
			else:
				return QAResult(message=f"{col} is not numeric, cannot find minimum")
		return QAResult(message="Column not found")
	
	if re.search(r"(maximum|max|highest|largest)\s+(?:value\s+)?(?:in|of)?\s*([a-zA-Z0-9_]+)", q):
		col = _normalize_col(df, re.search(r"(maximum|max|highest|largest)\s+(?:value\s+)?(?:in|of)?\s*([a-zA-Z0-9_]+)", q).group(2))
		if col and col in df.columns:
			if is_numeric_dtype(df[col]):
				max_val = df[col].max()
				max_rows = df[df[col] == max_val]
				fig, ax = plt.subplots(figsize=(8, 5))
				ax.hist(df[col].dropna(), bins=30, alpha=0.7)
				ax.axvline(max_val, color='red', linestyle='--', label=f'Max: {max_val}')
				ax.set_title(f'Distribution of {col} (Max highlighted)')
				ax.legend()
				return QAResult(table=max_rows, figure=fig, message=f"Maximum value in {col}: {max_val}")
			else:
				return QAResult(message=f"{col} is not numeric, cannot find maximum")
		return QAResult(message="Column not found")
	
	# 4) Unique values and distributions
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

	# 5) Aggregations with filters
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

	# 6) Top N categories
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

	# 7) Counts by category
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

	# 8) Time trends and patterns
	if re.search(r"(trend|over time|by month|monthly|weekly|daily|pattern)", q):
		date_col = _find_date_column(df)
		if not date_col:
			return QAResult(message="No datetime column found for trend analysis.")
		
		# Determine time period
		if 'daily' in q:
			period = 'D'
			title = "Daily counts"
		elif 'weekly' in q:
			period = 'W'
			title = "Weekly counts"
		else:
			period = 'M'
			title = "Monthly counts"
		
		counts = df[date_col].dropna().dt.to_period(period).value_counts().sort_index()
		res = counts.reset_index()
		res.columns = ["period", "count"]
		
		fig, ax = plt.subplots(figsize=(8, 5))
		ax.plot(res["period"].astype(str), res["count"])
		ax.set_title(title)
		ax.tick_params(axis='x', rotation=45)
		return QAResult(table=res, figure=fig, message=f"{title} by {date_col}")

	# 9) Business metrics and correlations
	if re.search(r"(profit|margin|growth|performance|correlation|relationship)", q):
		# Look for numeric columns that might be business metrics
		numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
		if len(numeric_cols) >= 2:
			fig, ax = plt.subplots(figsize=(8, 5))
			corr = df[numeric_cols].corr()
			sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
			ax.set_title("Business Metrics Correlation")
			return QAResult(table=corr, figure=fig, message="Correlation between business metrics")
		else:
			return QAResult(message="Need at least 2 numeric columns for business metrics analysis.")

	# 10) Data quality and missing values
	if re.search(r"(missing|null|empty|quality|clean)", q):
		missing_info = df.isnull().sum()
		missing_df = pd.DataFrame({'Column': missing_info.index, 'Missing_Count': missing_info.values, 'Missing_Percentage': (missing_info.values / len(df) * 100)})
		missing_df = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
		
		if not missing_df.empty:
			fig, ax = plt.subplots(figsize=(8, 5))
			ax.bar(missing_df['Column'], missing_df['Missing_Percentage'])
			ax.set_title('Missing Data by Column (%)')
			ax.set_xlabel('Column')
			ax.set_ylabel('Missing Percentage')
			ax.tick_params(axis='x', rotation=45)
			return QAResult(table=missing_df, figure=fig, message=f"Found {len(missing_df)} columns with missing data")
		else:
			return QAResult(message="No missing data found in the dataset")

	# 11) Data distribution and statistics
	if re.search(r"(distribution|spread|statistics|stats|summary)", q):
		numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
		if numeric_cols:
			fig, axes = plt.subplots(2, 2, figsize=(12, 8))
			fig.suptitle('Data Distribution Overview')
			
			for i, col in enumerate(numeric_cols[:4]):
				row, col_idx = i // 2, i % 2
				axes[row, col_idx].hist(df[col].dropna(), bins=20, alpha=0.7)
				axes[row, col_idx].set_title(f'{col}')
				axes[row, col_idx].set_xlabel(col)
			
			plt.tight_layout()
			return QAResult(table=df[numeric_cols].describe(), figure=fig, message="Data distribution overview for numeric columns")
		else:
			return QAResult(message="No numeric columns found for distribution analysis")

	# 12) Comparison between columns
	if re.search(r"(compare|comparison|vs|versus|between)\s+([a-zA-Z0-9_]+)\s+(?:and|&|vs|versus)\s+([a-zA-Z0-9_]+)", q):
		m = re.search(r"(compare|comparison|vs|versus|between)\s+([a-zA-Z0-9_]+)\s+(?:and|&|vs|versus)\s+([a-zA-Z0-9_]+)", q)
		col1 = _normalize_col(df, m.group(2))
		col2 = _normalize_col(df, m.group(3))
		
		if col1 and col2 and col1 in df.columns and col2 in df.columns:
			fig = _create_comparison_chart(df, col1, col2, f"Comparison: {col1} vs {col2}")
			comparison_data = pd.DataFrame({
				'Column': [col1, col2],
				'Count': [df[col1].count(), df[col2].count()],
				'Unique': [df[col1].nunique(), df[col2].nunique()]
			})
			if is_numeric_dtype(df[col1]):
				comparison_data.loc[0, 'Mean'] = df[col1].mean()
			if is_numeric_dtype(df[col2]):
				comparison_data.loc[1, 'Mean'] = df[col2].mean()
			
			return QAResult(table=comparison_data, figure=fig, message=f"Comparison between {col1} and {col2}")
		else:
			return QAResult(message="One or both columns not found")

	# 13) Outliers detection
	if re.search(r"(outlier|anomaly|extreme|unusual)", q):
		numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
		if numeric_cols:
			outliers_data = []
			fig, axes = plt.subplots(2, 2, figsize=(12, 8))
			fig.suptitle('Outlier Detection')
			
			for i, col in enumerate(numeric_cols[:4]):
				row, col_idx = i // 2, i % 2
				Q1 = df[col].quantile(0.25)
				Q3 = df[col].quantile(0.75)
				IQR = Q3 - Q1
				lower_bound = Q1 - 1.5 * IQR
				upper_bound = Q3 + 1.5 * IQR
				
				outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
				if not outliers.empty:
					outliers_data.append({
						'Column': col,
						'Outlier_Count': len(outliers),
						'Outlier_Percentage': len(outliers) / len(df) * 100
					})
				
				axes[row, col_idx].boxplot(df[col].dropna())
				axes[row, col_idx].set_title(f'{col} - Boxplot')
			
			plt.tight_layout()
			
			if outliers_data:
				outliers_df = pd.DataFrame(outliers_data)
				return QAResult(table=outliers_df, figure=fig, message="Outlier analysis for numeric columns")
			else:
				return QAResult(message="No significant outliers detected")
		else:
			return QAResult(message="No numeric columns found for outlier analysis")

	# Fallback with comprehensive suggestions
	return QAResult(message="Try asking about:\n• Sales in July 2024\n• Top 10 products\n• Average price by category\n• Monthly trends\n• Count by region\n• Revenue where country = USA\n• Minimum/maximum values\n• Data quality and missing values\n• Compare two columns\n• Find outliers\n• Data distribution\n• Statistics summary")
