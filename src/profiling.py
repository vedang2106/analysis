import pandas as pd


def compute_overview(df: pd.DataFrame):
	overview = {
		"num_rows": int(df.shape[0]),
		"num_cols": int(df.shape[1]),
		"dtypes": df.dtypes.astype(str).to_dict(),
		"missing_counts": df.isna().sum().to_dict(),
		"summary_stats": df.describe(include="all").transpose().fillna(0),
	}
	return overview
