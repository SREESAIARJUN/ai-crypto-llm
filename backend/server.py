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
import random

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
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TradingMetrics(BaseModel):
    total_trades: int
    successful_trades: int
    total_profit_loss: float
    accuracy_percentage: float
    last_trade_time: Optional[datetime] = None

# Global variables for trading state
current_portfolio_value = 1000.0  # Starting with $1000 USDT
current_btc_amount = 0.0
last_trade_price = 0.0

# LLM Integration Setup
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY not found in environment variables")

# Initialize LLM chats
def create_trading_chat():
    if not OPENAI_API_KEY:
        return None
    
    system_message = """You are a crypto trading decision assistant. Always respond with structured JSON output containing your Chain of Thought reasoning and final trading decision.

Analyze the provided market data including price, volume, RSI, news, and tweets. Make a trading decision based on technical analysis and sentiment.

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
- Base decisions on provided data only"""
    
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
- Sound reasoning

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

# Mock data functions (using free APIs concept)
async def get_mock_market_data():
    """Simulate real-time market data for demo purposes"""
    # In real implementation, this would fetch from CoinGecko, news APIs, etc.
    base_price = 45000 + random.randint(-5000, 5000)
    
    mock_news = [
        "Bitcoin ETF approval expected this quarter",
        "Major institutional adoption continues",
        "Market volatility increases amid regulatory concerns",
        "Whale activity detected on major exchanges",
        "DeFi integration driving new use cases"
    ]
    
    mock_tweets = [
        "Large BTC transfer to exchange wallets observed",
        "Crypto market showing strong fundamentals",
        "Technical indicators suggest trend reversal",
        "Institutional buying pressure increasing",
        "Market sentiment remains cautiously optimistic"
    ]
    
    return MarketData(
        price=base_price,
        volume=random.uniform(0.5, 2.0),
        rsi=random.randint(30, 80),
        news=random.sample(mock_news, 3),
        tweets=random.sample(mock_tweets, 3)
    )

async def execute_paper_trade(decision: str, price: float, confidence: float):
    """Execute paper trading logic"""
    global current_portfolio_value, current_btc_amount, last_trade_price
    
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
        
    return profit_loss

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Crypto Trading Agent API"}

@api_router.post("/trade/trigger")
async def trigger_trade():
    """Trigger the full LLM trading pipeline"""
    try:
        # Step 1: Get market data
        market_data = await get_mock_market_data()
        
        # Step 2: Create LLM trading decision
        trading_chat = create_trading_chat()
        if not trading_chat:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Prepare input for LLM
        market_input = f"""
        Current Market Data:
        - Price: ${market_data.price:,.2f}
        - Volume: {market_data.volume:.2f}
        - RSI: {market_data.rsi}
        - News: {market_data.news}
        - Tweets: {market_data.tweets}
        
        Current Portfolio: ${current_portfolio_value:.2f} USD, {current_btc_amount:.6f} BTC
        
        Provide your trading decision based on this data.
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
        
        Verify if this decision is valid and well-reasoned.
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
            chain_of_thought=chain_of_thought
        )
        
        await db.trades.insert_one(trade_result.dict())
        
        return trade_result
        
    except Exception as e:
        logging.error(f"Trading pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
                accuracy_percentage=0.0
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
            last_trade_time=last_trade_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/market/data")
async def get_current_market_data():
    """Get current market data"""
    try:
        market_data = await get_mock_market_data()
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

# Background task for auto-trading (can be enabled later)
async def auto_trade_scheduler():
    """Background task for automatic trading (currently disabled)"""
    while True:
        try:
            # await trigger_trade()  # Uncomment to enable auto-trading
            await asyncio.sleep(300)  # Wait 5 minutes between trades
        except Exception as e:
            logging.error(f"Auto-trade error: {str(e)}")
            await asyncio.sleep(60)

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
    client.close()