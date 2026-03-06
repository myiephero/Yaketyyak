"""
AI Translator using OpenAI GPT-5.2 for Terminal Translation
"""

import os
from typing import Optional
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()


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
- Format your response with clear sections if explaining multiple things
- Keep explanations warm and supportive - like a patient teacher

Response format:
1. Start with a brief, friendly summary (1-2 sentences)
2. Explain each component in detail
3. If it's an error: explain what went wrong and exactly how to fix it
4. End with encouragement or a helpful tip"""
    else:  # familiar mode
        return """You are a concise terminal translator for developers who understand basics but want quick explanations.

Guidelines:
- Assume familiarity with basic CLI concepts (files, directories, commands)
- Be concise and direct - no unnecessary explanations
- Focus on the specific command/error and its implications
- Mention relevant flags, options, or alternatives
- For errors: briefly explain the cause and provide the fix
- Use technical terms freely

Response format:
- Brief explanation (1-3 sentences)
- Key details or flags to note
- For errors: cause and fix"""


async def translate_with_ai(
    text: str,
    mode: str = "beginner",
    api_key: Optional[str] = None
) -> dict:
    """
    Translate terminal text using OpenAI GPT-5.2.
    
    Args:
        text: Terminal text to translate
        mode: "beginner" or "familiar"
        api_key: Optional API key override
    
    Returns:
        Dict with 'explanation' and metadata
    """
    key = api_key or os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("OPENAI_API_KEY")
    
    if not key:
        return {
            "explanation": "Error: No API key configured. Please add your OpenAI API key or Emergent LLM key in settings.",
            "source": "error",
            "error": True
        }
    
    try:
        chat = LlmChat(
            api_key=key,
            session_id=f"terminal-translator-{mode}",
            system_message=get_system_prompt(mode)
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(
            text=f"Please explain the following terminal output:\n\n```\n{text}\n```"
        )
        
        response = await chat.send_message(user_message)
        
        return {
            "explanation": response,
            "source": "ai",
            "model": "gpt-5.2"
        }
        
    except Exception as e:
        error_message = str(e)
        if "401" in error_message or "unauthorized" in error_message.lower():
            return {
                "explanation": "Authentication error: Your API key appears to be invalid. Please check your API key in settings.",
                "source": "error",
                "error": True
            }
        elif "429" in error_message or "rate" in error_message.lower():
            return {
                "explanation": "Rate limit exceeded. Please wait a moment and try again.",
                "source": "error",
                "error": True
            }
        else:
            return {
                "explanation": f"An error occurred while translating: {error_message}",
                "source": "error",
                "error": True
            }
