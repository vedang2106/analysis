import React, { useState } from 'react';

const ChatWithData = ({ onAskQuestion, loading }) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [asking, setAsking] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setAsking(true);
    try {
      const result = await onAskQuestion(question);
      setAnswer(result);
    } catch (err) {
      setAnswer({ error: 'Failed to get answer' });
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="section-card">
      <h2>💬 Chat with Your Data</h2>
      <p style={{ color: '#666', marginBottom: '1rem' }}>
        Ask questions about your dataset in natural language
      </p>

      <form onSubmit={handleSubmit} style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., 'minimum age', 'top 5 names', 'sales in July'"
            style={{
              flex: 1,
              padding: '0.75rem',
              borderRadius: '8px',
              border: '1px solid #E0E3E7',
              fontSize: '1rem'
            }}
            disabled={asking || loading}
          />
          <button
            type="submit"
            className="btn"
            disabled={asking || loading || !question.trim()}
          >
            {asking ? '🤔 Analyzing...' : '🚀 Answer'}
          </button>
        </div>
      </form>

      {answer && (
        <div>
          {answer.error ? (
            <div className="error-box">
              ❌ {answer.error}
            </div>
          ) : (
            <>
              {answer.message && (
                <div className="info-box" style={{ marginBottom: '1rem' }}>
                  💡 <strong>Answer:</strong> {answer.message}
                </div>
              )}

              {answer.table && answer.table.length > 0 && (
                <div style={{ marginBottom: '1rem' }}>
                  <h4>📊 Results Table</h4>
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          {Object.keys(answer.table[0]).map(col => (
                            <th key={col}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {answer.table.map((row, idx) => (
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

              {answer.figure && (
                <div className="chart-container">
                  <img src={answer.figure} alt="Q&A Chart" />
                </div>
              )}
            </>
          )}
        </div>
      )}

      <div style={{ background: '#f0f2f6', padding: '1rem', borderRadius: '10px', marginTop: '1rem' }}>
        <h4>💡 Try asking about:</h4>
        <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1.5rem' }}>
          <li>Sales in July 2024</li>
          <li>Top 10 products</li>
          <li>Average price by category</li>
          <li>Monthly trends</li>
          <li>Count by region</li>
          <li>Minimum/maximum values</li>
          <li>Data quality and missing values</li>
        </ul>
      </div>
    </div>
  );
};

export default ChatWithData;

