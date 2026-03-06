import os
import urllib.request
import json
from knowledge_base import local_lookup, ensure_knowledge_base_exists

AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:1.5b")


def _check_ollama():
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                data = json.loads(resp.read())
                models = [m.get("name", "") for m in data.get("models", [])]
                return True, models
    except Exception:
        pass
    return False, []


OLLAMA_RUNNING, OLLAMA_MODELS = _check_ollama()
OLLAMA_MODEL_READY = any(OLLAMA_MODEL in m for m in OLLAMA_MODELS)

CLOUD_AI_AVAILABLE = bool(AI_INTEGRATIONS_OPENAI_API_KEY or OPENAI_API_KEY)
AI_AVAILABLE = OLLAMA_RUNNING or CLOUD_AI_AVAILABLE

cloud_client = None
if CLOUD_AI_AVAILABLE:
    from openai import OpenAI
    cloud_client = OpenAI(
        api_key=AI_INTEGRATIONS_OPENAI_API_KEY or OPENAI_API_KEY,
        base_url=AI_INTEGRATIONS_OPENAI_BASE_URL or None,
    )

ollama_client = None
if OLLAMA_RUNNING:
    from openai import OpenAI as OllamaClient
    ollama_client = OllamaClient(
        api_key="ollama",
        base_url=f"{OLLAMA_HOST}/v1",
    )


def get_ai_status():
    if OLLAMA_MODEL_READY:
        return "ollama_ready", f"Ollama ({OLLAMA_MODEL})"
    if OLLAMA_RUNNING:
        return "ollama_no_model", f"Ollama running (model {OLLAMA_MODEL} not installed)"
    if CLOUD_AI_AVAILABLE:
        return "cloud", "Cloud AI (OpenAI)"
    return "none", "No AI available"


SYSTEM_PROMPTS = {
    "beginner": (
        "You are a friendly, patient terminal translator that explains terminal/CLI output "
        "to absolute beginners who have never used a command line before. "
        "Explain everything in simple, everyday language. Use analogies to things people "
        "already understand (like file cabinets, mailboxes, etc.). "
        "Break down each part of the output. Never assume the user knows any technical terms "
        "without explaining them. If there's an error, explain what went wrong, why it happened, "
        "and exactly what steps to take to fix it. Be encouraging and reassuring. "
        "Keep your response concise but thorough — aim for 3–8 sentences. "
        "Do NOT use markdown formatting (no headers, bold, bullets) — use plain text only."
    ),
    "familiar": (
        "You are a concise terminal translator for users who have basic CLI knowledge. "
        "Explain terminal output efficiently without over-explaining basic concepts. "
        "Focus on: what happened, why, and actionable next steps. "
        "For errors, provide the likely cause and the fix. Use technical terms freely "
        "but clarify anything unusual. Include relevant flags, options, or alternative "
        "commands when helpful. Keep responses focused, 2–5 sentences. "
        "Do NOT use markdown formatting (no headers, bold, bullets) — use plain text only."
    ),
}

LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "pt": "Portuguese",
    "ko": "Korean",
}


def get_system_prompt(mode, language="en"):
    prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["beginner"])
    if language != "en":
        lang_name = LANGUAGE_NAMES.get(language, "English")
        prompt += f"\n\nIMPORTANT: Respond entirely in {lang_name}."
    return prompt


def translate_with_ollama(terminal_text, mode="beginner", language="en"):
    if ollama_client is None:
        raise RuntimeError("Ollama is not running.")

    system_prompt = get_system_prompt(mode, language)
    user_prompt = f"Explain this terminal output:\n\n{terminal_text}"

    response = ollama_client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=2048,
    )

    return response.choices[0].message.content or ""


def translate_with_cloud(terminal_text, mode="beginner", language="en"):
    if cloud_client is None:
        raise RuntimeError(
            "No API key found. Set OPENAI_API_KEY environment variable to enable cloud AI translations."
        )

    system_prompt = get_system_prompt(mode, language)
    user_prompt = f"Explain this terminal output:\n\n{terminal_text}"

    response = cloud_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=8192,
    )

    return response.choices[0].message.content or ""


def translate(terminal_text, mode="beginner", language="en", use_ai=True):
    kb = ensure_knowledge_base_exists()
    local_result = local_lookup(terminal_text, kb, mode)

    if local_result:
        return local_result

    if use_ai:
        if OLLAMA_MODEL_READY and ollama_client:
            try:
                explanation = translate_with_ollama(terminal_text, mode, language)
                return {
                    "source": "ai",
                    "category": "ollama",
                    "explanation": explanation,
                }
            except Exception:
                pass

        if cloud_client:
            try:
                explanation = translate_with_cloud(terminal_text, mode, language)
                return {
                    "source": "ai",
                    "category": "cloud_ai",
                    "explanation": explanation,
                }
            except Exception as e:
                return {
                    "source": "error",
                    "category": "error",
                    "explanation": f"AI translation failed: {e}",
                }

        return {
            "source": "error",
            "category": "error",
            "explanation": "No AI backend available. Install Ollama or set OPENAI_API_KEY for AI translations.",
        }

    return {
        "source": "none",
        "category": "unknown",
        "explanation": "No local match found and AI translation is disabled.",
    }
