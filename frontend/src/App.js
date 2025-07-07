import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

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
  const [chartData, setChartData] = useState(null);
  const [chartTimeframe, setChartTimeframe] = useState('1h');
  const [chartLoading, setChartLoading] = useState(false);

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
    notification.className = `premium-notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove notification after 4 seconds
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 4000);
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

  // Fetch chart data
  const fetchChartData = async (timeframe = chartTimeframe) => {
    setChartLoading(true);
    try {
      const response = await axios.get(`${API}/trades/chart-data?timeframe=${timeframe}`);
      setChartData(response.data);
    } catch (error) {
      console.error('Error fetching chart data:', error);
    } finally {
      setChartLoading(false);
    }
  };

  // Change chart timeframe
  const handleTimeframeChange = (newTimeframe) => {
    setChartTimeframe(newTimeframe);
    fetchChartData(newTimeframe);
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
        fetchAutoTradingStatus(),
        fetchChartData()
      ]);
    };

    fetchAllData();

    if (autoRefresh) {
      const interval = setInterval(fetchAllData, 15000); // Refresh every 15 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getActionClasses = (action) => {
    switch (action) {
      case 'BUY': return 'action-badge badge-buy';
      case 'SELL': return 'action-badge badge-sell';
      case 'HOLD': return 'action-badge badge-hold';
      default: return 'action-badge';
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'BUY': return 'status-buy';
      case 'SELL': return 'status-sell';
      case 'HOLD': return 'status-hold';
      default: return 'secondary-text';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'confidence-high';
    if (confidence >= 0.6) return 'confidence-medium';
    return 'confidence-low';
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return 'sentiment-positive';
      case 'negative': return 'sentiment-negative';
      case 'neutral': return 'sentiment-neutral';
      default: return 'secondary-text';
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

  // Prepare chart data for Chart.js
  const prepareChartData = () => {
    if (!chartData || !chartData.price_history) return null;

    const labels = chartData.price_history.map(point => new Date(point.timestamp));
    const prices = chartData.price_history.map(point => point.price);
    const portfolioValues = chartData.portfolio_history.map(snapshot => ({
      x: new Date(snapshot.timestamp),
      y: snapshot.total_value
    }));

    // Prepare trade markers as scatter points
    const tradePoints = chartData.trade_markers.map(trade => ({
      x: new Date(trade.timestamp),
      y: trade.price,
      decision: trade.decision,
      confidence: trade.confidence,
      profit_loss: trade.profit_loss || 0,
      news_sentiment: trade.news_sentiment,
      twitter_sentiment: trade.twitter_sentiment
    }));

    const buyTrades = tradePoints.filter(trade => trade.decision === 'BUY');
    const sellTrades = tradePoints.filter(trade => trade.decision === 'SELL');
    const holdTrades = tradePoints.filter(trade => trade.decision === 'HOLD');

    return {
      labels,
      datasets: [
        {
          label: 'Bitcoin Price',
          data: prices,
          borderColor: '#F7931A',
          backgroundColor: 'rgba(247, 147, 26, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 1,
          pointHoverRadius: 5,
          yAxisID: 'price'
        },
        {
          label: 'Portfolio Value',
          data: portfolioValues,
          borderColor: '#00D084',
          backgroundColor: 'rgba(0, 208, 132, 0.1)',
          borderWidth: 2,
          fill: false,
          tension: 0.4,
          pointRadius: 1,
          pointHoverRadius: 5,
          yAxisID: 'portfolio'
        },
        {
          label: 'BUY Trades',
          data: buyTrades,
          backgroundColor: '#00D084',
          borderColor: '#00D084',
          pointRadius: 8,
          pointHoverRadius: 12,
          showLine: false,
          yAxisID: 'price'
        },
        {
          label: 'SELL Trades',
          data: sellTrades,
          backgroundColor: '#F6465D',
          borderColor: '#F6465D',
          pointRadius: 8,
          pointHoverRadius: 12,
          showLine: false,
          yAxisID: 'price'
        },
        {
          label: 'HOLD Trades',
          data: holdTrades,
          backgroundColor: '#FFA500',
          borderColor: '#FFA500',
          pointRadius: 6,
          pointHoverRadius: 10,
          showLine: false,
          yAxisID: 'price'
        }
      ]
    };
  };

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#E4E4E7',
          usePointStyle: true
        }
      },
      title: {
        display: true,
        text: `Live Trades Chart - ${chartTimeframe.toUpperCase()}`,
        color: '#E4E4E7',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#E4E4E7',
        bodyColor: '#E4E4E7',
        borderColor: '#374151',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const datasetLabel = context.dataset.label;
            
            if (datasetLabel.includes('Trades')) {
              const trade = context.raw;
              return [
                `${datasetLabel}: ${trade.decision}`,
                `Price: $${trade.y.toLocaleString()}`,
                `Confidence: ${(trade.confidence * 100).toFixed(1)}%`,
                `P&L: $${trade.profit_loss.toFixed(2)}`,
                `News: ${trade.news_sentiment || 'N/A'}`,
                `Twitter: ${trade.twitter_sentiment || 'N/A'}`
              ];
            } else if (datasetLabel === 'Bitcoin Price') {
              return `Price: $${context.parsed.y.toLocaleString()}`;
            } else if (datasetLabel === 'Portfolio Value') {
              return `Portfolio: $${context.parsed.y.toFixed(2)}`;
            }
            
            return `${datasetLabel}: ${context.parsed.y}`;
          }
        }
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          displayFormats: {
            hour: 'HH:mm',
            day: 'MMM dd',
            week: 'MMM dd'
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: '#9CA3AF'
        }
      },
      price: {
        type: 'linear',
        display: true,
        position: 'left',
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: '#9CA3AF',
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        },
        title: {
          display: true,
          text: 'Bitcoin Price (USD)',
          color: '#F7931A'
        }
      },
      portfolio: {
        type: 'linear',
        display: true,
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: '#9CA3AF',
          callback: function(value) {
            return '$' + value.toFixed(0);
          }
        },
        title: {
          display: true,
          text: 'Portfolio Value (USD)',
          color: '#00D084'
        }
      }
    }
  };

  return (
    <div className="premium-dark-bg">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold premium-title mb-4">
            🤖 Autonomous Crypto Trading Agent
          </h1>
          <p className="secondary-text text-lg">
            LLM-Powered Paper Trading with Real-time Sentiment Analysis
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <button
            onClick={triggerTrade}
            disabled={loading}
            className="premium-button btn-manual"
          >
            {loading ? (
              <>
                <div className="premium-spinner inline-block mr-2"></div>
                🧠 Analyzing...
              </>
            ) : (
              '🧠 Manual Trade Decision'
            )}
          </button>
          
          <button
            onClick={toggleAutoTrading}
            disabled={autoTradingLoading}
            className={`premium-button ${
              autoTradingEnabled ? 'btn-auto-disable' : 'btn-auto-enable'
            }`}
          >
            {autoTradingLoading ? (
              <>
                <div className="premium-spinner inline-block mr-2"></div>
                Processing...
              </>
            ) : (
              autoTradingEnabled ? '⏸️ Disable Auto-Trading' : '🚀 Enable Auto-Trading'
            )}
          </button>
          
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`premium-button ${autoRefresh ? 'btn-refresh' : 'btn-manual'}`}
          >
            {autoRefresh ? '🔄 Auto-refresh ON' : '⏸️ Auto-refresh OFF'}
          </button>
        </div>

        {/* Auto-Trading Status */}
        <div className="text-center mb-8">
          <div className={`auto-trading-status ${
            autoTradingEnabled ? 'auto-trading-active' : 'auto-trading-inactive'
          }`}>
            <div className={`status-dot ${
              autoTradingEnabled ? 'status-dot-active' : 'status-dot-inactive'
            }`}></div>
            <span className="font-medium">
              Auto-Trading: {autoTradingEnabled ? 'ACTIVE' : 'INACTIVE'}
            </span>
          </div>
        </div>

        {/* Metrics Dashboard */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="metric-card">
              <h3 className="text-lg font-semibold primary-text mb-2">Total Trades</h3>
              <p className="text-3xl font-bold btc-glow">{metrics.total_trades}</p>
            </div>
            <div className="metric-card">
              <h3 className="text-lg font-semibold primary-text mb-2">Successful</h3>
              <p className="text-3xl font-bold status-buy">{metrics.successful_trades}</p>
            </div>
            <div className="metric-card">
              <h3 className="text-lg font-semibold primary-text mb-2">Accuracy</h3>
              <p className="text-3xl font-bold rsi-glow">{metrics.accuracy_percentage.toFixed(1)}%</p>
            </div>
            <div className="metric-card">
              <h3 className="text-lg font-semibold primary-text mb-2">P&L</h3>
              <p className={`text-3xl font-bold ${metrics.total_profit_loss >= 0 ? 'status-buy' : 'status-sell'}`}>
                {formatCurrency(metrics.total_profit_loss)}
              </p>
            </div>
          </div>
        )}

        {/* Portfolio & Market Data Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Portfolio Status */}
          {portfolio && (
            <div className="glass-card">
              <h3 className="text-xl font-semibold primary-text mb-4">💼 Portfolio Status</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="secondary-text">USD Balance</span>
                  <span className="text-2xl font-bold status-buy">{formatCurrency(portfolio.usd_balance)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="secondary-text">BTC Amount</span>
                  <span className="text-2xl font-bold btc-glow">{portfolio.btc_amount.toFixed(6)} BTC</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="secondary-text">Last Trade Price</span>
                  <span className="text-2xl font-bold rsi-glow">{formatCurrency(portfolio.last_trade_price)}</span>
                </div>
              </div>
            </div>
          )}

          {/* Market Data & Sentiment */}
          {marketData && (
            <div className="glass-card">
              <h3 className="text-xl font-semibold primary-text mb-4">📊 Market Data & Sentiment</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="secondary-text">BTC Price</span>
                  <span className="text-2xl font-bold btc-glow">{formatCurrency(marketData.price)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="secondary-text">Volume</span>
                  <span className="text-lg font-bold volume-glow">{marketData.volume.toFixed(2)}x</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="secondary-text">RSI</span>
                  <span className="text-lg font-bold rsi-glow">{marketData.rsi.toFixed(1)}</span>
                </div>
                <div className="border-t border-gray-700 pt-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="secondary-text">News Sentiment</span>
                    <span className={`font-bold ${getSentimentColor(marketData.news_sentiment)}`}>
                      {getSentimentIcon(marketData.news_sentiment)} {marketData.news_sentiment}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="secondary-text">Twitter Sentiment</span>
                    <span className={`font-bold ${getSentimentColor(marketData.twitter_sentiment)}`}>
                      {getSentimentIcon(marketData.twitter_sentiment)} {marketData.twitter_sentiment}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Live Trades Chart */}
        <div className="glass-card mb-8">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold primary-text">📈 Live Trades Chart</h3>
            <div className="flex gap-2">
              {['1h', '24h', '7d'].map(timeframe => (
                <button
                  key={timeframe}
                  onClick={() => handleTimeframeChange(timeframe)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    chartTimeframe === timeframe
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {timeframe.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          
          {chartLoading ? (
            <div className="flex items-center justify-center h-96">
              <div className="premium-spinner mr-2"></div>
              <span className="secondary-text">Loading chart data...</span>
            </div>
          ) : chartData && prepareChartData() ? (
            <div className="h-96">
              <Line data={prepareChartData()} options={chartOptions} />
            </div>
          ) : (
            <div className="flex items-center justify-center h-96">
              <span className="secondary-text">No chart data available</span>
            </div>
          )}
          
          {/* Chart Legend Info */}
          {chartData && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span className="secondary-text">Bitcoin Price</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="secondary-text">Portfolio Value</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="secondary-text">BUY Trades</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="secondary-text">SELL Trades</span>
              </div>
            </div>
          )}
        </div>
        {liveTrade && (
          <div className="glass-card mb-8">
            <h3 className="text-xl font-semibold primary-text mb-4">🔥 Latest Trade Decision</h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <div className="flex items-center gap-4 mb-4">
                  <div className={getActionClasses(liveTrade.decision)}>
                    {liveTrade.decision}
                  </div>
                  <div className={`text-lg font-semibold ${getConfidenceColor(liveTrade.confidence)}`}>
                    {(liveTrade.confidence * 100).toFixed(1)}% confidence
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-semibold ${liveTrade.is_valid ? 'status-valid' : 'status-invalid'}`}>
                    {liveTrade.is_valid ? '✅ Valid' : '❌ Invalid'}
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="secondary-text">Price</span>
                    <span className="primary-text font-semibold">{formatCurrency(liveTrade.price)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="secondary-text">Timestamp</span>
                    <span className="primary-text text-sm">{formatDate(liveTrade.timestamp)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="secondary-text">P&L</span>
                    <span className={`font-semibold ${liveTrade.profit_loss >= 0 ? 'status-buy' : 'status-sell'}`}>
                      {formatCurrency(liveTrade.profit_loss || 0)}
                    </span>
                  </div>
                  {liveTrade.news_sentiment && (
                    <div className="flex justify-between">
                      <span className="secondary-text">News Sentiment</span>
                      <span className={`font-semibold ${getSentimentColor(liveTrade.news_sentiment)}`}>
                        {getSentimentIcon(liveTrade.news_sentiment)} {liveTrade.news_sentiment}
                      </span>
                    </div>
                  )}
                  {liveTrade.twitter_sentiment && (
                    <div className="flex justify-between">
                      <span className="secondary-text">Twitter Sentiment</span>
                      <span className={`font-semibold ${getSentimentColor(liveTrade.twitter_sentiment)}`}>
                        {getSentimentIcon(liveTrade.twitter_sentiment)} {liveTrade.twitter_sentiment}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold primary-text mb-2">🧠 Reasoning</h4>
                <p className="secondary-text text-sm mb-4">{liveTrade.reasoning}</p>
                
                <h4 className="text-lg font-semibold primary-text mb-2">🔍 Verifier Verdict</h4>
                <p className="secondary-text text-sm">{liveTrade.verdict}</p>
              </div>
            </div>

            {/* Chain of Thought */}
            {liveTrade.chain_of_thought && (
              <div className="chain-of-thought">
                <h4 className="text-lg font-semibold primary-text mb-3">🔗 Chain of Thought</h4>
                <div className="space-y-3">
                  <div>
                    <p className="secondary-text font-medium">Market Analysis:</p>
                    <p className="muted-text text-sm">{liveTrade.chain_of_thought.market_analysis}</p>
                  </div>
                  <div>
                    <p className="secondary-text font-medium">Risk Assessment:</p>
                    <p className="muted-text text-sm">{liveTrade.chain_of_thought.risk_assessment}</p>
                  </div>
                  <div>
                    <p className="secondary-text font-medium">Reasoning Steps:</p>
                    <ul className="muted-text text-sm list-disc list-inside">
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
        <div className="glass-card">
          <h3 className="text-xl font-semibold primary-text mb-4">📜 Trade History</h3>
          
          <div className="overflow-x-auto">
            <table className="premium-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Action</th>
                  <th>Price</th>
                  <th>Confidence</th>
                  <th>P&L</th>
                  <th>Sentiment</th>
                  <th>Valid</th>
                </tr>
              </thead>
              <tbody>
                {tradeHistory.map((trade, index) => (
                  <tr 
                    key={trade.id} 
                    className="cursor-pointer"
                    onClick={() => setSelectedTrade(selectedTrade === trade.id ? null : trade.id)}
                  >
                    <td className="text-xs">{formatDate(trade.timestamp)}</td>
                    <td>
                      <span className={`${getActionClasses(trade.decision)} px-2 py-1 text-xs`}>
                        {trade.decision}
                      </span>
                    </td>
                    <td>{formatCurrency(trade.price)}</td>
                    <td className={getConfidenceColor(trade.confidence)}>
                      {(trade.confidence * 100).toFixed(1)}%
                    </td>
                    <td className={`font-semibold ${trade.profit_loss >= 0 ? 'status-buy' : 'status-sell'}`}>
                      {formatCurrency(trade.profit_loss || 0)}
                    </td>
                    <td className="text-xs">
                      <div className="flex gap-1">
                        {trade.news_sentiment && (
                          <span className={getSentimentColor(trade.news_sentiment)}>
                            📰{getSentimentIcon(trade.news_sentiment)}
                          </span>
                        )}
                        {trade.twitter_sentiment && (
                          <span className={getSentimentColor(trade.twitter_sentiment)}>
                            🐦{getSentimentIcon(trade.twitter_sentiment)}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${trade.is_valid ? 'status-valid' : 'status-invalid'}`}>
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