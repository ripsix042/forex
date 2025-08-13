import React, { useEffect, useRef, memo, useState, useCallback } from 'react';
import { marketService } from '../services/marketService';

interface TradingChartProps {
  symbol?: string;
}

function TradingChart({ symbol = 'XAUUSD' }: TradingChartProps) {
  const container = useRef<HTMLDivElement>(null);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [marketStatus, setMarketStatus] = useState<string>('Unknown');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load market status and current price
  const loadMarketData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const [status, liveData] = await Promise.all([
        marketService.getMarketStatus(),
        marketService.getLiveData(symbol)
      ]);
      
      setMarketStatus(status.status || 'Unknown');
      setCurrentPrice(liveData.current_price || 0);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to load market data:', err);
      setError('Failed to load market data');
    } finally {
      setIsLoading(false);
    }
  }, [symbol]);

  // Initialize TradingView widget
  useEffect(() => {
    if (!container.current) return;

    // Clear any existing content
    container.current.innerHTML = '';

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = JSON.stringify({
      "allow_symbol_change": true,
      "calendar": false,
      "details": false,
      "hide_side_toolbar": false,
      "hide_top_toolbar": false,
      "hide_legend": false,
      "hide_volume": false,
      "hotlist": false,
      "interval": "5",
      "locale": "en",
      "save_image": true,
      "style": "1",
      "symbol": `OANDA:${symbol}`,
      "theme": "dark",
      "timezone": "Etc/UTC",
      "backgroundColor": "#0F0F0F",
      "gridColor": "rgba(242, 242, 242, 0.06)",
      "watchlist": [],
      "withdateranges": true,
      "compareSymbols": [],
      "studies": [],
      "autosize": true,
      "width": "100%",
      "height": "100%"
    });

    const widgetContainer = document.createElement('div');
    widgetContainer.className = 'tradingview-widget-container__widget';
    widgetContainer.style.height = 'calc(100% - 32px)';
    widgetContainer.style.width = '100%';
    
    const copyrightContainer = document.createElement('div');
    copyrightContainer.className = 'tradingview-widget-copyright';
    copyrightContainer.innerHTML = `<a href="https://www.tradingview.com/symbols/OANDA-${symbol}/?exchange=OANDA" rel="noopener nofollow" target="_blank"><span class="blue-text">${symbol} chart by TradingView</span></a>`;
    
    container.current.appendChild(widgetContainer);
    container.current.appendChild(copyrightContainer);
    widgetContainer.appendChild(script);

    // Load market data
    loadMarketData();
  }, [symbol, loadMarketData]);

  // Auto-refresh market data every 30 seconds
  useEffect(() => {
    const interval = setInterval(loadMarketData, 30000);
    return () => clearInterval(interval);
  }, [loadMarketData]);

  return (
    <div style={{ width: '100%', padding: '20px' }}>
      {/* Market Info Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        padding: '15px',
        backgroundColor: '#2a2a2a',
        borderRadius: '8px',
        color: 'white'
      }}>
        <div>
          <h3 style={{ margin: 0, color: '#ffaa00' }}>{symbol} Live Chart</h3>
          <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#ccc' }}>
            {currentPrice > 0 && (
              <span>
                Current Price: <span style={{ color: '#00ff88', fontWeight: 'bold' }}>
                  ${currentPrice.toFixed(2)}
                </span>
              </span>
            )}
            {lastUpdate && (
              <span style={{ marginLeft: '20px' }}>Last Update: {lastUpdate}</span>
            )}
            <span style={{ marginLeft: '20px' }}>Market: {marketStatus}</span>
          </p>
        </div>
        
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={loadMarketData}
            disabled={isLoading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.6 : 1,
              transition: 'all 0.2s'
            }}
          >
            {isLoading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div style={{
          padding: '10px',
          backgroundColor: '#dc3545',
          color: 'white',
          borderRadius: '4px',
          marginBottom: '20px',
          border: '1px solid #c82333'
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* TradingView Chart Container */}
      <div 
        className="tradingview-widget-container" 
        ref={container} 
        style={{ 
          height: "600px", 
          width: "100%",
          backgroundColor: '#0F0F0F',
          borderRadius: '8px',
          border: '1px solid #333'
        }}
      >
        {/* TradingView widget will be inserted here */}
      </div>

      {/* Additional CSS for TradingView styling */}
      <style>{`
        .tradingview-widget-copyright {
          font-size: 13px !important;
          line-height: 32px;
          text-align: center;
          vertical-align: middle;
          font-family: -apple-system, BlinkMacSystemFont, 'Trebuchet MS', Roboto, Ubuntu, sans-serif;
          color: #9db2bd !important;
        }
        .tradingview-widget-copyright .blue-text {
          color: #2962FF !important;
          text-decoration: none;
        }
        .tradingview-widget-copyright a {
          text-decoration: none !important;
          color: #9db2bd !important;
        }
        .tradingview-widget-copyright a:visited {
          color: #9db2bd !important;
        }
        .tradingview-widget-copyright a:hover .blue-text {
          color: #1E53E5 !important;
        }
        .tradingview-widget-copyright a:active .blue-text {
          color: #1848CC !important;
        }
        .tradingview-widget-copyright a:visited .blue-text {
          color: #2962FF !important;
        }
      `}</style>
    </div>
  );
}

export default memo(TradingChart);