from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime, timezone

from knowledge_base import lookup, get_all_patterns, get_pattern_count
from ai_translator import translate_with_ai
from github_analyzer import analyze_repo

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Terminal Translator API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Models ====================

class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    mode: str = Field(default="beginner", pattern="^(beginner|familiar)$")


class TranslateResponse(BaseModel):
    explanation: str
    source: str  # "local" or "ai"
    matched_pattern: Optional[str] = None
    lookup_time_ms: Optional[float] = None
    model: Optional[str] = None


class GitAnalyzeRequest(BaseModel):
    url: str = Field(..., min_length=1)
    mode: str = Field(default="beginner", pattern="^(beginner|familiar)$")


class TranslationHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    explanation: str
    source: str
    mode: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SettingsUpdate(BaseModel):
    mode: Optional[str] = Field(default=None, pattern="^(beginner|familiar)$")
    language: Optional[str] = None
    api_key: Optional[str] = None


# ==================== Endpoints ====================

@api_router.get("/")
async def root():
    return {
        "message": "Terminal Translator API",
        "version": "1.0.0",
        "endpoints": {
            "translate": "/api/translate",
            "github": "/api/github/analyze",
            "knowledge_base": "/api/knowledge-base"
        }
    }


@api_router.post("/translate", response_model=TranslateResponse)
async def translate_terminal(request: TranslateRequest):
    """
    Translate terminal text to plain English.
    First checks local knowledge base, then falls back to AI.
    """
    text = request.text.strip()
    mode = request.mode
    
    # 1. Check local knowledge base first (fast lookup)
    local_result = lookup(text, mode)
    
    if local_result:
        # Save to history
        history_entry = {
            "id": str(uuid.uuid4()),
            "text": text,
            "explanation": local_result["explanation"],
            "source": "local",
            "mode": mode,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.translation_history.insert_one(history_entry)
        
        return TranslateResponse(
            explanation=local_result["explanation"],
            source="local",
            matched_pattern=local_result.get("matched_pattern"),
            lookup_time_ms=local_result.get("lookup_time_ms")
        )
    
    # 2. Fall back to AI translation
    ai_result = await translate_with_ai(text, mode)
    
    # Save to history
    history_entry = {
        "id": str(uuid.uuid4()),
        "text": text,
        "explanation": ai_result["explanation"],
        "source": ai_result.get("source", "ai"),
        "mode": mode,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.translation_history.insert_one(history_entry)
    
    if ai_result.get("error"):
        return TranslateResponse(
            explanation=ai_result["explanation"],
            source="error"
        )
    
    return TranslateResponse(
        explanation=ai_result["explanation"],
        source="ai",
        model=ai_result.get("model")
    )


@api_router.post("/github/analyze")
async def analyze_github_repo(request: GitAnalyzeRequest):
    """
    Analyze a GitHub repository and provide plain-English summary with KPIs.
    """
    result = await analyze_repo(request.url, request.mode)
    
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return result


@api_router.get("/knowledge-base")
async def get_knowledge_base():
    """
    Get all patterns in the knowledge base.
    """
    patterns = get_all_patterns()
    return {
        "total_patterns": get_pattern_count(),
        "patterns": patterns
    }


@api_router.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    """
    Get statistics about the knowledge base.
    """
    return {
        "total_patterns": get_pattern_count(),
        "categories": {
            "git": 15,
            "npm_yarn": 5,
            "python": 4,
            "docker": 4,
            "linux": 14,
            "errors": 16
        }
    }


@api_router.get("/history")
async def get_translation_history(limit: int = 20):
    """
    Get recent translation history.
    """
    history = await db.translation_history.find(
        {},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    return {"history": history}


@api_router.delete("/history")
async def clear_translation_history():
    """
    Clear all translation history.
    """
    result = await db.translation_history.delete_many({})
    return {"deleted": result.deleted_count}


@api_router.get("/settings")
async def get_settings():
    """
    Get current user settings.
    """
    settings = await db.settings.find_one({"type": "user"}, {"_id": 0})
    
    if not settings:
        # Return defaults
        return {
            "mode": "beginner",
            "language": "en",
            "has_api_key": bool(os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("OPENAI_API_KEY"))
        }
    
    return {
        "mode": settings.get("mode", "beginner"),
        "language": settings.get("language", "en"),
        "has_api_key": settings.get("has_api_key", False)
    }


@api_router.put("/settings")
async def update_settings(settings: SettingsUpdate):
    """
    Update user settings.
    """
    update_data = {}
    
    if settings.mode:
        update_data["mode"] = settings.mode
    if settings.language:
        update_data["language"] = settings.language
    if settings.api_key:
        update_data["has_api_key"] = True
        # Store API key securely (in production, use proper secret management)
        update_data["api_key"] = settings.api_key
    
    if update_data:
        await db.settings.update_one(
            {"type": "user"},
            {"$set": update_data},
            upsert=True
        )
    
    return {"success": True, "updated": list(update_data.keys())}


@api_router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "knowledge_base_patterns": get_pattern_count(),
        "ai_configured": bool(os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("OPENAI_API_KEY"))
    }


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
