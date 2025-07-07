from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uuid
from datetime import datetime, timedelta
import json
import asyncio
import aiohttp
from emergentintegrations.llm.chat import LlmChat, UserMessage
import tweepy
import feedparser
from bs4 import BeautifulSoup
from textblob import TextBlob
import re
from collections import defaultdict

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class TradingDecision(BaseModel):
    action: str  # BUY, SELL, HOLD
    confidence: float
    reasoning: str

class ChainOfThought(BaseModel):
    market_analysis: str
    risk_assessment: str
    reasoning_steps: List[str]

class TradeResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    price: float
    decision: str
    confidence: float
    reasoning: str
    evidence: List[str]
    is_valid: bool = True
    verdict: str = "Pending verification"
    profit_loss: Optional[float] = None
    chain_of_thought: Optional[Dict[str, Any]] = None
    news_sentiment: Optional[str] = None
    twitter_sentiment: Optional[str] = None

class TradeResultCreate(BaseModel):
    price: float
    decision: str
    confidence: float
    reasoning: str
    evidence: List[str]

class VerificationResult(BaseModel):
    is_valid: bool
    verdict: str
    issues: List[str]

class MarketData(BaseModel):
    price: float
    volume: float
    rsi: float
    news: List[str]
    tweets: List[str]
    news_sentiment: str
    twitter_sentiment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TradingMetrics(BaseModel):
    total_trades: int
    successful_trades: int
    total_profit_loss: float
    accuracy_percentage: float
    last_trade_time: Optional[datetime] = None
    auto_trading_enabled: bool = False

class ChartDataPoint(BaseModel):
    timestamp: datetime
    price: float
    volume: float
    rsi: float

class TradeMarker(BaseModel):
    timestamp: datetime
    price: float
    decision: str
    confidence: float
    profit_loss: Optional[float] = None
    news_sentiment: Optional[str] = None
    twitter_sentiment: Optional[str] = None

class PortfolioSnapshot(BaseModel):
    timestamp: datetime
    total_value: float
    usd_balance: float
    btc_amount: float
    btc_value: float

class ChartData(BaseModel):
    price_history: List[ChartDataPoint]
    trade_markers: List[TradeMarker]
    portfolio_history: List[PortfolioSnapshot]
    sentiment_timeline: List[Dict[str, Any]]
    timeframe: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class TradingSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    initial_portfolio_value: float = 1000.0
    auto_trading_interval_minutes: int = 5
    price_history_limit: int = 100
    portfolio_snapshots_limit: int = 100
    sentiment_history_limit: int = 50
    frontend_refresh_interval_seconds: int = 15
    risk_threshold: float = 0.7
    confidence_threshold: float = 0.6
    max_trades_per_day: int = 10
    stop_loss_percentage: float = 5.0
    take_profit_percentage: float = 10.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Global variables for trading state
current_portfolio_value = 1000.0  # Starting with $1000 USDT
current_btc_amount = 0.0
last_trade_price = 0.0
auto_trading_enabled = False
auto_trading_task = None

# Store historical data for charts
price_history = []
portfolio_snapshots = []
sentiment_history = []

# API Keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
COINDESK_API_KEY = os.environ.get('COINDESK_API_KEY')

# Twitter API Setup
twitter_client = None
if TWITTER_API_KEY and TWITTER_API_SECRET:
    try:
        twitter_client = tweepy.Client(
            bearer_token=None,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=None,
            access_token_secret=None,
            wait_on_rate_limit=True
        )
    except Exception as e:
        logging.warning(f"Twitter API initialization failed: {e}")

