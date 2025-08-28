import io
from typing import Dict, List, Tuple
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import zipfile

try:
	import matplotlib.pyplot as plt  # noqa: F401
except Exception:
	plt = None  # type: ignore


def _figure_to_png_bytes(fig) -> bytes:
	buf = io.BytesIO()
	fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
	buf.seek(0)
	return buf.read()


def export_excel_with_summary(df: pd.DataFrame, overview: Dict, cleaning_report: Dict, insights_text: str, file_basename: str, figs: List[Tuple[str, object]] | None = None) -> bytes:
	buffer = io.BytesIO()
	with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
		df.to_excel(writer, index=False, sheet_name="CleanedData")
		# Summary sheet
		summary_rows = []
		summary_rows.append(["Rows", overview["num_rows"]])
		summary_rows.append(["Columns", overview["num_cols"]])
		for k, v in overview["dtypes"].items():
			summary_rows.append([f"dtype:{k}", v])
		for k, v in overview["missing_counts"].items():
			summary_rows.append([f"missing:{k}", v])
		summary_rows.append(["Duplicates Removed", cleaning_report.get("duplicates_removed", 0)])
		summary_rows.append(["Inferred Types", str(cleaning_report.get("inferred_types", {}))])
		summary_rows.append(["Imputations", str(cleaning_report.get("imputations", {}))])
		summary_rows.append(["Insights", insights_text])
		pd.DataFrame(summary_rows, columns=["Metric", "Value"]).to_excel(writer, index=False, sheet_name="Summary")

		# Charts sheet with embedded PNGs
		if figs:
			# Create charts sheet with openpyxl
			from openpyxl import Workbook
			from openpyxl.drawing.image import Image
			
			workbook = writer.book
			charts_ws = workbook.create_sheet("Charts")
			
			row = 1
			for idx, (title, fig) in enumerate(figs, start=1):
				# Write title
				charts_ws.cell(row=row, column=1, value=str(title))
				
				# Add chart image
				png_bytes = _figure_to_png_bytes(fig)
				img_stream = io.BytesIO(png_bytes)
				img = Image(img_stream)
				img.width = 400
				img.height = 300
				charts_ws.add_image(img, f'B{row + 1}')
				row += 40  # space between images
	buffer.seek(0)
	return buffer.read()


def export_powerbi_csv(df: pd.DataFrame) -> bytes:
	buffer = io.BytesIO()
	df.to_csv(buffer, index=False)
	buffer.seek(0)
	return buffer.read()


def export_powerbi_bundle(df: pd.DataFrame, figs: List[Tuple[str, object]] | None = None) -> bytes:
	zip_buf = io.BytesIO()
	with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
		# Add CSV
		csv_buf = io.BytesIO()
		df.to_csv(csv_buf, index=False)
		zf.writestr("data.csv", csv_buf.getvalue())
		# Add charts
		if figs:
			for i, (title, fig) in enumerate(figs, start=1):
				png = _figure_to_png_bytes(fig)
				name = f"charts/chart_{i:02d}.png"
				zf.writestr(name, png)
	zip_buf.seek(0)
	return zip_buf.read()


def export_tableau_bundle(df: pd.DataFrame, figs: List[Tuple[str, object]] | None = None) -> bytes:
	"""Create a simple Tableau-ready ZIP containing data.csv and optional charts.

	This avoids extra dependencies by using CSV which Tableau imports easily.
	Structure:
	  - tableau/data.csv
	  - tableau/charts/chart_XX.png (optional)
	  - README.txt with quick import instructions
	"""
	zip_buf = io.BytesIO()
	with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
		# Add CSV in a tableau/ folder
		csv_buf = io.BytesIO()
		df.to_csv(csv_buf, index=False)
		zf.writestr("tableau/data.csv", csv_buf.getvalue())

		# Optional: add charts for reference
		if figs:
			for i, (title, fig) in enumerate(figs, start=1):
				png = _figure_to_png_bytes(fig)
				name = f"tableau/charts/chart_{i:02d}.png"
				zf.writestr(name, png)

		# Include a small README with steps
		readme = (
			"Tableau Import Instructions\n\n"
			"1) Open Tableau Desktop or Tableau Public.\n"
			"2) Choose 'Text file' as a data source and select tableau/data.csv.\n"
			"3) Drag sheets to the canvas and start building visuals.\n"
			"4) Optional: Use charts in tableau/charts/ as references.\n"
		)
		zf.writestr("tableau/README.txt", readme)

	zip_buf.seek(0)
	return zip_buf.read()


def export_pdf_report(title: str, overview: Dict, cleaning_report: Dict, insights_text: str, figs: List[Tuple[str, object]] | None = None) -> bytes:
	buffer = io.BytesIO()
	c = canvas.Canvas(buffer, pagesize=A4)
	width, height = A4
	margin = 40
	y = height - margin
	c.setFont("Helvetica-Bold", 16)
	c.drawString(margin, y, f"Data Analysis Report: {title}")
	y -= 24
	c.setFont("Helvetica", 10)
	c.drawString(margin, y, "Overview:")
	y -= 14
	c.setFont("Helvetica", 9)
	for line in [
		f"Rows: {overview['num_rows']}",
		f"Columns: {overview['num_cols']}",
		f"Dtypes: {len(overview['dtypes'])} columns",
		f"Missing totals: {sum(overview['missing_counts'].values())}",
	]:
		c.drawString(margin, y, line)
		y -= 12
		if y < margin:
			c.showPage(); y = height - margin

	c.setFont("Helvetica", 10)
	c.drawString(margin, y, "Cleaning Report:")
	y -= 14
	c.setFont("Helvetica", 9)
	for k, v in cleaning_report.items():
		c.drawString(margin, y, f"{k}: {v}")
		y -= 12
		if y < margin:
			c.showPage(); y = height - margin

	c.setFont("Helvetica", 10)
	c.drawString(margin, y, "Insights:")
	y -= 14
	c.setFont("Helvetica", 9)
	for line in insights_text.split("\n"):
		c.drawString(margin, y, line[:110])
		y -= 12
		if y < margin:
			c.showPage(); y = height - margin

	# Charts pages
	if figs:
		for (title_text, fig) in figs:
			png = _figure_to_png_bytes(fig)
			img = ImageReader(io.BytesIO(png))
			img_w, img_h = img.getSize()
			# Fit within margins
			max_w = width - 2 * margin
			max_h = height - 2 * margin - 14
			scale = min(max_w / img_w, max_h / img_h)
			draw_w = img_w * scale
			draw_h = img_h * scale
			if y - draw_h < margin:
				c.showPage(); y = height - margin
			c.setFont("Helvetica-Bold", 12)
			c.drawString(margin, y, str(title_text))
			y -= 14
			c.drawImage(img, margin, y - draw_h, width=draw_w, height=draw_h, preserveAspectRatio=True, anchor='sw')
			y = y - draw_h - 18
			if y < margin:
				c.showPage(); y = height - margin

	c.showPage()
	c.save()
	buffer.seek(0)
	return buffer.read()
