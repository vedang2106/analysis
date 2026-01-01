import React, { useState } from 'react';

const DataOverview = ({ fileData, overview, onGetOverview, loading }) => {
  const [expanded, setExpanded] = useState({});

  const toggleExpanded = (key) => {
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="section-card">
      <h2>🔍 Data Understanding</h2>
      
      {!overview ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <button className="btn" onClick={onGetOverview} disabled={loading}>
            {loading ? '🔄 Computing...' : '📊 Compute Data Overview'}
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-4" style={{ marginBottom: '1.5rem' }}>
            <div className="metric-card">
              <h3>📊 Rows</h3>
              <h2>{overview.num_rows?.toLocaleString() || 0}</h2>
            </div>
            <div className="metric-card">
              <h3>📋 Columns</h3>
              <h2>{overview.num_cols || 0}</h2>
            </div>
            <div className="metric-card">
              <h3>❌ Missing</h3>
              <h2>
                {Object.values(overview.missing_counts || {}).reduce((a, b) => a + b, 0).toLocaleString()}
              </h2>
            </div>
            <div className="metric-card">
              <h3>🔢 Numeric</h3>
              <h2>
                {Object.entries(overview.dtypes || {}).filter(([_, dtype]) => 
                  dtype.includes('int') || dtype.includes('float')
                ).length}
              </h2>
            </div>
          </div>

          <div className="expander">
            <div className="expander-header" onClick={() => toggleExpanded('dtypes')}>
              <span>📋 Data Types</span>
              <span>{expanded.dtypes ? '▼' : '▶'}</span>
            </div>
            {expanded.dtypes && (
              <div className="expander-content open">
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Column</th>
                        <th>Data Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(overview.dtypes || {}).map(([col, dtype]) => (
                        <tr key={col}>
                          <td>{col}</td>
                          <td>{dtype}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          <div className="expander">
            <div className="expander-header" onClick={() => toggleExpanded('missing')}>
              <span>❌ Missing Values</span>
              <span>{expanded.missing ? '▼' : '▶'}</span>
            </div>
            {expanded.missing && (
              <div className="expander-content open">
                {Object.values(overview.missing_counts || {}).reduce((a, b) => a + b, 0) > 0 ? (
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th>Column</th>
                          <th>Missing Count</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(overview.missing_counts || {})
                          .filter(([_, count]) => count > 0)
                          .map(([col, count]) => (
                            <tr key={col}>
                              <td>{col}</td>
                              <td>{count.toLocaleString()}</td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="success-box" style={{ margin: '1rem 0' }}>
                    🎉 No missing values found in the dataset!
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="expander">
            <div className="expander-header" onClick={() => toggleExpanded('stats')}>
              <span>📊 Summary Statistics</span>
              <span>{expanded.stats ? '▼' : '▶'}</span>
            </div>
            {expanded.stats && (
              <div className="expander-content open">
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Column</th>
                        {overview.summary_stats && Object.keys(overview.summary_stats).length > 0 && 
                          Object.keys(Object.values(overview.summary_stats)[0] || {}).map(stat => (
                            <th key={stat}>{stat}</th>
                          ))
                        }
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(overview.summary_stats || {}).map(([col, stats]) => (
                        <tr key={col}>
                          <td>{col}</td>
                          {Object.values(stats || {}).map((val, idx) => (
                            <td key={idx}>{typeof val === 'number' ? val.toFixed(2) : String(val)}</td>
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

export default DataOverview;