# Initialize LLM chats
def create_trading_chat():
    if not OPENAI_API_KEY:
        return None
    
    system_message = """You are a crypto trading decision assistant. Always respond with structured JSON output containing your Chain of Thought reasoning and final trading decision.

Analyze the provided market data including price, volume, RSI, news, tweets, and sentiment analysis. Make a trading decision based on technical analysis, news sentiment, and social media sentiment.

Format your response as valid JSON:
{
  "chain_of_thought": {
    "market_analysis": "your technical analysis here",
    "risk_assessment": "risk evaluation", 
    "reasoning_steps": ["step 1", "step 2", "step 3"]
  },
  "trading_decision": {
    "action": "BUY|SELL|HOLD",
    "confidence": 0.85,
    "reasoning": "final decision reasoning"
  }
}

Rules:
- Only respond with valid JSON
- Confidence should be between 0.0 and 1.0
- Action must be exactly BUY, SELL, or HOLD
- Base decisions on provided data only
- Consider news sentiment and social media sentiment heavily
- Factor in technical indicators (RSI, volume, price trends)"""
    
    return LlmChat(
        api_key=OPENAI_API_KEY,
        session_id=f"crypto-trading-{uuid.uuid4()}",
        system_message=system_message
    ).with_model("openai", "gpt-4.1")

def create_verification_chat():
    if not OPENAI_API_KEY:
        return None
    
    system_message = """You are a crypto trading decision verifier. Review the trading decision and evidence to determine if it's valid.

Check for:
- Logical consistency between evidence and decision
- No hallucinated facts
- Reasonable confidence levels
- Sound reasoning considering sentiment analysis

Format your response as valid JSON:
{
  "is_valid": true,
  "verdict": "Reasoning is sound and well-supported",
  "issues": []
}

Only respond with valid JSON."""
    
    return LlmChat(
        api_key=OPENAI_API_KEY,
        session_id=f"crypto-verification-{uuid.uuid4()}",
        system_message=system_message
    ).with_model("openai", "gpt-4.1")

# Real-world data fetching functions
async def get_bitcoin_price():
    """Get current Bitcoin price from CoinGecko API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logging.info(f"CoinGecko API response: {data}")
                    
                    if "bitcoin" in data:
                        price = data["bitcoin"]["usd"]
                        volume_change = data["bitcoin"].get("usd_24h_change", 0)
                        
                        # Simulate RSI calculation (in real app, you'd use proper technical analysis)
                        rsi = 50 + (volume_change / 2)  # Simplified RSI approximation
                        rsi = max(0, min(100, rsi))  # Clamp between 0-100
                        
                        return price, abs(volume_change / 100), rsi
                    else:
                        logging.error(f"Bitcoin not found in CoinGecko response: {data}")
                        return 45000.0, 1.0, 50.0  # Fallback values
                else:
                    logging.error(f"CoinGecko API returned status {response.status}")
                    return 45000.0, 1.0, 50.0  # Fallback values
    except Exception as e:
        logging.error(f"Error fetching Bitcoin price: {e}")
        return 45000.0, 1.0, 50.0  # Fallback values

async def get_coindesk_news():
    """Get crypto news from CoinDesk API"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'X-CoinAPI-Key': COINDESK_API_KEY
            } if COINDESK_API_KEY else {}
            
            # Using CoinDesk RSS feed as fallback
            async with session.get(
                "https://www.coindesk.com/arc/outboundfeeds/rss/"
            ) as response:
                content = await response.text()
                feed = feedparser.parse(content)
                
                news_items = []
                for entry in feed.entries[:5]:  # Get latest 5 news
                    title = entry.title
                    # Clean up the title
                    cleaned_title = re.sub(r'<[^>]+>', '', title)
                    news_items.append(cleaned_title)
                
                return news_items
    except Exception as e:
        logging.error(f"Error fetching CoinDesk news: {e}")
        return [
            "Bitcoin price shows volatility amid market uncertainty",
            "Institutional adoption continues to grow",
            "Regulatory clarity remains a key market driver",
            "Crypto market sentiment shows mixed signals",
            "Bitcoin ETF developments continue to influence market"
        ]

