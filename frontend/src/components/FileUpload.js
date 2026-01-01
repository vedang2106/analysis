import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const FileUpload = ({ onUpload, disabled }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json']
    },
    maxSize: 200 * 1024 * 1024, // 200MB
    disabled
  });

  return (
    <div className="section-card">
      <h2>📁 Upload Dataset</h2>
      <div
        {...getRootProps()}
        className={`upload-area ${isDragActive ? 'dragover' : ''}`}
      >
        <input {...getInputProps()} />
        <h4 style={{ margin: '0 0 1rem 0', color: '#667eea', fontSize: '1.2rem' }}>
          📁 Upload Dataset
        </h4>
        {isDragActive ? (
          <p style={{ margin: 0, color: '#555', fontWeight: 500 }}>
            Drop the file here...
          </p>
        ) : (
          <>
            <p style={{ margin: '0 0 0.5rem 0', color: '#555', fontWeight: 500 }}>
              Drag and drop or browse to upload
            </p>
            <p style={{ fontSize: '0.85rem', color: '#777', margin: 0 }}>
              Limit: 200MB • Formats: CSV, XLSX, XLS, JSON
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default FileUpload;

