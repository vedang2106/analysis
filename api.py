"""
Flask Backend API for Data Analyst Automation Tool
Exposes all existing backend functions as REST API endpoints
"""
import io
import os
import secrets
import time
from datetime import datetime
from functools import wraps

import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server
import matplotlib.pyplot as plt

from src.loaders import detect_and_load
from src.profiling import compute_overview
from src.cleaning import auto_clean
from src.eda import generate_eda
from src.insights import generate_insights
from src.exports import export_excel_with_summary, export_powerbi_csv, export_powerbi_bundle, export_pdf_report
from src.nlqa import answer_question

app = Flask(__name__)

# Get allowed origins from environment variable or use defaults
# Include common development ports (3000, 3001) for React apps
allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001').split(',')

# Enable CORS for React frontend with proper configuration
CORS(app, resources={
    r"/api/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-Session-ID", "x-session-id"]
    }
})

# Session management
sessions = {}
SESSION_TIMEOUT = 8 * 60 * 60  # 8 hours

# Rate limiting
request_counts = {}


def get_session_id():
    """Get or create session ID from request"""
    # Try multiple header name variations (case-insensitive)
    session_id = request.headers.get('X-Session-ID') or request.headers.get('x-session-id')
    if not session_id or session_id.strip() == '':
        # Generate a new session ID if not provided
        session_id = secrets.token_hex(32)
    return session_id


def check_session(f):
    """Decorator to check session validity"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = get_session_id()
        if session_id not in sessions:
            sessions[session_id] = {
                'login_time': time.time(),
                'token': secrets.token_hex(32)
            }
        else:
            if time.time() - sessions[session_id]['login_time'] > SESSION_TIMEOUT:
                return jsonify({'error': 'Session expired'}), 401
        return f(*args, **kwargs)
    return decorated_function


def check_rate_limit(f):
    """Decorator for rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = get_session_id()
        current_time = time.time()
        
        if session_id not in request_counts:
            request_counts[session_id] = {'count': 0, 'last_time': current_time}
        
        req_info = request_counts[session_id]
        if current_time - req_info['last_time'] < 1:
            req_info['count'] += 1
            if req_info['count'] > 10:
                return jsonify({'error': 'Too many requests'}), 429
        else:
            req_info['count'] = 1
            req_info['last_time'] = current_time
        
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


