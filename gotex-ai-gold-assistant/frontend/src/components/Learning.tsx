import React, { useState, useEffect } from 'react';

interface LearningStats {
  total_files_processed: number;
  concepts_by_frequency: Record<string, number>;
  patterns_by_frequency: Record<string, number>;
  indicators_by_frequency: Record<string, number>;
  learning_timeline: Array<{
    date: string;
    file: string;
    type: string;
  }>;
  content_types: Record<string, number>;
}

const Learning: React.FC = () => {
  const [stats, setStats] = useState<LearningStats | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<string>('stats');

  useEffect(() => {
    fetchLearningStats();
  }, []);

  const fetchLearningStats = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/learning/stats/');
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch learning statistics');
    } finally {
      setLoading(false);
    }
  };

  const renderConceptsTable = () => {
    if (!stats || Object.keys(stats.concepts_by_frequency).length === 0) {
      return <p className="text-gray-500 italic">No concepts learned yet.</p>;
    }

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Concept
              </th>
              <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Frequency
              </th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(stats.concepts_by_frequency).map(([concept, frequency], index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="py-2 px-4 border-b border-gray-200 text-sm">{concept}</td>
                <td className="py-2 px-4 border-b border-gray-200 text-sm">{frequency}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderPatternsTable = () => {
    if (!stats || Object.keys(stats.patterns_by_frequency).length === 0) {
      return <p className="text-gray-500 italic">No patterns learned yet.</p>;
    }

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Pattern
              </th>
              <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Frequency
              </th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(stats.patterns_by_frequency).map(([pattern, frequency], index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="py-2 px-4 border-b border-gray-200 text-sm">{pattern}</td>
                <td className="py-2 px-4 border-b border-gray-200 text-sm">{frequency}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderIndicatorsTable = () => {
    if (!stats || Object.keys(stats.indicators_by_frequency).length === 0) {
      return <p className="text-gray-500 italic">No indicators learned yet.</p>;
    }

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Indicator
              </th>
              <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Frequency
              </th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(stats.indicators_by_frequency).map(([indicator, frequency], index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="py-2 px-4 border-b border-gray-200 text-sm">{indicator}</td>
                <td className="py-2 px-4 border-b border-gray-200 text-sm">{frequency}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderTimelineTable = () => {
    if (!stats || stats.learning_timeline.length === 0) {
      return <p className="text-gray-500 italic">No learning timeline data yet.</p>;
    }

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Date
              </th>
              <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                File
              </th>
              <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Type
              </th>
            </tr>
          </thead>
          <tbody>
            {stats.learning_timeline.map((entry, index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="py-2 px-4 border-b border-gray-200 text-sm">{entry.date}</td>
                <td className="py-2 px-4 border-b border-gray-200 text-sm">{entry.file}</td>
                <td className="py-2 px-4 border-b border-gray-200 text-sm">{entry.type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderCharts = () => {
    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-medium mb-2">Concepts Chart</h3>
          <div className="border rounded p-4 bg-white">
            <img 
              src="http://localhost:8000/learning/charts/concepts/" 
              alt="Concepts Chart" 
              className="max-w-full h-auto"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = 'https://via.placeholder.com/800x400?text=No+Chart+Available';
              }}
            />
          </div>
        </div>
        <div>
          <h3 className="text-lg font-medium mb-2">Learning Timeline Chart</h3>
          <div className="border rounded p-4 bg-white">
            <img 
              src="http://localhost:8000/learning/charts/timeline/" 
              alt="Timeline Chart" 
              className="max-w-full h-auto"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = 'https://via.placeholder.com/800x400?text=No+Chart+Available';
              }}
            />
          </div>
        </div>
      </div>
    );
  };

  const renderContent = () => {
    if (loading) {
      return <div className="text-center py-8">Loading learning data...</div>;
    }

    if (error) {
      return (
        <div className="bg-red-100 text-red-700 p-4 rounded">
          <p><strong>Error:</strong> {error}</p>
          <button 
            onClick={fetchLearningStats}
            className="mt-2 bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
          >
            Try Again
          </button>
        </div>
      );
    }

    if (!stats) {
      return <div className="text-center py-8">No learning data available.</div>;
    }

    switch (activeTab) {
      case 'stats':
        return (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded">
              <h3 className="text-lg font-medium mb-2">Learning Summary</h3>
              <p><strong>Total Files Processed:</strong> {stats.total_files_processed}</p>
              <p><strong>Unique Concepts Learned:</strong> {Object.keys(stats.concepts_by_frequency).length}</p>
              <p><strong>Unique Patterns Identified:</strong> {Object.keys(stats.patterns_by_frequency).length}</p>
              <p><strong>Unique Indicators Recognized:</strong> {Object.keys(stats.indicators_by_frequency).length}</p>
            </div>
            
            <div>
              <h3 className="text-lg font-medium mb-2">Content Types</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white">
                  <thead>
                    <tr>
                      <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                        Content Type
                      </th>
                      <th className="py-2 px-4 border-b border-gray-200 bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                        Count
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(stats.content_types).map(([type, count], index) => (
                      <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="py-2 px-4 border-b border-gray-200 text-sm">{type}</td>
                        <td className="py-2 px-4 border-b border-gray-200 text-sm">{count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        );
      case 'concepts':
        return (
          <div>
            <h3 className="text-lg font-medium mb-2">Trading Concepts Learned</h3>
            {renderConceptsTable()}
          </div>
        );
      case 'patterns':
        return (
          <div>
            <h3 className="text-lg font-medium mb-2">Trading Patterns Identified</h3>
            {renderPatternsTable()}
          </div>
        );
      case 'indicators':
        return (
          <div>
            <h3 className="text-lg font-medium mb-2">Trading Indicators Recognized</h3>
            {renderIndicatorsTable()}
          </div>
        );
      case 'timeline':
        return (
          <div>
            <h3 className="text-lg font-medium mb-2">Learning Timeline</h3>
            {renderTimelineTable()}
          </div>
        );
      case 'charts':
        return renderCharts();
      default:
        return <div>Select a tab to view learning data</div>;
    }
  };

  return (
    <div className="bg-white rounded shadow p-4 w-full max-w-4xl">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Learning Engine</h2>
        <button 
          onClick={fetchLearningStats}
          className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
        >
          Refresh Data
        </button>
      </div>
      
      <div className="border-b border-gray-200 mb-4">
        <nav className="-mb-px flex space-x-4">
          <button
            className={`py-2 px-3 border-b-2 text-sm font-medium ${activeTab === 'stats' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
            onClick={() => setActiveTab('stats')}
          >
            Summary
          </button>
          <button
            className={`py-2 px-3 border-b-2 text-sm font-medium ${activeTab === 'concepts' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
            onClick={() => setActiveTab('concepts')}
          >
            Concepts
          </button>
          <button
            className={`py-2 px-3 border-b-2 text-sm font-medium ${activeTab === 'patterns' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
            onClick={() => setActiveTab('patterns')}
          >
            Patterns
          </button>
          <button
            className={`py-2 px-3 border-b-2 text-sm font-medium ${activeTab === 'indicators' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
            onClick={() => setActiveTab('indicators')}
          >
            Indicators
          </button>
          <button
            className={`py-2 px-3 border-b-2 text-sm font-medium ${activeTab === 'timeline' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
            onClick={() => setActiveTab('timeline')}
          >
            Timeline
          </button>
          <button
            className={`py-2 px-3 border-b-2 text-sm font-medium ${activeTab === 'charts' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
            onClick={() => setActiveTab('charts')}
          >
            Charts
          </button>
        </nav>
      </div>
      
      {renderContent()}
    </div>
  );
};

export default Learning;