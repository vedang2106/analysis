import React, { useState } from 'react';

const DataCleaning = ({ onClean, cleanedData, cleaningReport, loading }) => {
  const [expanded, setExpanded] = useState({});

  const toggleExpanded = (key) => {
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="section-card">
      <h2>🧹 Automated Cleaning</h2>
      
      {!cleanedData ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <button className="btn" onClick={onClean} disabled={loading}>
            {loading ? '🔄 Cleaning...' : '🧹 Clean Data'}
          </button>
        </div>
      ) : (
        <>
          <div className="success-box">
            ✅ Data cleaning completed successfully!
          </div>

          <div className="expander">
            <div className="expander-header" onClick={() => toggleExpanded('report')}>
              <span>📋 Cleaning Report</span>
              <span>{expanded.report ? '▼' : '▶'}</span>
            </div>
            {expanded.report && (
              <div className="expander-content open">
                <div style={{ padding: '1rem', background: '#f8f9ff', borderRadius: '8px' }}>
                  <p><strong>Rows before:</strong> {cleaningReport?.rows_before?.toLocaleString()}</p>
                  <p><strong>Rows after:</strong> {cleaningReport?.rows_after?.toLocaleString()}</p>
                  <p><strong>Duplicates removed:</strong> {cleaningReport?.duplicates_removed?.toLocaleString()}</p>
                  
                  {cleaningReport?.imputations && Object.keys(cleaningReport.imputations).length > 0 && (
                    <div style={{ marginTop: '1rem' }}>
                      <strong>Imputations:</strong>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        {Object.entries(cleaningReport.imputations).map(([col, desc]) => (
                          <li key={col}><strong>{col}:</strong> {desc}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {cleaningReport?.inferred_types && Object.keys(cleaningReport.inferred_types).length > 0 && (
                    <div style={{ marginTop: '1rem' }}>
                      <strong>Inferred Types:</strong>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        {Object.entries(cleaningReport.inferred_types).map(([col, type]) => (
                          <li key={col}><strong>{col}:</strong> {type}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="expander">
            <div className="expander-header" onClick={() => toggleExpanded('preview')}>
              <span>👀 Preview of Cleaned Data (First 50 rows)</span>
              <span>{expanded.preview ? '▼' : '▶'}</span>
            </div>
            {expanded.preview && cleanedData.preview && (
              <div className="expander-content open">
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        {Object.keys(cleanedData.preview[0] || {}).map(col => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {cleanedData.preview.slice(0, 50).map((row, idx) => (
                        <tr key={idx}>
                          {Object.values(row).map((val, colIdx) => (
                            <td key={colIdx}>{String(val)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default DataCleaning;