@app.route('/api/upload', methods=['POST'])
@check_session
@check_rate_limit
def upload_file():
    """Upload and load dataset"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content into BytesIO to avoid seek issues
        file_content = file.read()
        file_size = len(file_content)
        
        if file_size == 0:
            return jsonify({'error': 'Empty file detected'}), 400
        
        # Create a BytesIO object for pandas to read
        file_stream = io.BytesIO(file_content)
        file_stream.seek(0)  # Ensure we're at the beginning
        
        # Load the file
        try:
            df, meta = detect_and_load(file_stream, file.filename)
        except Exception as load_error:
            import traceback
            error_trace = traceback.format_exc()
            print(f"File loading error: {error_trace}")
            return jsonify({
                'error': f'Failed to load file: {str(load_error)}',
                'filename': file.filename,
                'details': error_trace
            }), 500
        
        if df is None or df.empty:
            return jsonify({'error': 'Invalid dataset'}), 400
        
        # Store in session (convert to JSON-serializable format)
        session_id = get_session_id()
        print(f"Upload - Session ID: {session_id}")
        print(f"Upload - Request headers: {dict(request.headers)}")
        
        # Ensure session exists (should be created by decorator, but double-check)
        if session_id not in sessions:
            print(f"Warning: Session {session_id} not found, creating new one")
            sessions[session_id] = {
                'login_time': time.time(),
                'token': secrets.token_hex(32)
            }
        # Safely store data in session
        try:
            sessions[session_id]['df'] = df
            sessions[session_id]['filename'] = file.filename
            sessions[session_id]['meta'] = meta
            print(f"Upload - Successfully stored data in session {session_id}")
            print(f"Upload - Session now has keys: {list(sessions[session_id].keys())}")
        except KeyError as ke:
            print(f"KeyError accessing session {session_id}: {ke}")
            print(f"Available sessions: {list(sessions.keys())}")
            raise
        
        response_data = {
            'success': True,
            'filename': file.filename,
            'shape': {'rows': int(df.shape[0]), 'cols': int(df.shape[1])},
            'file_size': file_size,
            'memory_usage': float(df.memory_usage(deep=True).sum() / 1024 / 1024),
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'session_id': session_id
        }
        
        # Create response and add session ID to header for frontend to read
        response = jsonify(response_data)
        response.headers['X-Session-ID'] = session_id
        return response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Upload error: {error_details}")  # Log to console for debugging
        # Return a cleaner error message to frontend
        error_message = str(e)
        if len(error_message) > 500:
            error_message = error_message[:500] + "..."
        return jsonify({
            'error': error_message,
            'type': type(e).__name__
        }), 500


@app.route('/api/overview', methods=['GET'])
@check_session
@check_rate_limit
def get_overview():
    """Get data overview"""
    try:
        session_id = get_session_id()
        print(f"Overview request - Session ID: {session_id}")
        print(f"Available sessions: {list(sessions.keys())}")
        print(f"Session keys: {list(sessions.get(session_id, {}).keys())}")
        
        if session_id not in sessions:
            return jsonify({
                'error': 'No dataset loaded',
                'session_id': session_id,
                'available_sessions': list(sessions.keys())
            }), 400
        
        if 'df' not in sessions[session_id]:
            return jsonify({
                'error': 'No dataset loaded in session',
                'session_id': session_id,
                'session_keys': list(sessions[session_id].keys())
            }), 400
        
        df = sessions[session_id]['df']
        overview = compute_overview(df)
        
        # Convert DataFrame to dict for JSON serialization
        summary_stats = overview['summary_stats']
        overview['summary_stats'] = summary_stats.to_dict()
        overview['session_id'] = session_id  # Include session ID in response
        
        response = jsonify(overview)
        response.headers['X-Session-ID'] = session_id
        return response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Overview error: {error_details}")
        return jsonify({'error': str(e), 'details': error_details}), 500


@app.route('/api/clean', methods=['POST'])
@check_session
@check_rate_limit
def clean_data():
    """Clean the dataset"""
    try:
        session_id = get_session_id()
        if 'df' not in sessions.get(session_id, {}):
            return jsonify({'error': 'No dataset loaded'}), 400
        
        df = sessions[session_id]['df']
        
        # Clean the data
        clean_df, cleaning_report = auto_clean(df)
        
        # Store cleaned dataframe
        sessions[session_id]['clean_df'] = clean_df
        sessions[session_id]['cleaning_report'] = cleaning_report
        
        # Return preview of cleaned data (first 50 rows)
        preview = clean_df.head(50).to_dict('records')
        
        response_data = {
            'success': True,
            'cleaning_report': cleaning_report,
            'preview': preview,
            'shape': {'rows': int(clean_df.shape[0]), 'cols': int(clean_df.shape[1])},
            'session_id': session_id
        }
        response = jsonify(response_data)
        response.headers['X-Session-ID'] = session_id
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/eda', methods=['POST'])
@check_session
@check_rate_limit
def generate_eda_charts():
    """Generate EDA charts"""
    try:
        session_id = get_session_id()
        if 'clean_df' not in sessions.get(session_id, {}):
            return jsonify({'error': 'Data must be cleaned first'}), 400
        
        clean_df = sessions[session_id]['clean_df']
        
        # Get chart type selections from request
        data = request.get_json() or {}
        chart_selections = data.get('chart_selections', {
            'basic_plots': True,
            'scatter_plots': True,
            'time_series': True,
            'correlation': True,
            'categorical': True,
            'all_plots': False
        })
        
        # Sample for large datasets
        if len(clean_df) > 50000:
            sample_df = clean_df.sample(n=min(10000, len(clean_df)), random_state=42)
        else:
            sample_df = clean_df
        
        # Generate charts
        figs, eda_meta = generate_eda(sample_df)
        
        # Filter charts based on selections
        filtered_figs = []
        if chart_selections.get('all_plots', False):
            filtered_figs = figs
        else:
            for title, fig in figs:
                if chart_selections.get('basic_plots') and any(kw in title for kw in ["Distribution", "Boxplot", "Violin"]):
                    filtered_figs.append((title, fig))
                elif chart_selections.get('scatter_plots') and "Scatter" in title:
                    filtered_figs.append((title, fig))
                elif chart_selections.get('time_series') and "Time Series" in title:
                    filtered_figs.append((title, fig))
                elif chart_selections.get('correlation') and any(kw in title for kw in ["Correlation", "Pair Plot"]):
                    filtered_figs.append((title, fig))
                elif chart_selections.get('categorical') and "Categorical Analysis" in title:
                    filtered_figs.append((title, fig))
        
        # Convert figures to base64 images
        charts = []
        for title, fig in filtered_figs:
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
            charts.append({
                'title': title,
                'image': f'data:image/png;base64,{img_base64}'
            })
            plt.close(fig)
        
        sessions[session_id]['charts'] = filtered_figs
        
        response_data = {
            'success': True,
            'charts': charts,
            'count': len(charts),
            'session_id': session_id
        }
        response = jsonify(response_data)
        response.headers['X-Session-ID'] = session_id
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/qa', methods=['POST'])
@check_session
@check_rate_limit
def answer_qa():
    """Answer natural language questions"""
    try:
        session_id = get_session_id()
        print(f"Q&A request - Session ID: {session_id}")
        
        # Use cleaned data if available, otherwise use original data
        if 'clean_df' in sessions.get(session_id, {}):
            qa_df = sessions[session_id]['clean_df']
            print("Using cleaned data for Q&A")
        elif 'df' in sessions.get(session_id, {}):
            qa_df = sessions[session_id]['df']
            print("Using original data for Q&A (not cleaned yet)")
        else:
            return jsonify({'error': 'No dataset loaded. Please upload a file first.'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No request data provided'}), 400
            
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Sample for large datasets
        if len(qa_df) > 50000:
            qa_df = qa_df.sample(n=min(10000, len(qa_df)), random_state=42)
            print(f"Sampling large dataset: {len(qa_df)} rows")
        
        # Answer question
        print(f"Processing question: {question}")
        qa = answer_question(qa_df, question)
        print(f"Q&A result - message: {bool(qa.message)}, table: {qa.table is not None}, figure: {qa.figure is not None}")
        
        result = {
            'message': qa.message or '',
            'table': None,
            'figure': None,
            'session_id': session_id
        }
        
        if qa.table is not None:
            result['table'] = qa.table.to_dict('records')
        
        if qa.figure is not None:
            img_buffer = io.BytesIO()
            qa.figure.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
            result['figure'] = f'data:image/png;base64,{img_base64}'
            plt.close(qa.figure)
        
        response = jsonify(result)
        response.headers['X-Session-ID'] = session_id
        return response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Q&A error: {error_details}")
        return jsonify({'error': str(e), 'details': error_details}), 500


@app.route('/api/insights', methods=['GET'])
@check_session
@check_rate_limit
def get_insights():
    """Generate insights"""
    try:
        session_id = get_session_id()
        print(f"Insights request - Session ID: {session_id}")
        
        # Use cleaned data if available, otherwise use original data
        if 'clean_df' in sessions.get(session_id, {}):
            insights_df = sessions[session_id]['clean_df']
            print("Using cleaned data for insights")
        elif 'df' in sessions.get(session_id, {}):
            insights_df = sessions[session_id]['df']
            print("Using original data for insights (not cleaned yet)")
        else:
            return jsonify({'error': 'No dataset loaded. Please upload a file first.'}), 400
        
        # Sample for large datasets
        if len(insights_df) > 50000:
            insights_df = insights_df.sample(n=min(10000, len(insights_df)), random_state=42)
            print(f"Sampling large dataset: {len(insights_df)} rows")
        
        insights_text = generate_insights(insights_df)
        
        sessions[session_id]['insights'] = insights_text
        
        response_data = {
            'success': True,
            'insights': insights_text,
            'session_id': session_id
        }
        response = jsonify(response_data)
        response.headers['X-Session-ID'] = session_id
        return response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Insights error: {error_details}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/excel', methods=['GET'])
@check_session
@check_rate_limit
def export_excel():
    """Export Excel report"""
    try:
        session_id = get_session_id()
        print(f"Excel export request - Session ID: {session_id}")
        print(f"Available sessions: {list(sessions.keys())}")
        print(f"Session keys: {list(sessions.get(session_id, {}).keys())}")
        
        # Use cleaned data if available, otherwise use original data
        if session_id not in sessions:
            error_msg = f'Session not found. Session ID: {session_id}'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        if 'clean_df' in sessions[session_id]:
            export_df = sessions[session_id]['clean_df']
            cleaning_report = sessions[session_id].get('cleaning_report', {})
            print("Using cleaned data for Excel export")
        elif 'df' in sessions[session_id]:
            export_df = sessions[session_id]['df']
            cleaning_report = {}  # No cleaning report if data wasn't cleaned
            print("Using original data for Excel export (not cleaned yet)")
        else:
            error_msg = 'No dataset loaded. Please upload a file first.'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        overview = compute_overview(export_df)
        insights_text = sessions[session_id].get('insights', '')
        filename = sessions[session_id].get('filename', 'dataset')
        base_name = os.path.splitext(filename)[0]
        charts = sessions[session_id].get('charts', [])
        
        excel_bytes = export_excel_with_summary(
            export_df, overview, cleaning_report, insights_text,
            file_basename=base_name, figs=charts
        )
        
        return send_file(
            io.BytesIO(excel_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Excel export error: {error_details}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/powerbi', methods=['GET'])
@check_session
@check_rate_limit
def export_powerbi():
    """Export Power BI bundle"""
    try:
        session_id = get_session_id()
        print(f"Power BI export request - Session ID: {session_id}")
        print(f"Available sessions: {list(sessions.keys())}")
        
        if session_id not in sessions:
            error_msg = f'Session not found. Session ID: {session_id}'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Use cleaned data if available, otherwise use original data
        if 'clean_df' in sessions[session_id]:
            export_df = sessions[session_id]['clean_df']
            print("Using cleaned data for Power BI export")
        elif 'df' in sessions[session_id]:
            export_df = sessions[session_id]['df']
            print("Using original data for Power BI export (not cleaned yet)")
        else:
            error_msg = 'No dataset loaded. Please upload a file first.'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        charts = sessions[session_id].get('charts', [])
        filename = sessions[session_id].get('filename', 'dataset')
        base_name = os.path.splitext(filename)[0]
        
        powerbi_bytes = export_powerbi_bundle(export_df, figs=charts)
        
        return send_file(
            io.BytesIO(powerbi_bytes),
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Power BI export error: {error_details}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/pdf', methods=['GET'])
@check_session
@check_rate_limit
def export_pdf():
    """Export PDF report"""
    try:
        session_id = get_session_id()
        print(f"PDF export request - Session ID: {session_id}")
        print(f"Available sessions: {list(sessions.keys())}")
        
        if session_id not in sessions:
            error_msg = f'Session not found. Session ID: {session_id}'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Use cleaned data if available, otherwise use original data
        if 'clean_df' in sessions[session_id]:
            export_df = sessions[session_id]['clean_df']
            cleaning_report = sessions[session_id].get('cleaning_report', {})
            print("Using cleaned data for PDF export")
        elif 'df' in sessions[session_id]:
            export_df = sessions[session_id]['df']
            cleaning_report = {}  # No cleaning report if data wasn't cleaned
            print("Using original data for PDF export (not cleaned yet)")
        else:
            error_msg = 'No dataset loaded. Please upload a file first.'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        overview = compute_overview(export_df)
        insights_text = sessions[session_id].get('insights', '')
        filename = sessions[session_id].get('filename', 'dataset')
        base_name = os.path.splitext(filename)[0]
        charts = sessions[session_id].get('charts', [])
        
        pdf_bytes = export_pdf_report(base_name, overview, cleaning_report, insights_text, figs=charts)
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF export error: {error_details}")
        return jsonify({'error': str(e)}), 500


# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler to prevent server crashes"""
    import traceback
    error_details = traceback.format_exc()
    print(f"Unhandled exception: {error_details}")
    return jsonify({
        'error': str(e),
        'type': type(e).__name__
    }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Get port from environment variable (for production) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print("=" * 50)
    print("Starting Flask Backend API Server...")
    print(f"Server will run on: http://0.0.0.0:{port}")
    print(f"API endpoints available at: http://0.0.0.0:{port}/api")
    print(f"Debug mode: {debug_mode}")
    print("=" * 50)
    app.run(debug=debug_mode, port=port, host='0.0.0.0')

