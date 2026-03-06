"""
AI Translator using OpenAI for Terminal Translation
Falls back to AI when local knowledge base doesn't have a match
"""

import os
import httpx
from typing import Optional

# Built-in API key for zero-config experience
# Users can override with their own key via OPENAI_API_KEY env var
BUILTIN_KEY = os.environ.get("EMERGENT_LLM_KEY", "sk-emergent-51225E8A31c9eCcC09")


def get_system_prompt(mode: str) -> str:
    """Get the system prompt based on user mode."""
    if mode == "beginner":
        return """You are a friendly terminal translator helping complete beginners understand command line output.

Your role is to explain terminal commands, errors, and output in extremely simple, friendly language.

Guidelines:
- Assume the user has ZERO programming or terminal experience
- Use everyday analogies (like comparing git to photo albums, folders to physical folders, etc.)
- Break down each part of the command/error and explain what it does
- Always be encouraging - errors are normal and part of learning!
- If there's an error, explain what went wrong AND how to fix it step by step
- Use simple vocabulary, avoid jargon, define any technical terms you must use
- Keep responses concise but complete (2-4 paragraphs max)

Format: Start with a brief summary, then explain key parts, end with what to do next if applicable."""
    else:
        return """You are a concise terminal translator for developers who understand basics but want quick explanations.

Guidelines:
- Assume familiarity with basic CLI concepts
- Be concise and direct - no unnecessary explanations
- Focus on the specific command/error and its implications
- Mention relevant flags, options, or alternatives
- For errors: briefly explain the cause and provide the fix

Format: 1-3 sentences max. Get to the point."""


async def translate_with_ai(text: str, mode: str = "beginner", api_key: Optional[str] = None) -> dict:
    """
    Translate terminal text using OpenAI.
    Uses built-in key for zero-config, can be overridden.
    """
    key = api_key or os.environ.get("OPENAI_API_KEY") or BUILTIN_KEY
    
    if not key:
        return {
            "explanation": "No API key available. Using local knowledge base only.",
            "source": "error",
            "error": True
        }
    
    try:
        # Use emergent integrations if available, otherwise direct API call
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            chat = LlmChat(
                api_key=key,
                session_id=f"terminal-translator-{mode}",
                system_message=get_system_prompt(mode)
            ).with_model("openai", "gpt-5.2")
            
            user_message = UserMessage(
                text=f"Explain this terminal output:\n\n```\n{text}\n```"
            )
            
            response = await chat.send_message(user_message)
            
            return {
                "explanation": response,
                "source": "ai",
                "model": "gpt-5.2"
            }
            
        except ImportError:
            # Fall back to direct OpenAI API call
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [
                            {"role": "system", "content": get_system_prompt(mode)},
                            {"role": "user", "content": f"Explain this terminal output:\n\n```\n{text}\n```"}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.7
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "explanation": data["choices"][0]["message"]["content"],
                        "source": "ai",
                        "model": "gpt-4"
                    }
                else:
                    return {
                        "explanation": f"API error: {response.status_code}",
                        "source": "error",
                        "error": True
                    }
                    
    except Exception as e:
        error_message = str(e)
        if "401" in error_message or "unauthorized" in error_message.lower():
            return {
                "explanation": "API key invalid. Set OPENAI_API_KEY environment variable with a valid key.",
                "source": "error",
                "error": True
            }
        return {
            "explanation": f"Translation error: {error_message}",
            "source": "error",
            "error": True
        }


def translate_sync(text: str, mode: str = "beginner") -> dict:
    """Synchronous wrapper for translate_with_ai"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(translate_with_ai(text, mode))