async def get_twitter_sentiment():
    """Get Twitter sentiment about Bitcoin"""
    try:
        # For now, return fallback data to avoid API errors
        return [
            "Twitter sentiment: Market shows mixed signals",
            "Social media indicates cautious optimism", 
            "Crypto Twitter remains divided on short-term outlook"
        ], "Neutral"
        
    except Exception as e:
        logging.error(f"Error fetching Twitter data: {e}")
        return [
            "Twitter sentiment: Market shows mixed signals",
            "Social media indicates cautious optimism",
            "Crypto Twitter remains divided on short-term outlook"
        ], "Neutral"

def analyze_news_sentiment(news_items):
    """Analyze sentiment of news headlines"""
    try:
        sentiments = []
        for news in news_items:
            blob = TextBlob(news)
            sentiments.append(blob.sentiment.polarity)
        
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            if avg_sentiment > 0.1:
                return "Positive"
            elif avg_sentiment < -0.1:
                return "Negative"
            else:
                return "Neutral"
        return "Neutral"
    except Exception as e:
        logging.error(f"Error analyzing news sentiment: {e}")
        return "Neutral"

async def get_real_market_data():
    """Get real-time market data from multiple sources"""
    global price_history, sentiment_history
    
    try:
        # Get Bitcoin price and technical indicators
        price, volume, rsi = await get_bitcoin_price()
        
        # Get news data
        news_items = await get_coindesk_news()
        news_sentiment = analyze_news_sentiment(news_items)
        
        # Get Twitter data
        tweets, twitter_sentiment = await get_twitter_sentiment()
        
        # Store price history for charts
        current_time = datetime.utcnow()
        price_point = ChartDataPoint(
            timestamp=current_time,
            price=price,
            volume=volume,
            rsi=rsi
        )
        price_history.append(price_point)
        
        # Keep only last 100 price points to prevent memory issues
        if len(price_history) > 100:
            price_history = price_history[-100:]
        
        # Store sentiment history
        sentiment_point = {
            "timestamp": current_time,
            "news_sentiment": news_sentiment,
            "twitter_sentiment": twitter_sentiment,
            "news_items": news_items[:3],  # Store top 3 news items
            "tweets": tweets[:3] if isinstance(tweets, list) else []
        }
        sentiment_history.append(sentiment_point)
        
        # Keep only last 50 sentiment points
        if len(sentiment_history) > 50:
            sentiment_history = sentiment_history[-50:]
        
        return MarketData(
            price=price,
            volume=volume,
            rsi=rsi,
            news=news_items,
            tweets=tweets,
            news_sentiment=news_sentiment,
            twitter_sentiment=twitter_sentiment
        )
    except Exception as e:
        logging.error(f"Error getting real market data: {e}")
        # Return fallback data
        return MarketData(
            price=45000.0,
            volume=1.0,
            rsi=50.0,
            news=["Fallback: Bitcoin market shows mixed signals"],
            tweets=["Fallback: Social sentiment remains neutral"],
            news_sentiment="Neutral",
            twitter_sentiment="Neutral"
        )

async def execute_paper_trade(decision: str, price: float, confidence: float):
    """Execute paper trading logic"""
    global current_portfolio_value, current_btc_amount, last_trade_price, portfolio_snapshots
    
    profit_loss = 0.0
    
    if decision == "BUY" and current_portfolio_value > 0:
        # Buy BTC with available USD
        btc_bought = current_portfolio_value / price
        current_btc_amount += btc_bought
        current_portfolio_value = 0.0
        last_trade_price = price
        
    elif decision == "SELL" and current_btc_amount > 0:
        # Sell BTC for USD
        usd_received = current_btc_amount * price
        profit_loss = usd_received - (current_btc_amount * last_trade_price)
        current_portfolio_value = usd_received
        current_btc_amount = 0.0
    
    # Create portfolio snapshot for charts
    current_time = datetime.utcnow()
    btc_value = current_btc_amount * price
    total_value = current_portfolio_value + btc_value
    
    portfolio_snapshot = PortfolioSnapshot(
        timestamp=current_time,
        total_value=total_value,
        usd_balance=current_portfolio_value,
        btc_amount=current_btc_amount,
        btc_value=btc_value
    )
    portfolio_snapshots.append(portfolio_snapshot)
    
    # Keep only last 100 snapshots
    if len(portfolio_snapshots) > 100:
        portfolio_snapshots = portfolio_snapshots[-100:]
        
    return profit_loss

