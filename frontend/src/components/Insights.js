import React, { useState } from 'react';

const Insights = ({ insights, onGetInsights, loading }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="section-card">
      <h2>💡 Automated Insights</h2>
      
      {!insights ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <button className="btn" onClick={onGetInsights} disabled={loading}>
            {loading ? '🔍 Generating insights...' : '💡 Generate Insights'}
          </button>
        </div>
      ) : (
        <>
          <div className="success-box">
            ✅ Insights generated successfully!
          </div>

          <div style={{
            background: '#f8f9ff',
            padding: '1.5rem',
            borderRadius: '10px',
            borderLeft: '4px solid #667eea',
            marginBottom: '1rem'
          }}>
            <h4 style={{ marginBottom: '0.5rem' }}>🔍 Key Findings:</h4>
            <p style={{ fontSize: '1.1rem', margin: 0, whiteSpace: 'pre-wrap' }}>
              {insights}
            </p>
          </div>

          <div className="expander">
            <div className="expander-header" onClick={() => setExpanded(!expanded)}>
              <span>📋 Raw Insights Data</span>
              <span>{expanded ? '▼' : '▶'}</span>
            </div>
            {expanded && (
              <div className="expander-content open">
                <pre style={{
                  background: '#f5f5f5',
                  padding: '1rem',
                  borderRadius: '8px',
                  overflow: 'auto',
                  fontSize: '0.9rem'
                }}>
                  {insights}
                </pre>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Insights;

