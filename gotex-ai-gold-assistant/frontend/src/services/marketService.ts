interface CandleData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface MarketData {
  symbol: string;
  current_price: number;
  data: CandleData[];
  last_update: string;
}

interface MarketStatus {
  status: string;
  market_open: boolean;
  last_update: string;
}

class MarketService {
  private baseUrl = 'http://localhost:8000';

  async getLiveData(symbol: string = 'XAUUSD'): Promise<MarketData> {
    const response = await fetch(`${this.baseUrl}/market/live?symbol=${symbol}`);
    if (!response.ok) {
      throw new Error('Failed to fetch market data');
    }
    return response.json();
  }

  async getHistoricalData(symbol: string = 'XAUUSD', period: string = '1d', interval: string = '1h'): Promise<CandleData[]> {
    const response = await fetch(`${this.baseUrl}/market/history?symbol=${symbol}&period=${period}&interval=${interval}`);
    if (!response.ok) {
      throw new Error('Failed to fetch historical data');
    }
    const data = await response.json();
    return data.data || [];
  }

  async getPredictions(symbol: string = 'XAUUSD', numPredictions: number = 5): Promise<CandleData[]> {
    const response = await fetch(`${this.baseUrl}/market/predict?symbol=${symbol}&num_predictions=${numPredictions}`);
    if (!response.ok) {
      throw new Error('Failed to fetch predictions');
    }
    const data = await response.json();
    return data.predictions || [];
  }

  async getMarketStatus(): Promise<MarketStatus> {
    const response = await fetch(`${this.baseUrl}/market/status`);
    if (!response.ok) {
      throw new Error('Failed to fetch market status');
    }
    return response.json();
  }

  async trainModel(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/market/train`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to train model');
    }
    return response.json();
  }
}

export const marketService = new MarketService();
export type { CandleData, MarketData, MarketStatus };