import io
import os
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.loaders import detect_and_load
from src.profiling import compute_overview
from src.cleaning import auto_clean
from src.eda import generate_eda
from src.insights import generate_insights
from src.exports import export_excel_with_summary, export_powerbi_csv, export_powerbi_bundle, export_pdf_report
from src.nlqa import answer_question

# Security configuration
import secrets
import hashlib
import time

# Generate secure session token
if 'session_token' not in st.session_state:
    st.session_state.session_token = secrets.token_hex(32)
    st.session_state.login_time = time.time()

# Session timeout (8 hours)
SESSION_TIMEOUT = 8 * 60 * 60
if time.time() - st.session_state.login_time > SESSION_TIMEOUT:
    st.error("⚠ Session expired. Please refresh the page to continue.")
    st.stop()

# Rate limiting
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0
    st.session_state.last_request_time = time.time()

current_time = time.time()
if current_time - st.session_state.last_request_time < 1:  # 1 second cooldown
    st.session_state.request_count += 1
    if st.session_state.request_count > 10:  # Max 10 requests per second
        st.error("⚠ Too many requests. Please wait a moment.")
        st.stop()
else:
    st.session_state.request_count = 1
    st.session_state.last_request_time = current_time

# Page configuration
st.set_page_config(
    page_title="Data Analyst Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Auto-enable embed mode on Streamlit Cloud (keeps localhost unchanged)
st.markdown("""
<script>
(function() {
  try {
    const isCloud = location.hostname.endsWith('streamlit.app');
    if (!isCloud) return; // only enforce on hosted site
    const url = new URL(window.location.href);
    if (url.searchParams.get('embed') !== 'true') {
      url.searchParams.set('embed', 'true');
      // Redirect the TOP document (Streamlit Cloud shell) if we're inside an iframe
      if (window.top && window.top !== window.self) {
        try { window.top.location.replace(url.toString()); }
        catch (e) { window.location.replace(url.toString()); }
      } else {
        window.location.replace(url.toString());
      }
    }
  } catch (e) { /* no-op */ }
})();
</script>
""", unsafe_allow_html=True)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Corporate Blue & Gray color system */
    :root {
        --primary: #1A73E8;     /* Google Blue */
        --secondary: #F1F3F4;   /* Light Gray */
        --accent: #34A853;      /* Success Green */
        --text: #202124;        /* Dark Gray */
        --card-border: #E0E3E7; /* Neutral border */
        --shadow: rgba(0, 0, 0, 0.06);
    }
    /* Hide Streamlit Cloud UI elements */
    footer {visibility: hidden;}
    
    /* Hide share button and GitHub link */
    .stDeployButton {display: none;}
    
    /* Hide the "made with streamlit" footer */
    .stApp > footer {display: none;}
    
    /* Hide the "deployed on streamlit cloud" banner */
    .stApp > div[data-testid="stDecoration"] {display: none;}
    
    /* Hide Streamlit header right-side actions (Share, GitHub, Star, three-dots) but keep left menu */
    /* Keep the first child (hamburger/menu) and hide the rest in the toolbar */
    header [data-testid="stToolbar"] > div:not(:first-child) {display: none !important;}
    /* Additional fallbacks for different Streamlit DOM structures */
    .stApp header div[data-testid="stToolbar"] > div:nth-child(2) {display: none !important;}
    .stApp header div[data-testid="stToolbar"] > div:nth-child(3) {display: none !important;}
    
    .main-header {
        background: var(--primary);
        padding: 1.5rem;
        border-radius: 14px;
        color: #fff;
        text-align: center;
        margin-bottom: 1.25rem;
    }
    .metric-card {
        background: #fff;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid var(--card-border);
        box-shadow: 0 2px 6px var(--shadow);
    }
    .section-card {
        background: #fff;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid var(--card-border);
        box-shadow: 0 2px 6px var(--shadow);
        margin-bottom: 1.25rem;
    }
    .success-box {
        background: var(--accent);
        color: #fff;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background: var(--primary);
        color: #fff;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background: var(--primary);
        color: #fff;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.25rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px var(--shadow);
    }
    .upload-area {
        border: 2px dashed var(--primary);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        background: var(--secondary);
    }
    
    /* Security warning styles */
    .security-warning {
        background: #EA4335;
        color: #fff;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        border: 2px solid #D93025;
    }
    
    .security-info {
        background: var(--accent);
        color: #fff;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        border: 2px solid #2C8C47;
    }
    
    /* Completely hide the sidebar and its hamburger toggle to create a clean, centered layout */
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    
    /* Expand main content to full width when sidebar is hidden */
    .stApp [data-testid="stAppViewContainer"] > .main { width: 100% !important; }
    
    /* Global text color */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp li, .stApp label, .stApp span {
        color: var(--text);
    }
</style>
""", unsafe_allow_html=True)

# Robust JS to hide header right-side controls (Share, GitHub, Star, three-dots)
st.markdown("""
<script>
(function() {
  function hideHeaderActions() {
    try {
      const doc = window.parent ? window.parent.document : document;
      const header = doc.querySelector('header');
      if (!header) return;
      const toolbar = header.querySelector('[data-testid="stToolbar"]') || header;

      const candidates = Array.from(toolbar.querySelectorAll('a, button, div, svg'));
      candidates.forEach(function(el) {
        const text = (el.innerText || '').trim().toLowerCase();
        const label = (el.getAttribute('aria-label') || '').toLowerCase();
        const title = (el.getAttribute('title') || '').toLowerCase();
        const href = (el.getAttribute('href') || '').toLowerCase();

        const isAction =
          /share|github|star|more|overflow/.test(text) ||
          /share|github|star|more|overflow/.test(label) ||
          /share|github|star|more|overflow/.test(title) ||
          (href && href.includes('github.com'));

        if (isAction) {
          let node = el;
          // bubble up to clickable container
          for (let i = 0; i < 4 && node && node !== toolbar; i++) {
            if (node.tagName === 'A' || node.tagName === 'BUTTON') break;
            node = node.parentElement;
          }
          if (node && node !== toolbar) {
            node.style.setProperty('display', 'none', 'important');
          }
        }
      });
    } catch (e) {
      // no-op
    }
  }

  // Run now and also on future DOM changes
  hideHeaderActions();
  const doc = window.parent ? window.parent.document : document;
  const observer = new MutationObserver(hideHeaderActions);
  observer.observe(doc.body, { childList: true, subtree: true });
  // Periodic fallback
  setInterval(hideHeaderActions, 1500);
})();
</script>
""", unsafe_allow_html=True)

# Security features active in background (no UI display)

# Professional header with navigation hint
st.markdown("""
<div class="main-header">
    <h1>📊 Data Analyst Automation Tool</h1>
    <p style="font-size: 1.2rem; margin: 0;">Upload a dataset (CSV, Excel, JSON), auto-analyze, and export comprehensive reports</p>
    <p style="font-size: 0.9rem; margin: 0.5rem 0 0 0; opacity: 0.8;">💡 Use the menu (☰) in the top-left to access upload options</p>
</div>
""", unsafe_allow_html=True)

# Centered Upload Section (replaces sidebar uploader)
uploaded = None
left, center, right = st.columns([1, 2, 1])
with center:
    st.markdown("""
    <div class="upload-area" style="border: 2px dashed #667eea; border-radius: 15px; padding: 2rem; text-align: center; background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%); margin-bottom: 1.5rem;">
        <h4 style="margin: 0 0 1rem 0; color: #667eea; font-size: 1.2rem;">📁 Upload Dataset</h4>
        <p style="margin: 0 0 0.5rem 0; color: #555; font-weight: 500;">Drag and drop or browse to upload</p>
        <p style="font-size: 0.85rem; color: #777; margin: 0;">Limit: 200MB • Formats: CSV, XLSX, XLS, JSON</p>
    </div>
    """, unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["csv", "xlsx", "xls", "json"], label_visibility="collapsed", key="main_uploader")

# Professional sidebar with enhanced styling
output_excel = True
output_powerbi = True
output_pdf = True

# Export options toggles in main area
opt_col1, opt_col2, opt_col3 = st.columns(3)
with opt_col1:
    output_excel = st.checkbox("📊 Excel Report (cleaned data + summary + charts)", value=True)
with opt_col2:
    output_powerbi = st.checkbox("🔗 Power BI Bundle (CSV + charts ZIP)", value=True)
with opt_col3:
    output_pdf = st.checkbox("📄 PDF Report (professional report with charts)", value=True)

# Main content
if uploaded is not None:
    # Additional security checks
    try:
        # Loading section with security logging
        with st.spinner("🔄 Loading and analyzing dataset..."):
            # Log file access attempt
            st.session_state.last_file_access = time.time()
            
            # Validate file content before processing
            if uploaded.size == 0:
                st.error("⚠ Empty file detected. Please upload a valid dataset.")
                st.stop()
            
            df, meta = detect_and_load(uploaded, uploaded.name)
            
            # Validate dataframe
            if df is None or df.empty:
                st.error("⚠ Invalid dataset. Please check your file format.")
                st.stop()
                
    except Exception as e:
        st.error(f"⚠ Security Error: {str(e)}")
        st.info("🔒 File processing blocked due to security concerns.")
        st.stop()
    
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
        st.write("*Dataset Info:*")
        st.write(f"- File name: {uploaded.name}")
        st.write(f"- File size: {uploaded.size / 1024 / 1024:.2f} MB")
        st.write(f"- Rows: {df.shape[0]:,}")
        st.write(f"- Columns: {df.shape[1]}")
        st.write(f"- Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    with col2:
        st.write("*Column Types:*")
        for col in df.columns:
            st.write(f"- {col}: {df[col].dtype}")
    
    # Show first few rows
    st.write("*First 5 rows of data:*")
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
        st.markdown("🎯 Choose which types of charts to generate:")
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
            st.info("🎨 *All Plots* selected - will generate all available chart types")
        else:
            selected_count = sum([basic_plots, scatter_plots, time_series, correlation, categorical])
            st.info(f"📊 *Selected {selected_count} chart types* - charts will be filtered based on your selection")
        
        # Quick graph type info (moved to footer for better layout)
        st.info("💡 *Tip:* Use the checkboxes above to select which chart types to generate. See footer for detailed information about available chart types.")
        
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
                    summary_text = f"📊 *Chart Summary:* {', '.join([f'{k}: {v}' for k, v in chart_types.items()])} | *Total: {total_charts} charts*"
                    st.info(summary_text)
                else:
                    st.info(f"📊 *Total Charts Generated:* {len(figs)}")
                
                # Debug: Show user selections and actual charts
                with st.expander("🔍 Debug: Chart Selection vs Generation", expanded=False):
                    st.write("*User Selections:*")
                    st.write(f"- Basic Plots: {basic_plots}")
                    st.write(f"- Scatter Plots: {scatter_plots}")
                    st.write(f"- Time Series: {time_series}")
                    st.write(f"- Correlation: {correlation}")
                    st.write(f"- Categorical: {categorical}")
                    st.write(f"- All Plots: {all_plots}")
                    
                    st.write("*Charts Generated:*")
                    for i, (title, _) in enumerate(figs):
                        st.write(f"{i+1}. {title}")
                
                # Display charts in 2-column layout with better spacing
                cols = st.columns(2)
                for i, (title, fig) in enumerate(figs):
                    col_idx = i % 2
                    with cols[col_idx]:
                        st.markdown(f"{title}")
                        st.pyplot(fig)
                        st.markdown("---")  # Add separator between charts
            else:
                st.info("ℹ No charts generated. This might happen with very small datasets or specific data types.")
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
                    st.info(f"💡 *Answer:* {qa.message}")
                
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
                    st.write("*Generated insights text:*")
                    st.code(insights_text)
                    
                    st.write("*Dataset used for insights:*")
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
                st.write("*Dataset info:*")
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
            <h2>⚠ Limited Functionality Available</h2>
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
    # Professional welcome message
    st.markdown("""
    <div class="info-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.25rem 1.5rem; border-radius: 16px; color: white; text-align: center; margin-bottom: 1.25rem; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.25);">
        <h2 style="margin: 0 0 0.5rem 0; font-size: 1.6rem;">🚀 Data Analyst Automation</h2>
        <p style="font-size: 1rem; margin: 0; opacity: 0.9;">Upload a dataset to start fast, automated analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show upload prompt again in welcome state
    with center:
        st.markdown("""
        <div class="upload-area" style="border: 2px dashed #667eea; border-radius: 15px; padding: 2rem; text-align: center; background: #f8f9ff;">
            <strong>📁 Choose a file above to begin</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature highlights (concise)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card" style="background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #eaeaea; box-shadow: 0 2px 6px rgba(0,0,0,0.06); text-align: center;">
            <h3 style="color: #667eea; margin: 0 0 0.5rem 0; font-size: 1.1rem;">🔍 Auto-Analysis</h3>
            <p style="color: #666; margin: 0;">Profile, clean, and visualize</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card" style="background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #eaeaea; box-shadow: 0 2px 6px rgba(0,0,0,0.06); text-align: center;">
            <h3 style="color: #667eea; margin: 0 0 0.5rem 0; font-size: 1.1rem;">💬 Smart Q&A</h3>
            <p style="color: #666; margin: 0;">Ask in plain English</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card" style="background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #eaeaea; box-shadow: 0 2px 6px rgba(0,0,0,0.06); text-align: center;">
            <h3 style="color: #667eea; margin: 0 0 0.5rem 0; font-size: 1.1rem;">📤 Exports</h3>
            <p style="color: #666; margin: 0;">Excel, Power BI, PDF</p>
        </div>
        """, unsafe_allow_html=True)

# Clean footer without security banners
st.markdown("---")

with st.expander("About this app", expanded=False):
    colA, colB = st.columns(2)
    with colA:
        st.write("• Automated profiling and cleaning")
        st.write("• Smart chart generation")
        st.write("• Natural language Q&A")
    with colB:
        st.write("• Local processing, no data leaves your machine")
        st.write("• Export to Excel, Power BI, PDF")
        st.write("• Optimized for large datasets")

# Footer info
st.markdown("---")
st.markdown("*Built with ❤ using Python, Streamlit, Pandas, and Matplotlib*")
st.caption("Version 2.0 • Enterprise-Ready Data Analysis Platform")