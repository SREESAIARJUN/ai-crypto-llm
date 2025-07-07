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
  const [autoTradingEnabled, setAutoTradingEnabled] = useState(false);
  const [autoTradingLoading, setAutoTradingLoading] = useState(false);

  // Fetch auto-trading status
  const fetchAutoTradingStatus = async () => {
    try {
      const response = await axios.get(`${API}/trade/auto/status`);
      setAutoTradingEnabled(response.data.auto_trading_enabled);
    } catch (error) {
      console.error('Error fetching auto-trading status:', error);
    }
  };

  // Toggle auto-trading
  const toggleAutoTrading = async () => {
    setAutoTradingLoading(true);
    try {
      const endpoint = autoTradingEnabled ? '/trade/auto/disable' : '/trade/auto/enable';
      const response = await axios.post(`${API}${endpoint}`);
      setAutoTradingEnabled(response.data.status === 'active');
      
      // Show notification
      const message = autoTradingEnabled ? 'Auto-trading disabled' : 'Auto-trading enabled';
      showNotification(message, 'success');
    } catch (error) {
      console.error('Error toggling auto-trading:', error);
      showNotification('Error toggling auto-trading', 'error');
    } finally {
      setAutoTradingLoading(false);
    }
  };

  // Show notification
  const showNotification = (message, type) => {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 3000);
  };

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
      showNotification('Trade decision executed successfully!', 'success');
    } catch (error) {
      console.error('Error triggering trade:', error);
      showNotification('Error triggering trade: ' + error.message, 'error');
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
        fetchPortfolio(),
        fetchAutoTradingStatus()
      ]);
    };

    fetchAllData();

    if (autoRefresh) {
      const interval = setInterval(fetchAllData, 15000); // Refresh every 15 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getActionColor = (action) => {
    switch (action) {
      case 'BUY': return 'text-green-400';
      case 'SELL': return 'text-red-400';
      case 'HOLD': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getActionBg = (action) => {
    switch (action) {
      case 'BUY': return 'bg-green-500/20 border-green-500/50';
      case 'SELL': return 'bg-red-500/20 border-red-500/50';
      case 'HOLD': return 'bg-yellow-500/20 border-yellow-500/50';
      default: return 'bg-gray-500/20 border-gray-500/50';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return 'text-green-400';
      case 'negative': return 'text-red-400';
      case 'neutral': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return '😊';
      case 'negative': return '😢';
      case 'neutral': return '😐';
      default: return '❓';
    }
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
    <div className="netflix-bg">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2 netflix-title">
            🤖 Autonomous Crypto Trading Agent
          </h1>
          <p className="text-gray-300 text-lg">
            LLM-Powered Paper Trading with Real-time Sentiment Analysis
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <button
            onClick={triggerTrade}
            disabled={loading}
            className="netflix-button bg-red-600 hover:bg-red-700 disabled:bg-red-800/50"
          >
            {loading ? (
              <>
                <div className="spinner inline-block mr-2"></div>
                🧠 Analyzing...
              </>
            ) : (
              '🧠 Manual Trade Decision'
            )}
          </button>
          
          <button
            onClick={toggleAutoTrading}
            disabled={autoTradingLoading}
            className={`netflix-button ${
              autoTradingEnabled 
                ? 'bg-orange-600 hover:bg-orange-700' 
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {autoTradingLoading ? (
              <>
                <div className="spinner inline-block mr-2"></div>
                Processing...
              </>
            ) : (
              autoTradingEnabled ? '⏸️ Disable Auto-Trading' : '🚀 Enable Auto-Trading'
            )}
          </button>
          
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`netflix-button ${
              autoRefresh 
                ? 'bg-blue-600 hover:bg-blue-700' 
                : 'bg-gray-600 hover:bg-gray-700'
            }`}
          >
            {autoRefresh ? '🔄 Auto-refresh ON' : '⏸️ Auto-refresh OFF'}
          </button>
        </div>

        {/* Auto-Trading Status */}
        <div className="text-center mb-8">
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
            autoTradingEnabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
          }`}>
            <div className={`w-3 h-3 rounded-full ${
              autoTradingEnabled ? 'bg-green-400 animate-pulse' : 'bg-gray-400'
            }`}></div>
            <span className="font-medium">
              Auto-Trading: {autoTradingEnabled ? 'ACTIVE' : 'INACTIVE'}
            </span>
          </div>
        </div>

        {/* Metrics Dashboard */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="netflix-card">
              <h3 className="text-lg font-semibold text-white mb-2">Total Trades</h3>
              <p className="text-3xl font-bold text-blue-400">{metrics.total_trades}</p>
            </div>
            <div className="netflix-card">
              <h3 className="text-lg font-semibold text-white mb-2">Successful</h3>
              <p className="text-3xl font-bold text-green-400">{metrics.successful_trades}</p>
            </div>
            <div className="netflix-card">
              <h3 className="text-lg font-semibold text-white mb-2">Accuracy</h3>
              <p className="text-3xl font-bold text-purple-400">{metrics.accuracy_percentage.toFixed(1)}%</p>
            </div>
            <div className="netflix-card">
              <h3 className="text-lg font-semibold text-white mb-2">P&L</h3>
              <p className={`text-3xl font-bold ${metrics.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatCurrency(metrics.total_profit_loss)}
              </p>
            </div>
          </div>
        )}

        {/* Portfolio & Market Data Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Portfolio Status */}
          {portfolio && (
            <div className="netflix-card">
              <h3 className="text-xl font-semibold text-white mb-4">💼 Portfolio Status</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">USD Balance</span>
                  <span className="text-2xl font-bold text-green-400">{formatCurrency(portfolio.usd_balance)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">BTC Amount</span>
                  <span className="text-2xl font-bold text-orange-400">{portfolio.btc_amount.toFixed(6)} BTC</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Last Trade Price</span>
                  <span className="text-2xl font-bold text-blue-400">{formatCurrency(portfolio.last_trade_price)}</span>
                </div>
              </div>
            </div>
          )}

          {/* Market Data & Sentiment */}
          {marketData && (
            <div className="netflix-card">
              <h3 className="text-xl font-semibold text-white mb-4">📊 Market Data & Sentiment</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">BTC Price</span>
                  <span className="text-2xl font-bold text-orange-400">{formatCurrency(marketData.price)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Volume</span>
                  <span className="text-lg font-bold text-blue-400">{marketData.volume.toFixed(2)}x</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">RSI</span>
                  <span className="text-lg font-bold text-purple-400">{marketData.rsi.toFixed(1)}</span>
                </div>
                <div className="border-t border-gray-700 pt-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-300">News Sentiment</span>
                    <span className={`font-bold ${getSentimentColor(marketData.news_sentiment)}`}>
                      {getSentimentIcon(marketData.news_sentiment)} {marketData.news_sentiment}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">Twitter Sentiment</span>
                    <span className={`font-bold ${getSentimentColor(marketData.twitter_sentiment)}`}>
                      {getSentimentIcon(marketData.twitter_sentiment)} {marketData.twitter_sentiment}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Live Trade Panel */}
        {liveTrade && (
          <div className="netflix-card mb-8">
            <h3 className="text-xl font-semibold text-white mb-4">🔥 Latest Trade Decision</h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <div className="flex items-center gap-4 mb-4">
                  <div className={`px-4 py-2 rounded-lg border ${getActionBg(liveTrade.decision)}`}>
                    <span className={`text-2xl font-bold ${getActionColor(liveTrade.decision)}`}>
                      {liveTrade.decision}
                    </span>
                  </div>
                  <div className={`text-lg ${getConfidenceColor(liveTrade.confidence)}`}>
                    {(liveTrade.confidence * 100).toFixed(1)}% confidence
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm ${liveTrade.is_valid ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                    {liveTrade.is_valid ? '✅ Valid' : '❌ Invalid'}
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Price</span>
                    <span className="text-white font-semibold">{formatCurrency(liveTrade.price)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Timestamp</span>
                    <span className="text-white text-sm">{formatDate(liveTrade.timestamp)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">P&L</span>
                    <span className={`font-semibold ${liveTrade.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatCurrency(liveTrade.profit_loss || 0)}
                    </span>
                  </div>
                  {liveTrade.news_sentiment && (
                    <div className="flex justify-between">
                      <span className="text-gray-300">News Sentiment</span>
                      <span className={`font-semibold ${getSentimentColor(liveTrade.news_sentiment)}`}>
                        {getSentimentIcon(liveTrade.news_sentiment)} {liveTrade.news_sentiment}
                      </span>
                    </div>
                  )}
                  {liveTrade.twitter_sentiment && (
                    <div className="flex justify-between">
                      <span className="text-gray-300">Twitter Sentiment</span>
                      <span className={`font-semibold ${getSentimentColor(liveTrade.twitter_sentiment)}`}>
                        {getSentimentIcon(liveTrade.twitter_sentiment)} {liveTrade.twitter_sentiment}
                      </span>
                    </div>
                  )}
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
              <div className="mt-6 border-t border-gray-700 pt-4">
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

        {/* Trade History */}
        <div className="netflix-card">
          <h3 className="text-xl font-semibold text-white mb-4">📜 Trade History</h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left text-gray-300 pb-2">Date</th>
                  <th className="text-left text-gray-300 pb-2">Action</th>
                  <th className="text-left text-gray-300 pb-2">Price</th>
                  <th className="text-left text-gray-300 pb-2">Confidence</th>
                  <th className="text-left text-gray-300 pb-2">P&L</th>
                  <th className="text-left text-gray-300 pb-2">Sentiment</th>
                  <th className="text-left text-gray-300 pb-2">Valid</th>
                </tr>
              </thead>
              <tbody>
                {tradeHistory.map((trade, index) => (
                  <tr 
                    key={trade.id} 
                    className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors"
                    onClick={() => setSelectedTrade(selectedTrade === trade.id ? null : trade.id)}
                  >
                    <td className="py-3 text-gray-300 text-xs">{formatDate(trade.timestamp)}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${getActionBg(trade.decision)} ${getActionColor(trade.decision)}`}>
                        {trade.decision}
                      </span>
                    </td>
                    <td className="py-3 text-gray-300">{formatCurrency(trade.price)}</td>
                    <td className={`py-3 ${getConfidenceColor(trade.confidence)}`}>
                      {(trade.confidence * 100).toFixed(1)}%
                    </td>
                    <td className={`py-3 font-semibold ${trade.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatCurrency(trade.profit_loss || 0)}
                    </td>
                    <td className="py-3 text-xs">
                      <div className="flex gap-1">
                        {trade.news_sentiment && (
                          <span className={`${getSentimentColor(trade.news_sentiment)}`}>
                            📰{getSentimentIcon(trade.news_sentiment)}
                          </span>
                        )}
                        {trade.twitter_sentiment && (
                          <span className={`${getSentimentColor(trade.twitter_sentiment)}`}>
                            🐦{getSentimentIcon(trade.twitter_sentiment)}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${trade.is_valid ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
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