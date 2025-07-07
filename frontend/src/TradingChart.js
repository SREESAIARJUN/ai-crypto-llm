import React, { useEffect, useRef, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const TradingChart = ({ tradeHistory, marketData, liveTrade }) => {
  const [chartData, setChartData] = useState(null);
  const [rsiData, setRsiData] = useState(null);
  const [volumeData, setVolumeData] = useState(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (tradeHistory && tradeHistory.length > 0) {
      updateChartData();
    }
  }, [tradeHistory, marketData, liveTrade]);

  const updateChartData = () => {
    // Sort trades by timestamp
    const sortedTrades = [...tradeHistory].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // Prepare data for the last 20 trades or 2 hours worth of data
    const recentTrades = sortedTrades.slice(-20);
    
    // Create time labels
    const labels = recentTrades.map(trade => {
      const date = new Date(trade.timestamp);
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
    });

    // Add current time if we have market data
    if (marketData) {
      const currentTime = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
      });
      labels.push(currentTime);
    }

    // Price data
    const priceData = recentTrades.map(trade => trade.price);
    if (marketData) {
      priceData.push(marketData.price);
    }

    // RSI data
    const rsiValues = recentTrades.map(trade => {
      // Calculate simulated RSI based on price movement and confidence
      const baseRsi = 50;
      const priceMovement = trade.decision === 'BUY' ? 10 : trade.decision === 'SELL' ? -10 : 0;
      const confidenceAdjustment = (trade.confidence - 0.5) * 20;
      return Math.max(0, Math.min(100, baseRsi + priceMovement + confidenceAdjustment));
    });
    
    if (marketData) {
      rsiValues.push(marketData.rsi);
    }

    // Volume data (simulated)
    const volumeValues = recentTrades.map((trade, index) => {
      const baseVolume = 1.0;
      const volatility = Math.random() * 0.5;
      const trendFactor = trade.confidence * 0.5;
      return baseVolume + volatility + trendFactor;
    });

    if (marketData) {
      volumeValues.push(marketData.volume);
    }

    // Create trade decision points
    const tradePoints = recentTrades.map((trade, index) => ({
      x: index,
      y: trade.price,
      decision: trade.decision,
      confidence: trade.confidence,
      valid: trade.is_valid
    }));

    // Main price chart data
    const mainChartData = {
      labels,
      datasets: [
        {
          label: 'Bitcoin Price',
          data: priceData,
          borderColor: '#facc15',
          backgroundColor: 'rgba(250, 204, 21, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: '#facc15',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          shadow: true
        },
        {
          label: 'Trade Decisions',
          data: priceData.map((price, index) => {
            const trade = recentTrades[index];
            return trade ? price : null;
          }),
          borderColor: 'transparent',
          backgroundColor: 'transparent',
          pointRadius: priceData.map((_, index) => {
            const trade = recentTrades[index];
            return trade ? 12 : 0;
          }),
          pointHoverRadius: priceData.map((_, index) => {
            const trade = recentTrades[index];
            return trade ? 15 : 0;
          }),
          pointBackgroundColor: priceData.map((_, index) => {
            const trade = recentTrades[index];
            if (!trade) return 'transparent';
            switch (trade.decision) {
              case 'BUY': return '#00FFAA';
              case 'SELL': return '#FF4C4C';
              case 'HOLD': return '#FFD369';
              default: return '#A3A3A3';
            }
          }),
          pointBorderColor: '#ffffff',
          pointBorderWidth: 3,
          showLine: false
        }
      ]
    };

    // RSI chart data
    const rsiChartData = {
      labels,
      datasets: [
        {
          label: 'RSI',
          data: rsiValues,
          borderColor: '#60a5fa',
          backgroundColor: 'rgba(96, 165, 250, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#60a5fa',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 1
        },
        {
          label: 'Overbought (70)',
          data: new Array(labels.length).fill(70),
          borderColor: '#FF4C4C',
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderDash: [5, 5],
          pointRadius: 0,
          tension: 0
        },
        {
          label: 'Oversold (30)',
          data: new Array(labels.length).fill(30),
          borderColor: '#00FFAA',
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderDash: [5, 5],
          pointRadius: 0,
          tension: 0
        }
      ]
    };

    // Volume chart data
    const volumeChartData = {
      labels,
      datasets: [
        {
          label: 'Volume',
          data: volumeValues,
          backgroundColor: volumeValues.map((_, index) => {
            const trade = recentTrades[index];
            if (!trade) return 'rgba(74, 222, 128, 0.6)';
            switch (trade.decision) {
              case 'BUY': return 'rgba(0, 255, 170, 0.6)';
              case 'SELL': return 'rgba(255, 76, 76, 0.6)';
              default: return 'rgba(255, 211, 105, 0.6)';
            }
          }),
          borderColor: volumeValues.map((_, index) => {
            const trade = recentTrades[index];
            if (!trade) return '#4ade80';
            switch (trade.decision) {
              case 'BUY': return '#00FFAA';
              case 'SELL': return '#FF4C4C';
              default: return '#FFD369';
            }
          }),
          borderWidth: 1,
          borderRadius: 4
        }
      ]
    };

    setChartData(mainChartData);
    setRsiData(rsiChartData);
    setVolumeData(volumeChartData);
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          drawBorder: false
        },
        ticks: {
          color: '#A3A3A3',
          font: {
            size: 11
          },
          maxTicksLimit: 8
        }
      },
      y: {
        display: true,
        position: 'left',
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          drawBorder: false
        },
        ticks: {
          color: '#A3A3A3',
          font: {
            size: 11
          },
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      }
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: '#E5E5E5',
          font: {
            size: 12,
            weight: 600
          },
          usePointStyle: true,
          padding: 20
        }
      },
      tooltip: {
        enabled: true,
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#FFFFFF',
        bodyColor: '#A3A3A3',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          title: function(context) {
            return `Time: ${context[0].label}`;
          },
          label: function(context) {
            const sortedTrades = [...tradeHistory].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            const recentTrades = sortedTrades.slice(-20);
            const trade = recentTrades[context.dataIndex];
            if (context.datasetIndex === 0) {
              return `Price: $${context.parsed.y.toLocaleString()}`;
            } else if (context.datasetIndex === 1 && trade) {
              return [
                `Decision: ${trade.decision}`,
                `Confidence: ${(trade.confidence * 100).toFixed(1)}%`,
                `Valid: ${trade.is_valid ? 'Yes' : 'No'}`
              ];
            }
            return context.formattedValue;
          }
        }
      }
    },
    elements: {
      point: {
        hoverBorderWidth: 3
      }
    },
    animation: {
      duration: 1000,
      easing: 'easeInOutQuart'
    }
  };

  const rsiOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        display: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          drawBorder: false
        },
        ticks: {
          color: '#A3A3A3',
          font: { size: 10 },
          maxTicksLimit: 6
        }
      },
      y: {
        display: true,
        min: 0,
        max: 100,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          drawBorder: false
        },
        ticks: {
          color: '#A3A3A3',
          font: { size: 10 },
          stepSize: 20
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#FFFFFF',
        bodyColor: '#A3A3A3',
        cornerRadius: 8
      }
    },
    animation: {
      duration: 800
    }
  };

  const volumeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        display: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          drawBorder: false
        },
        ticks: {
          color: '#A3A3A3',
          font: { size: 10 },
          maxTicksLimit: 6
        }
      },
      y: {
        display: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          drawBorder: false
        },
        ticks: {
          color: '#A3A3A3',
          font: { size: 10 }
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#FFFFFF',
        bodyColor: '#A3A3A3',
        cornerRadius: 8
      }
    },
    animation: {
      duration: 800
    }
  };

  if (!chartData) {
    return (
      <div className="chart-container flex items-center justify-center">
        <div className="text-center">
          <div className="premium-spinner mx-auto mb-4"></div>
          <p className="secondary-text">Loading trading chart...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card">
      <h3 className="text-xl font-semibold primary-text mb-4">📈 Live Trading Chart</h3>
      
      {/* Main Price Chart */}
      <div className="chart-container mb-6" style={{ height: '400px' }}>
        <Line ref={chartRef} data={chartData} options={chartOptions} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* RSI Chart */}
        <div>
          <h4 className="text-sm font-semibold primary-text mb-2 rsi-glow">📊 RSI Indicator</h4>
          <div className="chart-container" style={{ height: '200px' }}>
            <Line data={rsiData} options={rsiOptions} />
          </div>
        </div>

        {/* Volume Chart */}
        <div>
          <h4 className="text-sm font-semibold primary-text mb-2 volume-glow">📊 Volume Analysis</h4>
          <div className="chart-container" style={{ height: '200px' }}>
            <Bar data={volumeData} options={volumeOptions} />
          </div>
        </div>
      </div>

      {/* Chart Legend */}
      <div className="mt-4 p-4 bg-black/20 rounded-lg">
        <h4 className="text-sm font-semibold primary-text mb-2">Chart Legend</h4>
        <div className="flex flex-wrap gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
            <span className="secondary-text">Bitcoin Price</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#00FFAA'}}></div>
            <span className="secondary-text">BUY Decision</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#FF4C4C'}}></div>
            <span className="secondary-text">SELL Decision</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#FFD369'}}></div>
            <span className="secondary-text">HOLD Decision</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-400"></div>
            <span className="secondary-text">RSI</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingChart;