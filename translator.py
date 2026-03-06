import os
from openai import OpenAI
from knowledge_base import local_lookup, ensure_knowledge_base_exists

AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

client = OpenAI(
    api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
    base_url=AI_INTEGRATIONS_OPENAI_BASE_URL,
)

SYSTEM_PROMPTS = {
    "beginner": (
        "You are a friendly, patient terminal translator that explains terminal/CLI output "
        "to absolute beginners who have never used a command line before. "
        "Explain everything in simple, everyday language. Use analogies to things people "
        "already understand (like file cabinets, mailboxes, etc.). "
        "Break down each part of the output. Never assume the user knows any technical terms "
        "without explaining them. If there's an error, explain what went wrong, why it happened, "
        "and exactly what steps to take to fix it. Be encouraging and reassuring. "
        "Keep your response concise but thorough \u2014 aim for 3\u20138 sentences. "
        "Do NOT use markdown formatting (no headers, bold, bullets) \u2014 use plain text only."
    ),
    "familiar": (
        "You are a concise terminal translator for users who have basic CLI knowledge. "
        "Explain terminal output efficiently without over-explaining basic concepts. "
        "Focus on: what happened, why, and actionable next steps. "
        "For errors, provide the likely cause and the fix. Use technical terms freely "
        "but clarify anything unusual. Include relevant flags, options, or alternative "
        "commands when helpful. Keep responses focused, 2\u20135 sentences. "
        "Do NOT use markdown formatting (no headers, bold, bullets) \u2014 use plain text only."
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


def translate_with_ai(terminal_text, mode="beginner", language="en"):
    system_prompt = get_system_prompt(mode, language)
    user_prompt = f"Explain this terminal output:\n\n{terminal_text}"

    # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
    # do not change this unless explicitly requested by the user
    response = client.chat.completions.create(
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
        try:
            ai_explanation = translate_with_ai(terminal_text, mode, language)
            return {
                "source": "ai",
                "category": "ai_analysis",
                "explanation": ai_explanation,
            }
        except Exception as e:
            return {
                "source": "error",
                "category": "error",
                "explanation": f"AI translation failed: {e}",
            }

    return {
        "source": "none",
        "category": "unknown",
        "explanation": "No local match found and AI translation is disabled.",
    }
