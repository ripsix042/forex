import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import Learning from "./components/Learning";
import "./App.css";

const App: React.FC = () => {
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleQuery = async () => {
    setLoading(true);
    setError("");
    setAnswer("");
    try {
      const formData = new FormData();
      formData.append("question", query);
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Network response was not ok");
      const data = await res.json();
      setAnswer(data.answer);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const [activeSection, setActiveSection] = useState<'upload' | 'query' | 'learning'>('upload');

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="text-white py-5 shadow">
        <div className="container mx-auto px-4">
          <h1 className="text-2xl font-bold text-center">
            Gotex – The AI Gold Trading Assistant
          </h1>
          <p className="text-center text-blue-100 mt-1">Your intelligent companion for gold trading insights</p>
        </div>
      </header>
      
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-center mb-6">
          <nav className="flex space-x-4">
            <button
              onClick={() => setActiveSection('upload')}
              className={`px-4 py-2 rounded-md ${activeSection === 'upload' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
            >
              Upload Files
            </button>
            <button
              onClick={() => setActiveSection('query')}
              className={`px-4 py-2 rounded-md ${activeSection === 'query' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
            >
              Ask Questions
            </button>
            <button
              onClick={() => setActiveSection('learning')}
              className={`px-4 py-2 rounded-md ${activeSection === 'learning' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
            >
              Learning Engine
            </button>
          </nav>
        </div>
      </div>
      
      <main className="flex flex-col items-center justify-center mt-2 w-full px-4 responsive-container">
        {activeSection === 'upload' && (
          <>
            <FileUpload onUpload={setUploadResult} />
            {uploadResult && (
              <div className="mt-6 w-full max-w-xl bg-white rounded shadow p-4">
                <h2 className="text-lg font-semibold mb-2">Upload Result</h2>
                <pre className="bg-gray-100 p-2 rounded">
                  {JSON.stringify(uploadResult, null, 2)}
                </pre>
              </div>
            )}
          </>
        )}
        
        {activeSection === 'query' && (
          <div className="w-full max-w-xl bg-white rounded shadow p-4">
            <h2 className="text-lg font-semibold mb-2">Ask Gotex</h2>
            <div className="mb-3">
              <p className="text-sm text-gray-600 mb-2">Ask questions about gold trading, such as prices, investment strategies, trading hours, ETFs, and more.</p>
              <div className="flex">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask a question about gold trading..."
                  className="flex-1 border rounded px-3 py-2 mr-2"
                  onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                />
                <button
                  onClick={handleQuery}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition duration-200"
                  disabled={loading}
                >
                  {loading ? "Asking..." : "Ask"}
                </button>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                <p>Try asking about: gold prices, investment strategies, trading hours, price factors, ETFs, physical gold, technical analysis, seasonal patterns</p>
              </div>
            </div>
            {error && (
              <div className="mt-4 bg-red-100 text-red-700 p-3 rounded">
                <strong>Error:</strong> {error}
              </div>
            )}
            {answer && (
              <div className="mt-4 bg-gray-100 p-4 rounded">
                <h3 className="font-medium mb-2">Answer:</h3>
                <p className="text-gray-800">{answer}</p>
              </div>
            )}
          </div>
        )}
        
        {activeSection === 'learning' && (
          <Learning />
        )}
      </main>
    </div>
  );
};

export default App;