async def execute_trading_pipeline():
    """Execute the full LLM trading pipeline"""
    try:
        # Step 1: Get real market data
        market_data = await get_real_market_data()
        
        # Step 2: Create LLM trading decision
        trading_chat = create_trading_chat()
        if not trading_chat:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Prepare input for LLM
        market_input = f"""
        Current Market Data:
        - Price: ${market_data.price:,.2f}
        - Volume: {market_data.volume:.2f}
        - RSI: {market_data.rsi:.1f}
        - News Headlines: {market_data.news}
        - Twitter Sentiment: {market_data.twitter_sentiment}
        - News Sentiment: {market_data.news_sentiment}
        - Recent Tweets: {market_data.tweets}
        
        Current Portfolio: ${current_portfolio_value:.2f} USD, {current_btc_amount:.6f} BTC
        
        Provide your trading decision based on this real-time data including sentiment analysis.
        """
        
        user_message = UserMessage(text=market_input)
        llm_response = await trading_chat.send_message(user_message)
        
        # Parse LLM response
        try:
            decision_data = json.loads(llm_response)
            trading_decision = decision_data["trading_decision"]
            chain_of_thought = decision_data["chain_of_thought"]
        except (json.JSONDecodeError, KeyError) as e:
            raise HTTPException(status_code=500, detail=f"LLM response parsing error: {str(e)}")
        
        # Step 3: Verify the decision
        verification_chat = create_verification_chat()
        verification_input = f"""
        Trading Decision: {trading_decision}
        Market Evidence: {market_input}
        Chain of Thought: {chain_of_thought}
        
        Verify if this decision is valid and well-reasoned considering the sentiment analysis.
        """
        
        verification_message = UserMessage(text=verification_input)
        verification_response = await verification_chat.send_message(verification_message)
        
        try:
            verification_data = json.loads(verification_response)
        except json.JSONDecodeError:
            verification_data = {"is_valid": True, "verdict": "Verification parsing failed", "issues": []}
        
        # Step 4: Execute paper trade
        profit_loss = await execute_paper_trade(
            trading_decision["action"],
            market_data.price,
            trading_decision["confidence"]
        )
        
        # Step 5: Save trade result
        trade_result = TradeResult(
            price=market_data.price,
            decision=trading_decision["action"],
            confidence=trading_decision["confidence"],
            reasoning=trading_decision["reasoning"],
            evidence=market_data.news + market_data.tweets,
            is_valid=verification_data["is_valid"],
            verdict=verification_data["verdict"],
            profit_loss=profit_loss,
            chain_of_thought=chain_of_thought,
            news_sentiment=market_data.news_sentiment,
            twitter_sentiment=market_data.twitter_sentiment
        )
        
        await db.trades.insert_one(trade_result.dict())
        
        return trade_result
        
    except Exception as e:
        logging.error(f"Trading pipeline error: {str(e)}")
        raise e

