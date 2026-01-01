import React, { useState } from 'react';

const Exports = ({ onExport, fileData }) => {
  const [exportOptions, setExportOptions] = useState({
    excel: true,
    powerbi: true,
    pdf: true
  });

  const handleExport = (type) => {
    onExport(type);
  };

  return (
    <div className="section-card">
      <h2>📤 Export Reports</h2>
      <p style={{ color: '#666', marginBottom: '1rem' }}>
        Download your analysis in various formats
      </p>

      <div className="grid grid-3" style={{ marginBottom: '1.5rem' }}>
        <div className="checkbox-item">
          <input
            type="checkbox"
            id="excel"
            checked={exportOptions.excel}
            onChange={() => setExportOptions(prev => ({ ...prev, excel: !prev.excel }))}
          />
          <label htmlFor="excel">📊 Excel Report (cleaned data + summary + charts)</label>
        </div>
        <div className="checkbox-item">
          <input
            type="checkbox"
            id="powerbi"
            checked={exportOptions.powerbi}
            onChange={() => setExportOptions(prev => ({ ...prev, powerbi: !prev.powerbi }))}
          />
          <label htmlFor="powerbi">🔗 Power BI Bundle (CSV + charts ZIP)</label>
        </div>
        <div className="checkbox-item">
          <input
            type="checkbox"
            id="pdf"
            checked={exportOptions.pdf}
            onChange={() => setExportOptions(prev => ({ ...prev, pdf: !prev.pdf }))}
          />
          <label htmlFor="pdf">📄 PDF Report (professional report with charts)</label>
        </div>
      </div>

      <div className="grid grid-3">
        {exportOptions.excel && (
          <button
            className="btn"
            onClick={() => handleExport('excel')}
            style={{ width: '100%' }}
          >
            📊 Download Excel
          </button>
        )}
        {exportOptions.powerbi && (
          <button
            className="btn"
            onClick={() => handleExport('powerbi')}
            style={{ width: '100%' }}
          >
            🔗 Download Power BI ZIP
          </button>
        )}
        {exportOptions.pdf && (
          <button
            className="btn"
            onClick={() => handleExport('pdf')}
            style={{ width: '100%' }}
          >
            📄 Download PDF
          </button>
        )}
      </div>

      {fileData && (
        <div className="success-box" style={{ marginTop: '2rem' }}>
          <h3>🎉 Analysis Complete!</h3>
          <p>Your dataset has been successfully analyzed. All sections are now available above.</p>
        </div>
      )}
    </div>
  );
};

export default Exports;

