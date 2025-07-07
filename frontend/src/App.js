import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TradingDashboard = () => {
  const [liveTrade, setLiveTrade] = useState(null);
  const [tradeHistory, setTradeHistory] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedTrade, setSelectedTrade] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch live trade data
  const fetchLiveTrade = async () => {
    try {
      const response = await axios.get(`${API}/trade/live`);
      setLiveTrade(response.data);
    } catch (error) {
      console.error('Error fetching live trade:', error);
    }
  };

  // Fetch trade history
  const fetchTradeHistory = async () => {
    try {
      const response = await axios.get(`${API}/trade/history?limit=20`);
      setTradeHistory(response.data);
    } catch (error) {
      console.error('Error fetching trade history:', error);
    }
  };

  // Fetch trading metrics
  const fetchMetrics = async () => {
    try {
      const response = await axios.get(`${API}/metrics`);
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  // Fetch market data
  const fetchMarketData = async () => {
    try {
      const response = await axios.get(`${API}/market/data`);
      setMarketData(response.data);
    } catch (error) {
      console.error('Error fetching market data:', error);
    }
  };

  // Fetch portfolio
  const fetchPortfolio = async () => {
    try {
      const response = await axios.get(`${API}/portfolio`);
      setPortfolio(response.data);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    }
  };

  // Trigger new trade
  const triggerTrade = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/trade/trigger`);
      setLiveTrade(response.data);
      await fetchTradeHistory();
      await fetchMetrics();
      await fetchPortfolio();
    } catch (error) {
      console.error('Error triggering trade:', error);
      alert('Error triggering trade: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh data
  useEffect(() => {
    const fetchAllData = async () => {
      await Promise.all([
        fetchLiveTrade(),
        fetchTradeHistory(),
        fetchMetrics(),
        fetchMarketData(),
        fetchPortfolio()
      ]);
    };

    fetchAllData();

    if (autoRefresh) {
      const interval = setInterval(fetchAllData, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getActionColor = (action) => {
    switch (action) {
      case 'BUY': return 'text-green-500';
      case 'SELL': return 'text-red-500';
      case 'HOLD': return 'text-yellow-500';
      default: return 'text-gray-500';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-500';
    if (confidence >= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🤖 Autonomous Crypto Trading Agent
          </h1>
          <p className="text-gray-300">
            LLM-Powered Paper Trading with Real-time Analysis
          </p>
        </div>

        {/* Controls */}
        <div className="flex justify-center gap-4 mb-8">
          <button
            onClick={triggerTrade}
            disabled={loading}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {loading ? '⏳ Analyzing...' : '🧠 Trigger Trade Decision'}
          </button>
          
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
              autoRefresh 
                ? 'bg-green-500 hover:bg-green-600 text-white' 
                : 'bg-gray-500 hover:bg-gray-600 text-white'
            }`}
          >
            {autoRefresh ? '🔄 Auto-refresh ON' : '⏸️ Auto-refresh OFF'}
          </button>
        </div>

        {/* Metrics Dashboard */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-2">Total Trades</h3>
              <p className="text-3xl font-bold text-blue-400">{metrics.total_trades}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-2">Successful</h3>
              <p className="text-3xl font-bold text-green-400">{metrics.successful_trades}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-2">Accuracy</h3>
              <p className="text-3xl font-bold text-purple-400">{metrics.accuracy_percentage.toFixed(1)}%</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-2">P&L</h3>
              <p className={`text-3xl font-bold ${metrics.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatCurrency(metrics.total_profit_loss)}
              </p>
            </div>
          </div>
        )}

        {/* Portfolio Status */}
        {portfolio && (
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
            <h3 className="text-xl font-semibold text-white mb-4">💼 Portfolio Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-gray-300">USD Balance</p>
                <p className="text-2xl font-bold text-green-400">{formatCurrency(portfolio.usd_balance)}</p>
              </div>
              <div>
                <p className="text-gray-300">BTC Amount</p>
                <p className="text-2xl font-bold text-orange-400">{portfolio.btc_amount.toFixed(6)} BTC</p>
              </div>
              <div>
                <p className="text-gray-300">Last Trade Price</p>
                <p className="text-2xl font-bold text-blue-400">{formatCurrency(portfolio.last_trade_price)}</p>
              </div>
            </div>
          </div>
        )}

        {/* Live Trade Panel */}
        {liveTrade && (
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
            <h3 className="text-xl font-semibold text-white mb-4">🔥 Latest Trade Decision</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="flex items-center gap-4 mb-4">
                  <div className={`text-2xl font-bold ${getActionColor(liveTrade.decision)}`}>
                    {liveTrade.decision}
                  </div>
                  <div className={`text-lg ${getConfidenceColor(liveTrade.confidence)}`}>
                    {(liveTrade.confidence * 100).toFixed(1)}% confidence
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm ${liveTrade.is_valid ? 'bg-green-500' : 'bg-red-500'} text-white`}>
                    {liveTrade.is_valid ? '✅ Valid' : '❌ Invalid'}
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <p className="text-gray-300 text-sm">Price</p>
                    <p className="text-white font-semibold">{formatCurrency(liveTrade.price)}</p>
                  </div>
                  <div>
                    <p className="text-gray-300 text-sm">Timestamp</p>
                    <p className="text-white">{formatDate(liveTrade.timestamp)}</p>
                  </div>
                  <div>
                    <p className="text-gray-300 text-sm">P&L</p>
                    <p className={`font-semibold ${liveTrade.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatCurrency(liveTrade.profit_loss || 0)}
                    </p>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">🧠 Reasoning</h4>
                <p className="text-gray-300 text-sm mb-4">{liveTrade.reasoning}</p>
                
                <h4 className="text-lg font-semibold text-white mb-2">🔍 Verifier Verdict</h4>
                <p className="text-gray-300 text-sm">{liveTrade.verdict}</p>
              </div>
            </div>

            {/* Chain of Thought */}
            {liveTrade.chain_of_thought && (
              <div className="mt-6 border-t border-gray-600 pt-4">
                <h4 className="text-lg font-semibold text-white mb-3">🔗 Chain of Thought</h4>
                <div className="space-y-3">
                  <div>
                    <p className="text-gray-300 font-medium">Market Analysis:</p>
                    <p className="text-gray-400 text-sm">{liveTrade.chain_of_thought.market_analysis}</p>
                  </div>
                  <div>
                    <p className="text-gray-300 font-medium">Risk Assessment:</p>
                    <p className="text-gray-400 text-sm">{liveTrade.chain_of_thought.risk_assessment}</p>
                  </div>
                  <div>
                    <p className="text-gray-300 font-medium">Reasoning Steps:</p>
                    <ul className="text-gray-400 text-sm list-disc list-inside">
                      {liveTrade.chain_of_thought.reasoning_steps?.map((step, index) => (
                        <li key={index}>{step}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Market Data */}
        {marketData && (
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
            <h3 className="text-xl font-semibold text-white mb-4">📊 Current Market Data</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-gray-300">BTC Price</p>
                <p className="text-2xl font-bold text-orange-400">{formatCurrency(marketData.price)}</p>
              </div>
              <div>
                <p className="text-gray-300">Volume</p>
                <p className="text-2xl font-bold text-blue-400">{marketData.volume.toFixed(2)}x</p>
              </div>
              <div>
                <p className="text-gray-300">RSI</p>
                <p className="text-2xl font-bold text-purple-400">{marketData.rsi}</p>
              </div>
            </div>
          </div>
        )}

        {/* Trade History */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
          <h3 className="text-xl font-semibold text-white mb-4">📜 Trade History</h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-600">
                  <th className="text-left text-gray-300 pb-2">Date</th>
                  <th className="text-left text-gray-300 pb-2">Action</th>
                  <th className="text-left text-gray-300 pb-2">Price</th>
                  <th className="text-left text-gray-300 pb-2">Confidence</th>
                  <th className="text-left text-gray-300 pb-2">P&L</th>
                  <th className="text-left text-gray-300 pb-2">Valid</th>
                </tr>
              </thead>
              <tbody>
                {tradeHistory.map((trade, index) => (
                  <tr 
                    key={trade.id} 
                    className="border-b border-gray-700 hover:bg-white/5 cursor-pointer"
                    onClick={() => setSelectedTrade(selectedTrade === trade.id ? null : trade.id)}
                  >
                    <td className="py-3 text-gray-300">{formatDate(trade.timestamp)}</td>
                    <td className={`py-3 font-semibold ${getActionColor(trade.decision)}`}>
                      {trade.decision}
                    </td>
                    <td className="py-3 text-gray-300">{formatCurrency(trade.price)}</td>
                    <td className={`py-3 ${getConfidenceColor(trade.confidence)}`}>
                      {(trade.confidence * 100).toFixed(1)}%
                    </td>
                    <td className={`py-3 font-semibold ${trade.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatCurrency(trade.profit_loss || 0)}
                    </td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${trade.is_valid ? 'bg-green-500' : 'bg-red-500'} text-white`}>
                        {trade.is_valid ? 'Valid' : 'Invalid'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingDashboard;