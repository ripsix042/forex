import React, { useState, useEffect } from 'react';

interface QueryHistory {
  id: string;
  question: string;
  answer: string;
  timestamp: Date;
  sources?: string[];
}

interface QueryInterfaceProps {
  onQuery?: (result: any) => void;
}

const QueryInterface: React.FC<QueryInterfaceProps> = ({ onQuery }) => {
  const [query, setQuery] = useState<string>('');
  const [answer, setAnswer] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [queryHistory, setQueryHistory] = useState<QueryHistory[]>([]);
  const [showHistory, setShowHistory] = useState<boolean>(false);
  const [sources, setSources] = useState<string[]>([]);

  const suggestedQuestions = [
    "What are the current gold market trends?",
    "How does inflation affect gold prices?",
    "What are the best gold trading strategies?",
    "When is the best time to buy gold?",
    "How do central bank policies impact gold?",
    "What factors influence gold volatility?"
  ];

  useEffect(() => {
    loadQueryHistory();
  }, []);

  const loadQueryHistory = () => {
    const saved = localStorage.getItem('queryHistory');
    if (saved) {
      try {
        const parsed = JSON.parse(saved).map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }));
        setQueryHistory(parsed);
      } catch (error) {
        console.error('Error loading query history:', error);
      }
    }
  };

  const saveQueryHistory = (newQuery: QueryHistory) => {
    const updated = [newQuery, ...queryHistory].slice(0, 20); // Keep last 20 queries
    setQueryHistory(updated);
    localStorage.setItem('queryHistory', JSON.stringify(updated));
  };

  const handleQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setAnswer('');
    setSources([]);

    try {
      const response = await fetch('http://localhost:8000/query/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: query }),
      });

      const data = await response.json();

      if (response.ok) {
        setAnswer(data.answer);
        setSources(data.sources || []);
        
        // Save to history
        const newQuery: QueryHistory = {
          id: Date.now().toString(),
          question: query,
          answer: data.answer,
          timestamp: new Date(),
          sources: data.sources
        };
        saveQueryHistory(newQuery);
        
        onQuery?.(data);
      } else {
        setError(data.error || 'An error occurred while processing your question.');
      }
    } catch (error) {
      setError('Failed to connect to the server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setQuery(question);
  };

  const handleHistoryClick = (historyItem: QueryHistory) => {
    setQuery(historyItem.question);
    setAnswer(historyItem.answer);
    setSources(historyItem.sources || []);
    setShowHistory(false);
  };

  const clearHistory = () => {
    setQueryHistory([]);
    localStorage.removeItem('queryHistory');
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      {/* Query Input Section */}
      <div style={{ marginBottom: '30px' }}>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleQuery()}
            placeholder="Ask me anything about gold trading..."
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '2px solid #e1e5e9',
              borderRadius: '8px',
              fontSize: '16px',
              outline: 'none',
              transition: 'border-color 0.2s',
            }}
            onFocus={(e) => e.target.style.borderColor = '#007bff'}
            onBlur={(e) => e.target.style.borderColor = '#e1e5e9'}
          />
          <button
            onClick={handleQuery}
            disabled={loading || !query.trim()}
            style={{
              padding: '12px 24px',
              backgroundColor: loading ? '#6c757d' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s',
              minWidth: '100px'
            }}
          >
            {loading ? 'Asking...' : 'Ask'}
          </button>
        </div>

        {/* History Toggle */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={() => setShowHistory(!showHistory)}
            style={{
              padding: '8px 16px',
              backgroundColor: 'transparent',
              color: '#007bff',
              border: '1px solid #007bff',
              borderRadius: '6px',
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            {showHistory ? 'Hide History' : `Show History (${queryHistory.length})`}
          </button>
          {queryHistory.length > 0 && (
            <button
              onClick={clearHistory}
              style={{
                padding: '8px 16px',
                backgroundColor: 'transparent',
                color: '#dc3545',
                border: '1px solid #dc3545',
                borderRadius: '6px',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Clear History
            </button>
          )}
        </div>
      </div>

      {/* Query History */}
      {showHistory && queryHistory.length > 0 && (
        <div style={{
          marginBottom: '30px',
          border: '1px solid #e1e5e9',
          borderRadius: '8px',
          maxHeight: '300px',
          overflowY: 'auto'
        }}>
          <div style={{
            padding: '12px 16px',
            backgroundColor: '#f8f9fa',
            borderBottom: '1px solid #e1e5e9',
            fontWeight: 'bold'
          }}>
            Query History
          </div>
          {queryHistory.map((item) => (
            <div
              key={item.id}
              onClick={() => handleHistoryClick(item)}
              style={{
                padding: '12px 16px',
                borderBottom: '1px solid #f1f3f4',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f8f9fa'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              <div style={{ fontWeight: '500', marginBottom: '4px' }}>
                {item.question}
              </div>
              <div style={{ fontSize: '12px', color: '#6c757d' }}>
                {formatTimestamp(item.timestamp)}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Suggested Questions */}
      {!answer && !loading && (
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ marginBottom: '15px', color: '#495057' }}>Suggested Questions:</h3>
          <div style={{ display: 'grid', gap: '10px', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleSuggestedQuestion(question)}
                style={{
                  padding: '12px 16px',
                  backgroundColor: '#f8f9fa',
                  border: '1px solid #e1e5e9',
                  borderRadius: '8px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  fontSize: '14px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#e9ecef';
                  e.currentTarget.style.borderColor = '#007bff';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#f8f9fa';
                  e.currentTarget.style.borderColor = '#e1e5e9';
                }}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div style={{
          padding: '30px',
          textAlign: 'center',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid #007bff',
            borderTop: '4px solid transparent',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 15px'
          }}></div>
          <p style={{ margin: 0, color: '#6c757d' }}>Analyzing your question...</p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div style={{
          padding: '15px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Answer Display */}
      {answer && (
        <div style={{
          padding: '20px',
          backgroundColor: '#d4edda',
          color: '#155724',
          border: '1px solid #c3e6cb',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '15px' }}>Answer:</h3>
          <div style={{ lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
            {answer}
          </div>
          
          {/* Sources */}
          {sources.length > 0 && (
            <div style={{ marginTop: '20px', paddingTop: '15px', borderTop: '1px solid #c3e6cb' }}>
              <h4 style={{ marginBottom: '10px', fontSize: '14px', color: '#0f5132' }}>Sources:</h4>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                {sources.map((source, index) => (
                  <li key={index} style={{ marginBottom: '5px', fontSize: '13px' }}>
                    {source}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* CSS for spinner animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default QueryInterface;