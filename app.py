import io
import os
from datetime import datetime

import pandas as pd
import streamlit as st

from src.loaders import detect_and_load
from src.profiling import compute_overview
from src.cleaning import auto_clean
from src.eda import generate_eda
from src.insights import generate_insights
from src.exports import export_excel_with_summary, export_powerbi_csv, export_powerbi_bundle, export_pdf_report
from src.nlqa import answer_question

st.set_page_config(page_title="Data Analyst Automation", layout="wide")
st.title("Data Analyst Automation Tool")

st.markdown("Upload a dataset (CSV, Excel, JSON), auto-analyze, and export a report.")

with st.sidebar:
	st.header("Options")
	uploaded = st.file_uploader("Upload file", type=["csv", "xlsx", "xls", "json"])
	output_excel = st.checkbox("Export Excel (cleaned + summary + charts)", value=True)
	output_powerbi = st.checkbox("Export Power BI bundle (CSV + charts ZIP)", value=True)
	output_pdf = st.checkbox("Export PDF report (with charts)", value=True)

if uploaded is not None:
	with st.spinner("Loading dataset..."):
		df, meta = detect_and_load(uploaded, uploaded.name)
		st.success(f"Loaded '{uploaded.name}' with shape {df.shape}")

	st.subheader("Data Understanding")
	overview = compute_overview(df)
	col1, col2, col3 = st.columns(3)
	with col1:
		st.metric("Rows", overview["num_rows"]) 
		st.metric("Columns", overview["num_cols"]) 
	with col2:
		st.write("Dtypes:")
		st.dataframe(pd.DataFrame(overview["dtypes"], columns=["dtype"]))
	with col3:
		st.write("Missing Values:")
		st.dataframe(pd.DataFrame(overview["missing_counts"], columns=["missing"]))

	st.write("Summary Statistics:")
	st.dataframe(overview["summary_stats"].T)

	st.subheader("Automated Cleaning")
	with st.spinner("Cleaning data..."):
		clean_df, cleaning_report = auto_clean(df)
	st.write("Cleaning report:")
	st.json(cleaning_report)
	st.write("Preview of cleaned data:")
	st.dataframe(clean_df.head(50))

	st.subheader("Exploratory Data Analysis (auto)")
	figs, eda_meta = generate_eda(clean_df)
	for title, fig in figs:
		st.markdown(f"**{title}**")
		st.pyplot(fig)

	st.subheader("Chat with your data (no storage)")
	st.caption("Ask questions like: 'top 5 names', 'average age where country = UK', 'monthly trend'.")
	user_q = st.text_input("Your question")
	if st.button("Answer") and user_q.strip():
		qa = answer_question(clean_df, user_q)
		if qa.message:
			st.write(qa.message)
		if qa.table is not None:
			st.dataframe(qa.table)
		if qa.figure is not None:
			st.pyplot(qa.figure)
			figs.append(("Q&A Chart", qa.figure))

	st.subheader("Insights")
	insights_text = generate_insights(clean_df)
	st.write(insights_text)

	st.subheader("Exports")
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	base_name = os.path.splitext(uploaded.name)[0]

	excel_bytes = None
	powerbi_bytes = None
	pdf_bytes = None

	if output_excel:
		with st.spinner("Generating Excel export..."):
			excel_bytes = export_excel_with_summary(clean_df, overview, cleaning_report, insights_text, file_basename=base_name, figs=figs)
			st.download_button(
				label="Download Excel",
				data=excel_bytes,
				file_name=f"{base_name}_{timestamp}.xlsx",
				mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
			)

	if output_powerbi:
		with st.spinner("Preparing Power BI bundle (ZIP)..."):
			powerbi_bytes = export_powerbi_bundle(clean_df, figs=figs)
			st.download_button(
				label="Download Power BI ZIP",
				data=powerbi_bytes,
				file_name=f"{base_name}_{timestamp}.zip",
				mime="application/zip",
			)

	if output_pdf:
		with st.spinner("Generating PDF report..."):
			pdf_bytes = export_pdf_report(base_name, overview, cleaning_report, insights_text, figs=figs)
			st.download_button(
				label="Download PDF",
				data=pdf_bytes,
				file_name=f"{base_name}_{timestamp}.pdf",
				mime="application/pdf",
			)
else:
	st.info("Please upload a CSV, Excel, or JSON file to begin.")