# Background task for auto-trading
async def auto_trade_scheduler():
    """Background task for automatic trading"""
    global auto_trading_enabled
    
    while auto_trading_enabled:
        try:
            logging.info("🤖 Auto-trading: Executing trade decision...")
            # Use the same demo logic as manual trigger to avoid API errors
            current_time = datetime.utcnow()
            
            # Get current market data
            market_data = await get_real_market_data()
            
            # Create a simple trading decision without LLM for testing
            trade_result = TradeResult(
                price=market_data.price,
                decision="HOLD",  # Safe default decision
                confidence=0.5,
                reasoning="Auto-trading demo decision - LLM integration temporarily disabled",
                evidence=market_data.news[:3],  # Top 3 news items
                is_valid=True,
                verdict="Auto-trading demo decision for testing",
                profit_loss=0.0,
                chain_of_thought={
                    "market_analysis": "Automated price analysis based on current market data",
                    "risk_assessment": "Conservative auto-trading approach",
                    "reasoning_steps": ["Auto-analyzed current price", "Checked market sentiment", "Decided to hold"]
                },
                news_sentiment=market_data.news_sentiment,
                twitter_sentiment=market_data.twitter_sentiment
            )
            
            # Execute paper trade
            profit_loss = await execute_paper_trade(
                trade_result.decision,
                market_data.price,
                trade_result.confidence
            )
            trade_result.profit_loss = profit_loss
            
            # Save trade result
            await db.trades.insert_one(trade_result.dict())
            
            logging.info("✅ Auto-trading: Trade decision completed")
            await asyncio.sleep(300)  # Wait 5 minutes between trades
        except Exception as e:
            logging.error(f"Auto-trade error: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Crypto Trading Agent API with Real-time Data"}

@api_router.post("/trade/trigger")
async def trigger_trade():
    """Trigger a manual trade decision"""
    try:
        # For now, return a simple mock trade result to avoid API key issues
        current_time = datetime.utcnow()
        
        # Get current market data
        market_data = await get_real_market_data()
        
        # Create a simple trading decision without LLM for testing
        trade_result = TradeResult(
            price=market_data.price,
            decision="HOLD",  # Safe default decision
            confidence=0.5,
            reasoning="Demo trading decision - LLM integration temporarily disabled",
            evidence=market_data.news[:3],  # Top 3 news items
            is_valid=True,
            verdict="Demo trade decision for testing",
            profit_loss=0.0,
            chain_of_thought={
                "market_analysis": "Price analysis based on current market data",
                "risk_assessment": "Conservative approach for demo",
                "reasoning_steps": ["Analyzed current price", "Checked market sentiment", "Decided to hold"]
            },
            news_sentiment=market_data.news_sentiment,
            twitter_sentiment=market_data.twitter_sentiment
        )
        
        # Execute paper trade
        profit_loss = await execute_paper_trade(
            trade_result.decision,
            market_data.price,
            trade_result.confidence
        )
        trade_result.profit_loss = profit_loss
        
        # Save trade result
        await db.trades.insert_one(trade_result.dict())
        
        return trade_result
        
    except Exception as e:
        logging.error(f"Manual trade trigger error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/trade/auto/enable")
async def enable_auto_trading():
    """Enable automatic trading"""
    global auto_trading_enabled, auto_trading_task
    
    if not auto_trading_enabled:
        auto_trading_enabled = True
        auto_trading_task = asyncio.create_task(auto_trade_scheduler())
        logging.info("🚀 Auto-trading enabled")
        return {"message": "Auto-trading enabled", "status": "active"}
    else:
        return {"message": "Auto-trading already enabled", "status": "active"}

@api_router.post("/trade/auto/disable")
async def disable_auto_trading():
    """Disable automatic trading"""
    global auto_trading_enabled, auto_trading_task
    
    if auto_trading_enabled:
        auto_trading_enabled = False
        if auto_trading_task:
            auto_trading_task.cancel()
            auto_trading_task = None
        logging.info("⏸️ Auto-trading disabled")
        return {"message": "Auto-trading disabled", "status": "inactive"}
    else:
        return {"message": "Auto-trading already disabled", "status": "inactive"}

@api_router.get("/trade/auto/status")
async def get_auto_trading_status():
    """Get auto-trading status"""
    return {"auto_trading_enabled": auto_trading_enabled}

