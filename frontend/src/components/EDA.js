import React, { useState } from 'react';

const EDA = ({ onGenerate, charts, loading }) => {
  const [chartSelections, setChartSelections] = useState({
    basic_plots: true,
    scatter_plots: true,
    time_series: true,
    correlation: true,
    categorical: true,
    all_plots: false
  });

  const handleCheckboxChange = (key) => {
    setChartSelections(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleGenerate = () => {
    onGenerate(chartSelections);
  };

  return (
    <div className="section-card">
      <h2>📈 Exploratory Data Analysis</h2>
      
      <div style={{ marginBottom: '1.5rem' }}>
        <p style={{ marginBottom: '1rem' }}>🎯 Choose which types of charts to generate:</p>
        
        <div className="grid grid-3">
          <div className="checkbox-group">
            <div className="checkbox-item">
              <input
                type="checkbox"
                id="basic_plots"
                checked={chartSelections.basic_plots}
                onChange={() => handleCheckboxChange('basic_plots')}
              />
              <label htmlFor="basic_plots">📊 Basic Plots</label>
            </div>
            <div className="checkbox-item">
              <input
                type="checkbox"
                id="scatter_plots"
                checked={chartSelections.scatter_plots}
                onChange={() => handleCheckboxChange('scatter_plots')}
              />
              <label htmlFor="scatter_plots">🔍 Scatter Plots</label>
            </div>
          </div>
          
          <div className="checkbox-group">
            <div className="checkbox-item">
              <input
                type="checkbox"
                id="time_series"
                checked={chartSelections.time_series}
                onChange={() => handleCheckboxChange('time_series')}
              />
              <label htmlFor="time_series">⏰ Time Series</label>
            </div>
            <div className="checkbox-item">
              <input
                type="checkbox"
                id="correlation"
                checked={chartSelections.correlation}
                onChange={() => handleCheckboxChange('correlation')}
              />
              <label htmlFor="correlation">🔗 Correlation</label>
            </div>
          </div>
          
          <div className="checkbox-group">
            <div className="checkbox-item">
              <input
                type="checkbox"
                id="categorical"
                checked={chartSelections.categorical}
                onChange={() => handleCheckboxChange('categorical')}
              />
              <label htmlFor="categorical">📋 Categorical</label>
            </div>
            <div className="checkbox-item">
              <input
                type="checkbox"
                id="all_plots"
                checked={chartSelections.all_plots}
                onChange={() => handleCheckboxChange('all_plots')}
              />
              <label htmlFor="all_plots">🎨 All Plots</label>
            </div>
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
        <button className="btn" onClick={handleGenerate} disabled={loading}>
          {loading ? '🔄 Generating charts...' : '📊 Generate Charts'}
        </button>
      </div>

      {charts.length > 0 && (
        <>
          <div className="info-box" style={{ marginBottom: '1.5rem' }}>
            ✅ Generated {charts.length} charts successfully!
          </div>
          
          <div className="grid grid-2">
            {charts.map((chart, idx) => (
              <div key={idx} className="chart-container">
                <h4 style={{ marginBottom: '0.5rem', color: '#667eea' }}>{chart.title}</h4>
                <img src={chart.image} alt={chart.title} />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default EDA;

