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

# Page configuration
st.set_page_config(
    page_title="Data Analyst Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Hide Streamlit Cloud UI elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide share button and GitHub link */
    .stDeployButton {display: none;}
    
    /* Hide the "made with streamlit" footer */
    .stApp > footer {display: none;}
    
    /* Hide the "deployed on streamlit cloud" banner */
    .stApp > div[data-testid="stDecoration"] {display: none;}
    
    /* Hide Share, Star, and GitHub buttons */
    .stApp > div[data-testid="stToolbar"] {display: none;}
    .stApp > div[data-testid="stToolbar"] > div {display: none;}
    .stApp > div[data-testid="stToolbar"] > div > div {display: none;}
    
    /* Hide specific buttons by text content */
    .stApp button:contains("Share") {display: none !important;}
    .stApp button:contains("⭐") {display: none !important;}
    .stApp a[href*="github.com"] {display: none !important;}
    
    /* Alternative selectors for the toolbar buttons */
    .stApp > div[data-testid="stToolbar"] button {display: none !important;}
    .stApp > div[data-testid="stToolbar"] a {display: none !important;}
    
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .section-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .success-box {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>📊 Data Analyst Automation Tool</h1>
    <p style="font-size: 1.2rem; margin: 0;">Upload a dataset (CSV, Excel, JSON), auto-analyze, and export comprehensive reports</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h3>⚙️ Options</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload with enhanced styling
    st.markdown("""
    <div class="upload-area">
        <h4>📁 Upload Dataset</h4>
        <p>Drag and drop or browse to upload</p>
        <p style="font-size: 0.9rem; color: #666;">Limit: 200MB • Formats: CSV, XLSX, XLS, JSON</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader("", type=["csv", "xlsx", "xls", "json"], label_visibility="collapsed")
    
    if uploaded:
        st.success(f"✅ {uploaded.name} uploaded successfully!")
    
    st.markdown("---")
    
    # Export options with better styling
    st.markdown("**📤 Export Options**")
    output_excel = st.checkbox("📊 Excel (cleaned + summary + charts)", value=True)
    output_powerbi = st.checkbox("🔗 Power BI bundle (CSV + charts ZIP)", value=True)
    output_pdf = st.checkbox("📄 PDF report (with charts)", value=True)

# Main content
if uploaded is not None:
    # Loading section
    with st.spinner("🔄 Loading and analyzing dataset..."):
        df, meta = detect_and_load(uploaded, uploaded.name)
    
    # Success message
    st.markdown(f"""
    <div class="success-box">
        <h3>🎉 Dataset Loaded Successfully!</h3>
        <p><strong>{uploaded.name}</strong> • Shape: {df.shape[0]} rows × {df.shape[1]} columns</p>
    </div>
    """, unsafe_allow_html=True)

    # Debug information
    st.markdown("""
    <div class="section-card">
        <h2>🔧 Debug Information</h2>
        <p>This section shows what's happening with your dataset processing.</p>
    """, unsafe_allow_html=True)
    
    # Show basic dataset info
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Dataset Info:**")
        st.write(f"- File name: {uploaded.name}")
        st.write(f"- File size: {uploaded.size / 1024 / 1024:.2f} MB")
        st.write(f"- Rows: {df.shape[0]:,}")
        st.write(f"- Columns: {df.shape[1]}")
        st.write(f"- Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    with col2:
        st.write("**Column Types:**")
        for col in df.columns:
            st.write(f"- {col}: {df[col].dtype}")
    
    # Show first few rows
    st.write("**First 5 rows of data:**")
    st.dataframe(df.head(), use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Data Understanding Section
    st.markdown("""
    <div class="section-card">
        <h2>🔍 Data Understanding</h2>
    """, unsafe_allow_html=True)
    
    try:
        st.info("🔄 Computing data overview...")
        overview = compute_overview(df)
        st.success("✅ Data overview computed successfully!")
        
        # Metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin: 0;">📊 Rows</h3>
                <h2 style="color: #764ba2; margin: 0;">{}</h2>
            </div>
            """.format(overview["num_rows"]), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin: 0;">📋 Columns</h3>
                <h2 style="color: #764ba2; margin: 0;">{}</h2>
            </div>
            """.format(overview["num_cols"]), unsafe_allow_html=True)
        
        with col3:
            missing_total = sum(overview["missing_counts"].values())
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin: 0;">❌ Missing</h3>
                <h2 style="color: #764ba2; margin: 0;">{}</h2>
            </div>
            """.format(missing_total), unsafe_allow_html=True)
        
        with col4:
            numeric_cols = len([col for col in df.columns if df[col].dtype in ['int64', 'float64']])
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin: 0;">🔢 Numeric</h3>
                <h2 style="color: #764ba2; margin: 0;">{}</h2>
            </div>
            """.format(numeric_cols), unsafe_allow_html=True)
        
        # Data types and missing values in tabs
        tab1, tab2, tab3 = st.tabs(["📋 Data Types", "❌ Missing Values", "📊 Summary Statistics"])
        
        with tab1:
            dtypes_df = pd.DataFrame(list(overview["dtypes"].items()), columns=["Column", "Data Type"])
            st.dataframe(dtypes_df, use_container_width=True)
        
        with tab2:
            missing_df = pd.DataFrame(list(overview["missing_counts"].items()), columns=["Column", "Missing Count"])
            if missing_df["Missing Count"].sum() > 0:
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.success("🎉 No missing values found in the dataset!")
        
        with tab3:
            st.dataframe(overview["summary_stats"].T, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error in Data Understanding: {str(e)}")
        st.info("💡 Could not compute data overview. Check if the dataset is properly loaded.")
        overview = {"num_rows": len(df), "num_cols": len(df.columns), "dtypes": {}, "missing_counts": {}, "summary_stats": pd.DataFrame()}
        st.markdown("</div>", unsafe_allow_html=True)

    # Automated Cleaning Section
    st.markdown("""
    <div class="section-card">
        <h2>🧹 Automated Cleaning</h2>
    """, unsafe_allow_html=True)
    
    try:
        with st.spinner("🔄 Cleaning data..."):
            # For large datasets, show progress
            if len(df) > 10000:
                st.info(f"📊 Processing large dataset ({len(df):,} rows). This may take a moment...")
            
            clean_df, cleaning_report = auto_clean(df)
            st.success("✅ Data cleaning completed successfully!")
        
        # Cleaning results in expandable sections
        with st.expander("📋 Cleaning Report", expanded=True):
            st.json(cleaning_report)
        
        with st.expander("👀 Preview of Cleaned Data"):
            st.dataframe(clean_df.head(50), use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # EDA Section
        st.markdown("""
        <div class="section-card">
            <h2>📈 Exploratory Data Analysis</h2>
        """, unsafe_allow_html=True)
        
        # Graph Type Selection
        st.markdown("**🎯 Choose which types of charts to generate:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            basic_plots = st.checkbox("📊 Basic Plots", value=True, help="Distribution plots, boxplots, violin plots")
            scatter_plots = st.checkbox("🔍 Scatter Plots", value=True, help="Scatter matrix for numeric columns")
        
        with col2:
            time_series = st.checkbox("⏰ Time Series", value=True, help="Time-based analysis for date columns")
            correlation = st.checkbox("🔗 Correlation", value=True, help="Correlation heatmaps and pair plots")
        
        with col3:
            categorical = st.checkbox("📋 Categorical", value=True, help="Bar charts and pie charts for text columns")
            all_plots = st.checkbox("🎨 All Plots", value=False, help="Generate all available chart types")
        
        # Show expected chart count based on selections
        if all_plots:
            st.info("🎨 **All Plots** selected - will generate all available chart types")
        else:
            selected_count = sum([basic_plots, scatter_plots, time_series, correlation, categorical])
            st.info(f"📊 **Selected {selected_count} chart types** - charts will be filtered based on your selection")
        
        # Quick graph type info (moved to footer for better layout)
        st.info("💡 **Tip:** Use the checkboxes above to select which chart types to generate. See footer for detailed information about available chart types.")
        
        try:
            with st.spinner("🔄 Generating charts and analysis..."):
                # Limit charts for very large datasets to avoid memory issues
                if len(clean_df) > 50000:
                    st.info("📊 Large dataset detected. Generating sample-based charts for better performance...")
                    # Sample data for EDA if too large
                    sample_df = clean_df.sample(n=min(10000, len(clean_df)), random_state=42)
                    figs, eda_meta = generate_eda(sample_df)
                else:
                    figs, eda_meta = generate_eda(clean_df)
                
                # Filter charts based on user selections
                filtered_figs = []
                if all_plots:
                    # If "All Plots" is selected, include everything
                    filtered_figs = figs
                else:
                    # Filter based on individual selections
                    for title, fig in figs:
                        if basic_plots and any(keyword in title for keyword in ["Distribution", "Boxplot", "Violin"]):
                            filtered_figs.append((title, fig))
                        elif scatter_plots and "Scatter" in title:
                            filtered_figs.append((title, fig))
                        elif time_series and "Time Series" in title:
                            filtered_figs.append((title, fig))
                        elif correlation and any(keyword in title for keyword in ["Correlation", "Pair Plot"]):
                            filtered_figs.append((title, fig))
                        elif categorical and "Categorical Analysis" in title:
                            filtered_figs.append((title, fig))
                
                # Use filtered figures
                figs = filtered_figs
            
            # Display charts in columns for better layout
            if figs:
                st.success(f"✅ Generated {len(figs)} charts successfully!")
                
                # Show chart summary
                chart_types = {}
                for title, _ in figs:
                    if "Distribution" in title:
                        chart_types["Distribution Plots"] = chart_types.get("Distribution Plots", 0) + 1
                    elif "Boxplot" in title:
                        chart_types["Boxplots"] = chart_types.get("Boxplots", 0) + 1
                    elif "Violin" in title:
                        chart_types["Violin Plots"] = chart_types.get("Violin Plots", 0) + 1
                    elif "Scatter" in title:
                        chart_types["Scatter Plots"] = chart_types.get("Scatter Plots", 0) + 1
                    elif "Time Series" in title:
                        chart_types["Time Series"] = chart_types.get("Time Series", 0) + 1
                    elif "Correlation" in title:
                        chart_types["Correlation"] = chart_types.get("Correlation", 0) + 1
                    elif "Pair Plot" in title:
                        chart_types["Pair Plots"] = chart_types.get("Pair Plots", 0) + 1
                    elif "Categorical Analysis" in title:
                        chart_types["Categorical Analysis"] = chart_types.get("Categorical Analysis", 0) + 1
                
                # Display chart summary with total count
                if chart_types:
                    total_charts = len(figs)
                    summary_text = f"📊 **Chart Summary:** {', '.join([f'{k}: {v}' for k, v in chart_types.items()])} | **Total: {total_charts} charts**"
                    st.info(summary_text)
                else:
                    st.info(f"📊 **Total Charts Generated:** {len(figs)}")
                
                # Debug: Show user selections and actual charts
                with st.expander("🔍 Debug: Chart Selection vs Generation", expanded=False):
                    st.write("**User Selections:**")
                    st.write(f"- Basic Plots: {basic_plots}")
                    st.write(f"- Scatter Plots: {scatter_plots}")
                    st.write(f"- Time Series: {time_series}")
                    st.write(f"- Correlation: {correlation}")
                    st.write(f"- Categorical: {categorical}")
                    st.write(f"- All Plots: {all_plots}")
                    
                    st.write("**Charts Generated:**")
                    for i, (title, _) in enumerate(figs):
                        st.write(f"{i+1}. {title}")
                
                # Display charts in 2-column layout with better spacing
                cols = st.columns(2)
                for i, (title, fig) in enumerate(figs):
                    col_idx = i % 2
                    with cols[col_idx]:
                        st.markdown(f"**{title}**")
                        st.pyplot(fig)
                        st.markdown("---")  # Add separator between charts
            else:
                st.info("ℹ️ No charts generated. This might happen with very small datasets or specific data types.")
                figs = []
        except Exception as e:
            st.error(f"❌ Error generating EDA: {str(e)}")
            st.info("💡 Try uploading a different dataset or check the data format.")
            figs = []
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Chat with Data Section
        st.markdown("""
        <div class="section-card">
            <h2>💬 Chat with Your Data</h2>
            <p style="color: #666; margin-bottom: 1rem;">Ask questions about your dataset in natural language</p>
        """, unsafe_allow_html=True)
        
        # Question input with better styling
        col1, col2 = st.columns([3, 1])
        with col1:
            user_q = st.text_input("💭 Your question", placeholder="e.g., 'minimum age', 'top 5 names', 'sales in July'")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            answer_clicked = st.button("🚀 Answer", use_container_width=True)
        
        if answer_clicked and user_q.strip():
            try:
                with st.spinner("🤔 Analyzing your question..."):
                    # Use sample data for large datasets in Q&A
                    if len(clean_df) > 50000:
                        qa_df = clean_df.sample(n=min(10000, len(clean_df)), random_state=42)
                        st.info("📊 Using sample data for faster analysis of large dataset.")
                    else:
                        qa_df = clean_df
                    
                    qa = answer_question(qa_df, user_q)
                
                # Display results in a nice format
                if qa.message:
                    st.info(f"💡 **Answer:** {qa.message}")
                
                if qa.table is not None:
                    with st.expander("📊 Results Table", expanded=True):
                        st.dataframe(qa.table, use_container_width=True)
                
                if qa.figure is not None:
                    st.pyplot(qa.figure)
                    figs.append(("Q&A Chart", qa.figure))
            except Exception as e:
                st.error(f"❌ Error processing question: {str(e)}")
                st.info("💡 Try rephrasing your question or check if the data contains the columns you're asking about.")
        
        # Helpful suggestions
        st.markdown("""
        <div style="background: #f0f2f6; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
            <h4>💡 Try asking about:</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">
                <li>Sales in July 2024</li>
                <li>Top 10 products</li>
                <li>Average price by category</li>
                <li>Monthly trends</li>
                <li>Count by region</li>
                <li>Minimum/maximum values</li>
                <li>Data quality and missing values</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Insights Section
        st.markdown("""
        <div class="section-card">
            <h2>💡 Automated Insights</h2>
        """, unsafe_allow_html=True)
        
        try:
            with st.spinner("🔍 Generating insights..."):
                # Use sample data for large datasets in insights
                if len(clean_df) > 50000:
                    insights_df = clean_df.sample(n=min(10000, len(clean_df)), random_state=42)
                    st.info("📊 Using sample data for insights generation on large dataset.")
                else:
                    insights_df = clean_df
                
                insights_text = generate_insights(insights_df)
                st.success("✅ Insights generated successfully!")
                
                # Display insights in a more prominent way
                st.markdown("""
                <div style="background: #f8f9ff; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea;">
                    <h4>🔍 Key Findings:</h4>
                    <p style="font-size: 1.1rem; margin: 0;">{}</p>
                </div>
                """.format(insights_text), unsafe_allow_html=True)
                
                # Also show raw insights text for debugging
                with st.expander("📋 Raw Insights Data", expanded=False):
                    st.write("**Generated insights text:**")
                    st.code(insights_text)
                    
                    st.write("**Dataset used for insights:**")
                    st.write(f"- Rows: {len(insights_df):,}")
                    st.write(f"- Columns: {len(insights_df.columns)}")
                    st.write(f"- Sample size: {len(insights_df)}")
                
        except Exception as e:
            st.error(f"❌ Error generating insights: {str(e)}")
            st.info("💡 This might happen with very small datasets or specific data types.")
            insights_text = "Unable to generate insights due to an error."
            
            # Show error details
            with st.expander("🐛 Error Details", expanded=True):
                st.error(f"Error: {str(e)}")
                st.write("**Dataset info:**")
                st.write(f"- Rows: {len(clean_df):,}")
                st.write(f"- Columns: {len(clean_df.columns)}")
                st.write(f"- Column types: {dict(clean_df.dtypes)}")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Exports Section
        st.markdown("""
        <div class="section-card">
            <h2>📤 Export Reports</h2>
            <p style="color: #666; margin-bottom: 1rem;">Download your analysis in various formats</p>
        """, unsafe_allow_html=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(uploaded.name)[0]

        # Export buttons in columns
        col1, col2, col3 = st.columns(3)
        
        if output_excel:
            with col1:
                try:
                    with st.spinner("📊 Generating Excel..."):
                        excel_bytes = export_excel_with_summary(clean_df, overview, cleaning_report, insights_text, file_basename=base_name, figs=figs)
                        st.download_button(
                            label="📊 Download Excel",
                            data=excel_bytes,
                            file_name=f"{base_name}_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        st.success("✅ Excel export ready!")
                except Exception as e:
                    st.error(f"❌ Error generating Excel: {str(e)}")

        if output_powerbi:
            with col2:
                try:
                    with st.spinner("🔗 Preparing Power BI..."):
                        powerbi_bytes = export_powerbi_bundle(clean_df, figs=figs)
                        st.download_button(
                            label="🔗 Download Power BI ZIP",
                            data=powerbi_bytes,
                            file_name=f"{base_name}_{timestamp}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                        st.success("✅ Power BI bundle ready!")
                except Exception as e:
                    st.error(f"❌ Error generating Power BI bundle: {str(e)}")

        if output_pdf:
            with col3:
                try:
                    with st.spinner("📄 Generating PDF..."):
                        pdf_bytes = export_pdf_report(base_name, overview, cleaning_report, insights_text, figs=figs)
                        st.download_button(
                            label="📄 Download PDF",
                            data=pdf_bytes,
                            file_name=f"{base_name}_{timestamp}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("✅ PDF report ready!")
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Success message
        st.markdown("""
        <div class="success-box">
            <h3>🎉 Analysis Complete!</h3>
            <p>Your dataset has been successfully analyzed. All sections are now available above.</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error in data processing pipeline: {str(e)}")
        st.info("💡 The dataset might be too large or have an unsupported format. Try a smaller dataset or different file format.")
        
        # Show what we can still do
        st.markdown("""
        <div class="section-card">
            <h2>⚠️ Limited Functionality Available</h2>
            <p>Due to processing errors, some features are limited. You can still:</p>
            <ul>
                <li>View the raw data structure</li>
                <li>Export the original dataset</li>
                <li>Try with a smaller sample of your data</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize empty variables for exports
        clean_df = df
        cleaning_report = {"error": "Processing failed", "rows_before": len(df), "rows_after": len(df)}
        insights_text = "Unable to generate insights due to processing error."
        figs = []

else:
    # Welcome message when no file uploaded
    st.markdown("""
    <div class="info-box">
        <h2>🚀 Welcome to Data Analyst Automation!</h2>
        <p style="font-size: 1.1rem;">Upload a dataset to get started with automated analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea;">🔍 Auto-Analysis</h3>
            <p>Automatic data profiling, cleaning, and insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea;">💬 Smart Q&A</h3>
            <p>Ask questions about your data in natural language</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea;">📤 Multi-Format Export</h3>
            <p>Export to Excel, Power BI, and PDF with charts</p>
        </div>
        """, unsafe_allow_html=True)

# Footer with About Us and Security Features (always visible)
st.markdown("---")

# About Us Section
st.markdown("## 🏢 About Data Analyst Automation Platform")

# Mission and Features
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Our Mission")
    st.write("We provide enterprise-grade data analysis automation that transforms raw data into actionable insights. Our platform empowers analysts, business users, and data scientists to extract maximum value from their datasets.")
    
    st.markdown("### 🚀 Key Features")
    st.write("• 🔍 Automated Data Profiling & Cleaning")
    st.write("• 📊 Intelligent Chart Generation")
    st.write("• 💬 Natural Language Q&A")
    st.write("• 📤 Multi-Format Export (Excel, Power BI, PDF)")
    st.write("• ⚡ Large Dataset Optimization")
    st.write("• 🎨 Professional Visualizations")

with col2:
    st.markdown("### 🔒 Security & Privacy Features")
    st.write("• 🛡️ **No Data Storage:** Your data is processed in-memory only")
    st.write("• 🔐 **Local Processing:** All analysis runs on your local machine")
    st.write("• 🚫 **No External APIs:** No data sent to third-party services")
    st.write("• 💾 **Secure Exports:** Files generated locally with your data")
    st.write("• 🔒 **Privacy First:** Zero data retention or tracking")
    st.write("• ⚡ **Offline Capable:** Works without internet connection")
    
    st.markdown("### 📚 Available Chart Types")
    st.write("• 📊 Distribution, Box, Violin Plots")
    st.write("• 🔍 Scatter Matrix & Correlation Heatmaps")
    st.write("• ⏰ Time Series Analysis")
    st.write("• 📋 Categorical Analysis (Bar/Pie Charts)")
    st.write("• 🎯 Pair Plot Matrices")

# Chart Display Features
st.markdown("### 🎨 Chart Display Features")
col3, col4, col5 = st.columns(3)
with col3:
    st.write("• 📱 Responsive 2-column layout")
    st.write("• 🔍 Clear chart titles and separators")
with col4:
    st.write("• ⚡ Optimized for large datasets")
    st.write("• 🎯 User-selectable chart types")
with col5:
    st.write("• 📊 Smart chart filtering")
    st.write("• 🎨 Professional styling")

# Footer info
st.markdown("---")
st.markdown("**Built with ❤️ using Python, Streamlit, Pandas, and Matplotlib**")
st.caption("Version 2.0 • Enterprise-Ready Data Analysis Platform")
