import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import QueryInterface from './components/QueryInterface';
import Learning from './components/Learning';
import TradingChart from './components/TradingChart';

function App() {
  const [activeTab, setActiveTab] = useState<'upload' | 'chart' | 'query' | 'learning'>('upload');

  const handleUpload = (result: any) => {
    console.log('Upload result:', result);
  };

  const handleQuery = (result: any) => {
    console.log('Query result:', result);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏆 GoTex AI Gold Assistant</h1>
        <p>Your intelligent companion for gold trading insights</p>
      </header>

      <nav style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '20px',
        margin: '20px 0',
        borderBottom: '1px solid #e1e5e9',
        paddingBottom: '10px'
      }}>
        <button
          onClick={() => setActiveTab('upload')}
          style={{
            padding: '10px 20px',
            backgroundColor: activeTab === 'upload' ? '#007bff' : 'transparent',
            color: activeTab === 'upload' ? 'white' : '#007bff',
            border: '2px solid #007bff',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
        >
          📁 Upload Files
        </button>
        <button
          onClick={() => setActiveTab('chart')}
          style={{
            padding: '10px 20px',
            backgroundColor: activeTab === 'chart' ? '#17a2b8' : 'transparent',
            color: activeTab === 'chart' ? 'white' : '#17a2b8',
            border: '2px solid #17a2b8',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
        >
          📈 Live Chart
        </button>
        <button
          onClick={() => setActiveTab('query')}
          style={{
            padding: '10px 20px',
            backgroundColor: activeTab === 'query' ? '#28a745' : 'transparent',
            color: activeTab === 'query' ? 'white' : '#28a745',
            border: '2px solid #28a745',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
        >
          💬 Ask Questions
        </button>
        <button
          onClick={() => setActiveTab('learning')}
          style={{
            padding: '10px 20px',
            backgroundColor: activeTab === 'learning' ? '#ffc107' : 'transparent',
            color: activeTab === 'learning' ? 'black' : '#ffc107',
            border: '2px solid #ffc107',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
        >
          📊 Learning Engine
        </button>
      </nav>

      <main style={{ padding: '20px', minHeight: '60vh' }}>
        {activeTab === 'upload' && (
          <div>
            <h2>📤 Upload Your Documents</h2>
            <p>Upload documents or YouTube videos to build your knowledge base</p>
            <FileUpload onUpload={handleUpload} />
          </div>
        )}

        {activeTab === 'chart' && (
          <div>
            <h2>📈 Live XAUUSD Chart</h2>
            <p>Real-time gold trading chart with AI predictions</p>
            <TradingChart symbol="XAUUSD" />
          </div>
        )}

        {activeTab === 'query' && (
          <div>
            <h2>🤖 AI Gold Trading Assistant</h2>
            <p>Ask me anything about gold trading, market trends, and investment strategies</p>
            <QueryInterface onQuery={handleQuery} />
          </div>
        )}

        {activeTab === 'learning' && (
          <div>
            <h2>📈 Learning Analytics</h2>
            <p>Track your learning progress and discover insights</p>
            <Learning />
          </div>
        )}
      </main>

      <footer style={{
        textAlign: 'center',
        padding: '20px',
        borderTop: '1px solid #e1e5e9',
        color: '#6c757d'
      }}>
        <p>© 2024 GoTex AI Gold Assistant - Powered by Advanced AI</p>
      </footer>
    </div>
  );
}

export default App;
