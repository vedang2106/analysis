import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import FileUpload from './components/FileUpload';
import DataOverview from './components/DataOverview';
import DataCleaning from './components/DataCleaning';
import EDA from './components/EDA';
import ChatWithData from './components/ChatWithData';
import Insights from './components/Insights';
import Exports from './components/Exports';

// Use relative path for Vercel deployment, localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5000/api');

// Configure axios with timeout
axios.defaults.timeout = 300000; // 5 minutes for large file uploads
// Don't set Content-Type globally - set it per request for JSON, let browser handle FormData

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [fileData, setFileData] = useState(null);
  const [overview, setOverview] = useState(null);
  const [cleanedData, setCleanedData] = useState(null);
  const [cleaningReport, setCleaningReport] = useState(null);
  const [charts, setCharts] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Initialize session and check backend health
  useEffect(() => {
    const storedSessionId = localStorage.getItem('sessionId');
    if (storedSessionId) {
      setSessionId(storedSessionId);
    } else {
      const newSessionId = generateSessionId();
      setSessionId(newSessionId);
      localStorage.setItem('sessionId', newSessionId);
    }

    // Check if backend is running
    const checkBackendHealth = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 });
        if (response.data?.status === 'ok') {
          console.log('Backend server is running');
        }
      } catch (err) {
        console.warn('Backend health check failed:', err.message);
        setError(`⚠️ Cannot connect to backend server at ${API_BASE_URL}. Please ensure the Flask server is running on port 5000.`);
      }
    };

    checkBackendHealth();
  }, []);

  const generateSessionId = () => {
    return Array.from(crypto.getRandomValues(new Uint8Array(16)))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  };

  const apiRequest = async (method, endpoint, data = null, config = {}) => {
    try {
      setError(null);
      // Ensure we have a session ID
      const currentSessionId = sessionId || localStorage.getItem('sessionId') || generateSessionId();
      if (!sessionId && currentSessionId) {
        setSessionId(currentSessionId);
        localStorage.setItem('sessionId', currentSessionId);
      }
      
      const headers = {
        'X-Session-ID': currentSessionId,
        ...config.headers
      };
      
      // Set Content-Type for JSON requests, but not for FormData (browser will set it with boundary)
      if (data && !(data instanceof FormData) && method === 'POST') {
        headers['Content-Type'] = 'application/json';
      }
      
      console.log(`API Request: ${method} ${endpoint}`, { sessionId: currentSessionId });

      // Merge timeout into config
      const requestConfig = {
        ...config,
        headers,
        timeout: config.timeout || 300000 // 5 minutes default
      };

      let response;
      const fullUrl = `${API_BASE_URL}${endpoint}`;
      console.log(`Making ${method} request to: ${fullUrl}`);
      
      if (method === 'GET') {
        response = await axios.get(fullUrl, requestConfig);
      } else if (method === 'POST') {
        response = await axios.post(fullUrl, data, requestConfig);
      }

      // Update session ID from response header if available
      const responseSessionId = response.headers['x-session-id'] || response.headers['X-Session-ID'];
      if (responseSessionId && responseSessionId !== currentSessionId) {
        console.log('Updating session ID from response header:', responseSessionId);
        setSessionId(responseSessionId);
        localStorage.setItem('sessionId', responseSessionId);
      }
      
      // Also check response body for session_id
      if (response.data && response.data.session_id && response.data.session_id !== currentSessionId) {
        console.log('Updating session ID from response body:', response.data.session_id);
        setSessionId(response.data.session_id);
        localStorage.setItem('sessionId', response.data.session_id);
      }

      return response.data;
    } catch (err) {
      console.error('API Request Error:', err);
      
      let errorMsg = 'An error occurred';
      
      // Check for network errors (connection refused, network error, connection reset)
      if (err.code === 'ECONNREFUSED' || 
          err.code === 'ERR_NETWORK' || 
          err.code === 'ERR_CONNECTION_RESET' ||
          err.message?.includes('Network Error') ||
          err.message?.includes('Connection reset') ||
          (err.request && !err.response)) {
        errorMsg = `Cannot connect to backend server at ${API_BASE_URL}. Please ensure the Flask server is running on port 5000.`;
      } else if (err.code === 'ETIMEDOUT' || err.message?.includes('timeout')) {
        errorMsg = 'Request timed out. The server is taking too long to respond. Please try again or check if the server is still running.';
      } else if (err.response) {
        // Server responded with error status
        errorMsg = err.response.data?.error || err.response.data?.message || `Server error: ${err.response.status} ${err.response.statusText}`;
      } else if (err.request) {
        // Request was made but no response received
        errorMsg = 'No response from server. Please check if the backend server is running.';
      } else {
        // Something else happened
        errorMsg = err.message || 'An unexpected error occurred';
      }
      
      setError(errorMsg);
      throw err;
    }
  };

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);

      // For file uploads, use longer timeout and don't set Content-Type
      const data = await apiRequest('POST', '/upload', formData, {
        timeout: 600000, // 10 minutes for large file uploads
        headers: {} // Let browser set Content-Type with boundary
      });

      // Update session ID if returned from server
      if (data.session_id) {
        setSessionId(data.session_id);
        localStorage.setItem('sessionId', data.session_id);
        console.log('Updated session ID:', data.session_id);
      }

      setFileData(data);
      setOverview(null);
      setCleanedData(null);
      setCleaningReport(null);
      setCharts([]);
      setInsights(null);
    } catch (err) {
      // Error is already set by apiRequest
      console.error('Upload error:', err);
      console.error('Error details:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleGetOverview = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest('GET', '/overview');
      setOverview(data);
    } catch (err) {
      console.error('Overview error:', err);
      // Error message already set by apiRequest
    } finally {
      setLoading(false);
    }
  };

  const handleClean = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest('POST', '/clean');
      setCleanedData(data);
      setCleaningReport(data.cleaning_report);
    } catch (err) {
      console.error('Clean error:', err);
      // Error message already set by apiRequest
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateEDA = async (chartSelections) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest('POST', '/eda', { chart_selections: chartSelections });
      setCharts(data.charts || []);
    } catch (err) {
      console.error('EDA error:', err);
      // Error message already set by apiRequest
    } finally {
      setLoading(false);
    }
  };

  const handleGetInsights = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest('GET', '/insights');
      setInsights(data.insights);
    } catch (err) {
      console.error('Insights error:', err);
      // Error message already set by apiRequest
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (type) => {
    setLoading(true);
    setError(null);
    try {
      // Ensure we have a session ID
      const currentSessionId = sessionId || localStorage.getItem('sessionId') || generateSessionId();
      if (!sessionId && currentSessionId) {
        setSessionId(currentSessionId);
        localStorage.setItem('sessionId', currentSessionId);
      }

      console.log(`Export ${type} - Session ID: ${currentSessionId}`);
      
      const response = await axios.get(`${API_BASE_URL}/export/${type}`, {
        headers: { 'X-Session-ID': currentSessionId },
        responseType: 'blob',
        timeout: 300000, // 5 minutes
        validateStatus: function (status) {
          // Don't throw error for 4xx/5xx, handle it manually
          return status >= 200 && status < 500;
        }
      });

      // Check if response is an error (blob with error JSON)
      if (response.status >= 400) {
        // Try to read the error message from the blob
        const text = await response.data.text();
        let errorMsg = 'Export failed';
        try {
          const errorJson = JSON.parse(text);
          errorMsg = errorJson.error || errorMsg;
        } catch (e) {
          errorMsg = text || `Export failed with status ${response.status}`;
        }
        setError(errorMsg);
        console.error('Export error:', errorMsg);
        return;
      }

      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const contentDisposition = response.headers['content-disposition'];
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : `export_${type}_${Date.now()}.${type === 'powerbi' ? 'zip' : type}`;
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export error:', err);
      if (err.code === 'ECONNREFUSED' || err.message?.includes('Network Error')) {
        setError(`Cannot connect to backend server. Please ensure the Flask server is running on port 5000.`);
      } else if (err.code === 'ETIMEDOUT' || err.message?.includes('timeout')) {
        setError('Export request timed out. Please try again.');
      } else {
        const errorMsg = err.response?.data?.error || err.message || 'Export failed';
        setError(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <div className="main-header">
          <h1>📊 Data Analyst Automation Tool</h1>
          <p style={{ fontSize: '1.2rem', margin: '0.5rem 0' }}>
            Upload a dataset (CSV, Excel, JSON), auto-analyze, and export comprehensive reports
          </p>
        </div>

        {error && (
          <div className="error-box">
            <strong>⚠ Error:</strong> {error}
          </div>
        )}

        {loading && (
          <div className="loading-spinner"></div>
        )}

        <FileUpload onUpload={handleFileUpload} disabled={loading} />

        {fileData && (
          <>
            <div className="success-box">
              <h3>🎉 Dataset Loaded Successfully!</h3>
              <p>
                <strong>{fileData.filename}</strong> • Shape: {fileData.shape.rows.toLocaleString()} rows × {fileData.shape.cols} columns
              </p>
            </div>

            <DataOverview
              fileData={fileData}
              overview={overview}
              onGetOverview={handleGetOverview}
              loading={loading}
            />

            {overview && (
              <DataCleaning
                onClean={handleClean}
                cleanedData={cleanedData}
                cleaningReport={cleaningReport}
                loading={loading}
              />
            )}

            {overview && (
              <>
                {cleanedData && (
                  <EDA
                    onGenerate={handleGenerateEDA}
                    charts={charts}
                    loading={loading}
                  />
                )}

                <ChatWithData
                  onAskQuestion={async (question) => {
                    setLoading(true);
                    try {
                      const data = await apiRequest('POST', '/qa', { question });
                      return data;
                    } catch (err) {
                      console.error('QA error:', err);
                      const errorMsg = err.response?.data?.error || 'Failed to answer question';
                      return { error: errorMsg };
                    } finally {
                      setLoading(false);
                    }
                  }}
                  loading={loading}
                />

                <Insights
                  insights={insights}
                  onGetInsights={handleGetInsights}
                  loading={loading}
                />

                <Exports
                  onExport={handleExport}
                  fileData={fileData}
                />
              </>
            )}
          </>
        )}

        {!fileData && (
          <div className="info-box" style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            padding: '1.25rem 1.5rem',
            borderRadius: '16px',
            color: 'white',
            textAlign: 'center',
            marginBottom: '1.25rem'
          }}>
            <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '1.6rem' }}>🚀 Data Analyst Automation</h2>
            <p style={{ fontSize: '1rem', margin: 0, opacity: 0.9 }}>
              Upload a dataset to start fast, automated analysis
            </p>
          </div>
        )}

        <footer style={{ marginTop: '3rem', padding: '2rem', textAlign: 'center', color: '#666' }}>
          <p>Built with ❤ using Python, React, Flask, Pandas, and Matplotlib</p>
          <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
            Version 2.0 • Enterprise-Ready Data Analysis Platform
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;