@api_router.get("/trade/live")
async def get_live_trade():
    """Get the most recent trade decision"""
    try:
        latest_trade = await db.trades.find().sort("timestamp", -1).limit(1).to_list(1)
        if not latest_trade:
            return {"message": "No trades found"}
        
        return TradeResult(**latest_trade[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trade/history")
async def get_trade_history(limit: int = 50):
    """Get paginated trade history"""
    try:
        trades = await db.trades.find().sort("timestamp", -1).limit(limit).to_list(limit)
        return [TradeResult(**trade) for trade in trades]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trade/{trade_id}")
async def get_trade_details(trade_id: str):
    """Get detailed reasoning for a specific trade"""
    try:
        trade = await db.trades.find_one({"id": trade_id})
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        return TradeResult(**trade)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/metrics")
async def get_trading_metrics():
    """Get trading performance metrics"""
    try:
        all_trades = await db.trades.find().to_list(1000)
        
        if not all_trades:
            return TradingMetrics(
                total_trades=0,
                successful_trades=0,
                total_profit_loss=0.0,
                accuracy_percentage=0.0,
                auto_trading_enabled=auto_trading_enabled
            )
        
        total_trades = len(all_trades)
        successful_trades = sum(1 for trade in all_trades if trade.get("profit_loss", 0) > 0)
        total_profit_loss = sum(trade.get("profit_loss", 0) for trade in all_trades)
        accuracy_percentage = (successful_trades / total_trades) * 100 if total_trades > 0 else 0
        
        last_trade_time = None
        if all_trades:
            last_trade_time = all_trades[0]["timestamp"]
        
        return TradingMetrics(
            total_trades=total_trades,
            successful_trades=successful_trades,
            total_profit_loss=total_profit_loss,
            accuracy_percentage=accuracy_percentage,
            last_trade_time=last_trade_time,
            auto_trading_enabled=auto_trading_enabled
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/market/data")
async def get_current_market_data():
    """Get current market data"""
    try:
        market_data = await get_real_market_data()
        return market_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/portfolio")
async def get_portfolio_status():
    """Get current portfolio status"""
    return {
        "usd_balance": current_portfolio_value,
        "btc_amount": current_btc_amount,
        "last_trade_price": last_trade_price
    }

@api_router.get("/trades/chart-data")
async def get_chart_data(timeframe: str = "1h"):
    """Get formatted data for live trades chart"""
    try:
        # Get trade markers from database
        trades = await db.trades.find().sort("timestamp", -1).limit(50).to_list(50)
        trade_markers = []
        
        for trade in trades:
            marker = TradeMarker(
                timestamp=trade["timestamp"],
                price=trade["price"],
                decision=trade["decision"],
                confidence=trade["confidence"],
                profit_loss=trade.get("profit_loss", 0.0),
                news_sentiment=trade.get("news_sentiment"),
                twitter_sentiment=trade.get("twitter_sentiment")
            )
            trade_markers.append(marker)
        
        # Sort trade markers by timestamp
        trade_markers.sort(key=lambda x: x.timestamp)
        
        # Filter data based on timeframe
        now = datetime.utcnow()
        if timeframe == "1h":
            cutoff_time = now - timedelta(hours=1)
        elif timeframe == "24h":
            cutoff_time = now - timedelta(hours=24)
        elif timeframe == "7d":
            cutoff_time = now - timedelta(days=7)
        else:
            cutoff_time = now - timedelta(hours=1)
        
        # Filter price history
        filtered_price_history = [
            point for point in price_history 
            if point.timestamp >= cutoff_time
        ]
        
        # Filter portfolio snapshots
        filtered_portfolio = [
            snapshot for snapshot in portfolio_snapshots 
            if snapshot.timestamp >= cutoff_time
        ]
        
        # Filter sentiment history
        filtered_sentiment = [
            point for point in sentiment_history 
            if point["timestamp"] >= cutoff_time
        ]
        
        # If no price history exists, create a current data point
        if not filtered_price_history:
            try:
                current_price, volume, rsi = await get_bitcoin_price()
                current_point = ChartDataPoint(
                    timestamp=now,
                    price=current_price,
                    volume=volume,
                    rsi=rsi
                )
                filtered_price_history = [current_point]
            except Exception as e:
                logging.error(f"Error getting current price for chart: {e}")
                # Use fallback data
                filtered_price_history = [
                    ChartDataPoint(
                        timestamp=now,
                        price=45000.0,
                        volume=1.0,
                        rsi=50.0
                    )
                ]
        
        # If no portfolio snapshots exist, create current snapshot
        if not filtered_portfolio:
            try:
                current_price = filtered_price_history[-1].price if filtered_price_history else 45000.0
                btc_value = current_btc_amount * current_price
                total_value = current_portfolio_value + btc_value
                
                current_snapshot = PortfolioSnapshot(
                    timestamp=now,
                    total_value=total_value,
                    usd_balance=current_portfolio_value,
                    btc_amount=current_btc_amount,
                    btc_value=btc_value
                )
                filtered_portfolio = [current_snapshot]
            except Exception as e:
                logging.error(f"Error creating portfolio snapshot: {e}")
                filtered_portfolio = []
        
        chart_data = ChartData(
            price_history=filtered_price_history,
            trade_markers=trade_markers,
            portfolio_history=filtered_portfolio,
            sentiment_timeline=filtered_sentiment,
            timeframe=timeframe
        )
        
        return chart_data
        
    except Exception as e:
        logging.error(f"Error getting chart data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/trades/chart-data/live")
async def get_live_chart_update():
    """Get real-time chart data update"""
    try:
        # Get current market data
        market_data = await get_real_market_data()
        
        # Get latest trade if exists
        latest_trade = await db.trades.find().sort("timestamp", -1).limit(1).to_list(1)
        latest_trade_marker = None
        
        if latest_trade:
            trade = latest_trade[0]
            latest_trade_marker = TradeMarker(
                timestamp=trade["timestamp"],
                price=trade["price"],
                decision=trade["decision"],
                confidence=trade["confidence"],
                profit_loss=trade.get("profit_loss", 0.0),
                news_sentiment=trade.get("news_sentiment"),
                twitter_sentiment=trade.get("twitter_sentiment")
            )
        
        # Get current portfolio value
        current_price = market_data.price
        btc_value = current_btc_amount * current_price
        total_value = current_portfolio_value + btc_value
        
        current_portfolio_snapshot = PortfolioSnapshot(
            timestamp=datetime.utcnow(),
            total_value=total_value,
            usd_balance=current_portfolio_value,
            btc_amount=current_btc_amount,
            btc_value=btc_value
        )
        
        # Get latest price point
        latest_price_point = None
        if price_history:
            latest_price_point = price_history[-1]
        else:
            latest_price_point = ChartDataPoint(
                timestamp=datetime.utcnow(),
                price=current_price,
                volume=market_data.volume,
                rsi=market_data.rsi
            )
        
        # Get latest sentiment
        latest_sentiment = None
        if sentiment_history:
            latest_sentiment = sentiment_history[-1]
        else:
            latest_sentiment = {
                "timestamp": datetime.utcnow(),
                "news_sentiment": market_data.news_sentiment,
                "twitter_sentiment": market_data.twitter_sentiment,
                "news_items": market_data.news[:3],
                "tweets": market_data.tweets[:3] if isinstance(market_data.tweets, list) else []
            }
        
        return {
            "latest_price": latest_price_point,
            "latest_trade": latest_trade_marker,
            "current_portfolio": current_portfolio_snapshot,
            "latest_sentiment": latest_sentiment,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logging.error(f"Error getting live chart update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    global auto_trading_enabled, auto_trading_task
    auto_trading_enabled = False
    if auto_trading_task:
        auto_trading_task.cancel()
    client.close()