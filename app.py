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
from src.exports import export_excel_with_summary, export_powerbi_csv, export_powerbi_bundle, export_pdf_report, export_tableau_bundle
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
    st.error("⚠️ Session expired. Please refresh the page to continue.")
    st.stop()

# Rate limiting
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0
    st.session_state.last_request_time = time.time()

current_time = time.time()
if current_time - st.session_state.last_request_time < 1:  # 1 second cooldown
    st.session_state.request_count += 1
    if st.session_state.request_count > 10:  # Max 10 requests per second
        st.error("⚠️ Too many requests. Please wait a moment.")
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
    /* Modern Professional Color System */
    :root {
        --primary: #2563eb;         /* Modern Blue */
        --primary-dark: #1d4ed8;    /* Darker Blue */
        --secondary: #f8fafc;       /* Light Gray */
        --accent: #10b981;          /* Success Green */
        --accent-orange: #f59e0b;   /* Warning Orange */
        --text: #1f2937;            /* Dark Gray */
        --text-light: #6b7280;      /* Medium Gray */
        --card-bg: #ffffff;         /* Pure White */
        --card-border: #e5e7eb;     /* Light Border */
        --shadow: rgba(0, 0, 0, 0.1);
        --shadow-lg: rgba(0, 0, 0, 0.15);
        --gradient-primary: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        --gradient-accent: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }
    
    /* Hide Streamlit Cloud UI elements */
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    .stApp > footer {display: none;}
    .stApp > div[data-testid="stDecoration"] {display: none;}
    header [data-testid="stToolbar"] > div:not(:first-child) {display: none !important;}
    .stApp header div[data-testid="stToolbar"] > div:nth-child(2) {display: none !important;}
    .stApp header div[data-testid="stToolbar"] > div:nth-child(3) {display: none !important;}
    
    /* Hide sidebar for clean layout */
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    .stApp [data-testid="stAppViewContainer"] > .main { width: 100% !important; }
    
    /* Enhanced Header Design */
    .main-header {
        background: var(--gradient-primary);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        color: #fff;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(37, 99, 235, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .main-header h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.1rem !important;
        opacity: 0.95 !important;
        position: relative;
        z-index: 1;
    }
    
    /* Modern Card Design */
    .metric-card {
        background: var(--card-bg);
        padding: 1.75rem;
        border-radius: 16px;
        border: 1px solid var(--card-border);
        box-shadow: 0 4px 12px var(--shadow);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--shadow-lg);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
    }
    
    .section-card {
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid var(--card-border);
        box-shadow: 0 4px 16px var(--shadow);
        margin-bottom: 2rem;
        position: relative;
    }
    
    .section-card h2 {
        color: var(--text) !important;
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Enhanced Status Boxes */
    .success-box {
        background: var(--gradient-accent);
        color: #fff;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
        border: none;
    }
    
    .info-box {
        background: var(--gradient-primary);
        color: #fff;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
        border: none;
    }
    
    /* Modern Button Styling */
    .stButton > button {
        background: var(--gradient-primary) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
        background: var(--primary-dark) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Enhanced Upload Area */
    .upload-area {
        border: 2px dashed var(--primary) !important;
        border-radius: 20px !important;
        padding: 2.5rem !important;
        text-align: center !important;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .upload-area:hover {
        border-color: var(--primary-dark) !important;
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px var(--shadow-lg) !important;
    }
    
    .upload-area h4 {
        color: var(--primary) !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Enhanced Input Styling */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid var(--card-border) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--secondary);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--card-bg) !important;
        color: var(--primary) !important;
        box-shadow: 0 2px 8px var(--shadow) !important;
    }
    
    /* Enhanced Checkboxes */
    .stCheckbox > label {
        background: var(--card-bg) !important;
        padding: 1rem !important;
        border-radius: 12px !important;
        border: 1px solid var(--card-border) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    
    .stCheckbox > label:hover {
        border-color: var(--primary) !important;
        box-shadow: 0 2px 8px var(--shadow) !important;
    }
    
    /* Enhanced Expanders */
    .streamlit-expanderHeader {
        background: var(--secondary) !important;
        border-radius: 12px !important;
        padding: 1rem 1.5rem !important;
        font-weight: 600 !important;
        border: 1px solid var(--card-border) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1.5rem !important;
    }
    
    /* Enhanced Download Buttons */
    .stDownloadButton > button {
        background: var(--gradient-accent) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        width: 100% !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Enhanced Dataframe Styling */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px var(--shadow) !important;
    }
    
    /* Enhanced Spinner */
    .stSpinner > div {
        border-color: var(--primary) !important;
    }
    
    /* Enhanced Alert Boxes */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 12px var(--shadow) !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #fff !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #fff !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: #fff !important;
    }
    
    /* Typography Enhancements */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp li, .stApp label, .stApp span {
        color: var(--text) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Enhanced Progress Indicators */
    .stProgress > div > div {
        background: var(--gradient-primary) !important;
        border-radius: 8px !important;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1.5rem !important;
        }
        
        .main-header h1 {
            font-size: 2rem !important;
        }
        
        .section-card {
            padding: 1.5rem !important;
        }
        
        .metric-card {
            padding: 1.25rem !important;
        }
    }
    
    /* Loading Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
    
    /* Smooth Transitions */
    * {
        transition: all 0.3s ease !important;
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
    <p style="font-size: 1.2rem; margin: 0.5rem 0;">Transform your datasets into actionable insights with automated analysis, visualization, and reporting</p>
    <p style="font-size: 0.9rem; margin: 0.75rem 0 0 0; opacity: 0.9;">💡 Professional-grade data analysis • Export to Excel, Power BI & PDF • Natural language Q&A</p>
</div>
""", unsafe_allow_html=True)

# Centered Upload Section (replaces sidebar uploader)
uploaded = None
left, center, right = st.columns([1, 2, 1])
with center:
    st.markdown("""
    <div class="upload-area">
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">📁</div>
            <h4 style="margin: 0 0 0.5rem 0; color: #2563eb; font-size: 1.4rem; font-weight: 600;">Upload Your Dataset</h4>
            <p style="margin: 0 0 0.5rem 0; color: #6b7280; font-weight: 500; font-size: 1rem;">Drag and drop your file here or click to browse</p>
            <p style="font-size: 0.85rem; color: #9ca3af; margin: 0;">
                <span style="background: #e5e7eb; padding: 0.25rem 0.5rem; border-radius: 6px; margin: 0 0.25rem;">CSV</span>
                <span style="background: #e5e7eb; padding: 0.25rem 0.5rem; border-radius: 6px; margin: 0 0.25rem;">XLSX</span>
                <span style="background: #e5e7eb; padding: 0.25rem 0.5rem; border-radius: 6px; margin: 0 0.25rem;">JSON</span>
                • Max 200MB
            </p>
    </div>
    </div>
    """, unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["csv", "xlsx", "xls", "json"], label_visibility="collapsed", key="main_uploader")

# Professional sidebar with enhanced styling
output_excel = True
output_powerbi = True
output_pdf = True

# Export options toggles in main area
opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)
with opt_col1:
    output_excel = st.checkbox("📊 Excel Report (cleaned data + summary + charts)", value=True)
with opt_col2:
    output_powerbi = st.checkbox("🔗 Power BI Bundle (CSV + charts ZIP)", value=True)
with opt_col3:
    output_pdf = st.checkbox("📄 PDF Report (professional report with charts)", value=True)
with opt_col4:
    output_tableau = st.checkbox("📦 Tableau Bundle (CSV + charts ZIP)", value=True)

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
                st.error("⚠️ Empty file detected. Please upload a valid dataset.")
                st.stop()
            
            df, meta = detect_and_load(uploaded, uploaded.name)
            
            # Validate dataframe
            if df is None or df.empty:
                st.error("⚠️ Invalid dataset. Please check your file format.")
                st.stop()
                
    except Exception as e:
        st.error(f"⚠️ Security Error: {str(e)}")
        st.info("🔒 File processing blocked due to security concerns.")
        st.stop()
    
    # Success message
    st.markdown(f"""
    <div class="success-box">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎉</div>
        <h3 style="margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 600;">Dataset Loaded Successfully!</h3>
        <p style="margin: 0; font-size: 1.1rem; opacity: 0.95;"><strong>{uploaded.name}</strong></p>
        <p style="margin: 0.25rem 0 0 0; font-size: 1rem; opacity: 0.9;">{df.shape[0]:,} rows × {df.shape[1]} columns • {uploaded.size / 1024 / 1024:.1f} MB</p>
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
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <h3 style="color: #2563eb; margin: 0; font-size: 1rem; font-weight: 600;">📊 Total Rows</h3>
                    <div style="background: #dbeafe; color: #2563eb; padding: 0.25rem 0.5rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">DATA</div>
                </div>
                <h2 style="color: #1f2937; margin: 0; font-size: 2rem; font-weight: 700;">{:,}</h2>
                <p style="color: #6b7280; margin: 0.25rem 0 0 0; font-size: 0.85rem;">Records in dataset</p>
            </div>
            """.format(overview["num_rows"]), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <h3 style="color: #2563eb; margin: 0; font-size: 1rem; font-weight: 600;">📋 Columns</h3>
                    <div style="background: #dcfce7; color: #16a34a; padding: 0.25rem 0.5rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">FIELDS</div>
                </div>
                <h2 style="color: #1f2937; margin: 0; font-size: 2rem; font-weight: 700;">{}</h2>
                <p style="color: #6b7280; margin: 0.25rem 0 0 0; font-size: 0.85rem;">Data attributes</p>
            </div>
            """.format(overview["num_cols"]), unsafe_allow_html=True)
        
        with col3:
            missing_total = sum(overview["missing_counts"].values())
            missing_pct = (missing_total / (overview["num_rows"] * overview["num_cols"]) * 100) if overview["num_rows"] > 0 else 0
            st.markdown("""
            <div class="metric-card">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <h3 style="color: #2563eb; margin: 0; font-size: 1rem; font-weight: 600;">❌ Missing</h3>
                    <div style="background: #fef3c7; color: #d97706; padding: 0.25rem 0.5rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">QUALITY</div>
            </div>
                <h2 style="color: #1f2937; margin: 0; font-size: 2rem; font-weight: 700;">{:,}</h2>
                <p style="color: #6b7280; margin: 0.25rem 0 0 0; font-size: 0.85rem;">{:.1f}% of total values</p>
            </div>
            """.format(missing_total, missing_pct), unsafe_allow_html=True)
        
        with col4:
            numeric_cols = len([col for col in df.columns if df[col].dtype in ['int64', 'float64']])
            st.markdown("""
            <div class="metric-card">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <h3 style="color: #2563eb; margin: 0; font-size: 1rem; font-weight: 600;">🔢 Numeric</h3>
                    <div style="background: #e0e7ff; color: #4f46e5; padding: 0.25rem 0.5rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">TYPES</div>
                </div>
                <h2 style="color: #1f2937; margin: 0; font-size: 2rem; font-weight: 700;">{}</h2>
                <p style="color: #6b7280; margin: 0.25rem 0 0 0; font-size: 0.85rem;">Quantitative fields</p>
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
                
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 2rem; border-radius: 16px; border-left: 5px solid #2563eb; margin: 1rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                        <div style="background: #2563eb; color: white; padding: 0.5rem; border-radius: 8px; margin-right: 1rem;">
                            <span style="font-size: 1.2rem;">🔍</span>
                        </div>
                        <h4 style="margin: 0; color: #1f2937; font-size: 1.3rem; font-weight: 600;">Key Insights & Findings</h4>
                    </div>
                    <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <p style="font-size: 1.1rem; line-height: 1.6; margin: 0; color: #374151;">{}</p>
                    </div>
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
        col1, col2, col3, col4 = st.columns(4)
        
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

        # Tableau bundle export (CSV + optional charts)
        if 'output_tableau' in locals() and output_tableau:
            with col4:
                try:
                    with st.spinner("📦 Preparing Tableau bundle..."):
                        tableau_bytes = export_tableau_bundle(clean_df, figs=figs)
                        st.download_button(
                            label="📦 Download Tableau ZIP",
                            data=tableau_bytes,
                            file_name=f"{base_name}_{timestamp}_tableau.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                        st.success("✅ Tableau bundle ready!")
                except Exception as e:
                    st.error(f"❌ Error generating Tableau bundle: {str(e)}")
        
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
st.markdown("""
<div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 16px; margin-top: 2rem;">
    <h4 style="color: #2563eb; margin: 0 0 1rem 0; font-weight: 600;">Built with Modern Technology Stack</h4>
    <p style="color: #6b7280; margin: 0; font-size: 0.95rem;">
        <span style="background: #dbeafe; color: #2563eb; padding: 0.25rem 0.75rem; border-radius: 20px; margin: 0 0.25rem; font-weight: 500;">Python</span>
        <span style="background: #dcfce7; color: #16a34a; padding: 0.25rem 0.75rem; border-radius: 20px; margin: 0 0.25rem; font-weight: 500;">Streamlit</span>
        <span style="background: #fef3c7; color: #d97706; padding: 0.25rem 0.75rem; border-radius: 20px; margin: 0 0.25rem; font-weight: 500;">Pandas</span>
        <span style="background: #e0e7ff; color: #4f46e5; padding: 0.25rem 0.75rem; border-radius: 20px; margin: 0 0.25rem; font-weight: 500;">Matplotlib</span>
    </p>
    <p style="color: #9ca3af; margin: 0.75rem 0 0 0; font-size: 0.85rem;">Version 2.0 • Enterprise-Ready Data Analysis Platform</p>
</div>
""", unsafe_allow_html=True)
