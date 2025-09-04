# app/routers/agents.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

router = APIRouter(prefix="/agents", tags=["agents"])

# Initialize OpenAI client - it will be None if no key is found
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

class AgentRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gpt-3.5-turbo"
    history: Optional[List[dict]] = []

class AgentResponse(BaseModel):
    content: str
    model: str

@router.post("/chat", response_model=AgentResponse)
async def chat_agent(request: AgentRequest):
    try:
        if not client or not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
        
        # Build messages for OpenAI
        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
        
        # Add history if provided
        for msg in request.history[-10:]:  # Last 10 messages
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("content", "")})
        
        # Add current prompt
        messages.append({"role": "user", "content": request.prompt})
        
        # Call OpenAI with new client
        response = client.chat.completions.create(
            model=request.model if request.model != "claude" else "gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
        return AgentResponse(
            content=content,
            model=request.model
        )
    
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")  # This will show in your backend console
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/business/{tool_type}", response_model=AgentResponse)
async def business_agent(tool_type: str, request: AgentRequest):
    prompts = {
        "name": f"Generate 5 creative business names for: {request.prompt}",
        "plan": f"Create a brief business plan outline for: {request.prompt}",
        "pitch": f"Write a 30-second elevator pitch for: {request.prompt}",
        "slogan": f"Generate 5 catchy slogans for: {request.prompt}",
        "mission": f"Write a mission statement for: {request.prompt}"
    }
    
    if tool_type not in prompts:
        raise HTTPException(status_code=400, detail="Invalid business tool type")
    
    modified_request = AgentRequest(
        prompt=prompts[tool_type],
        model=request.model
    )
    return await chat_agent(modified_request)

@router.post("/email/{email_type}", response_model=AgentResponse)
async def email_agent(email_type: str, request: AgentRequest):
    templates = {
        "sales": "Write a professional sales email",
        "welcome": "Write a warm welcome email",
        "followup": "Write a follow-up email",
        "apology": "Write a sincere apology email",
        "newsletter": "Write an engaging newsletter email"
    }
    
    if email_type not in templates:
        raise HTTPException(status_code=400, detail="Invalid email type")
    
    modified_request = AgentRequest(
        prompt=f"{templates[email_type]} based on: {request.prompt}",
        model=request.model
    )
    return await chat_agent(modified_request)

@router.post("/social/{platform}", response_model=AgentResponse)
async def social_agent(platform: str, request: AgentRequest):
    platforms = {
        "twitter": "Write a Twitter/X post (max 280 characters)",
        "linkedin": "Write a professional LinkedIn post",
        "instagram": "Write an Instagram caption with relevant hashtags",
        "facebook": "Write a Facebook post",
        "tiktok": "Write a TikTok video caption with trending hashtags"
    }
    
    if platform not in platforms:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    modified_request = AgentRequest(
        prompt=f"{platforms[platform]} about: {request.prompt}",
        model=request.model
    )
    return await chat_agent(modified_request)

@router.post("/blog/post", response_model=AgentResponse)
async def blog_post_agent(request: AgentRequest):
    modified_request = AgentRequest(
        prompt=f"Write a blog post about: {request.prompt}",
        model=request.model
    )
    return await chat_agent(modified_request)

@router.post("/blog/outline", response_model=AgentResponse)
async def blog_outline_agent(request: AgentRequest):
    modified_request = AgentRequest(
        prompt=f"Create a detailed blog post outline for: {request.prompt}",
        model=request.model
    )
    return await chat_agent(modified_request)

@router.post("/brand/{brand_type}", response_model=AgentResponse)
async def brand_agent(brand_type: str, request: AgentRequest):
    types = {
        "slogan": "Create a brand slogan",
        "tagline": "Create a brand tagline",
        "mission": "Write a brand mission statement",
        "values": "Define brand values",
        "story": "Write a brand story"
    }
    
    if brand_type not in types:
        raise HTTPException(status_code=400, detail="Invalid brand content type")
    
    modified_request = AgentRequest(
        prompt=f"{types[brand_type]} for: {request.prompt}",
        model=request.model
    )
    return await chat_agent(modified_request)

