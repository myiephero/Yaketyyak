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
    "beginner": {
        "en": (
            "You are a friendly, patient terminal translator that explains terminal/CLI output "
            "to absolute beginners who have never used a command line before. "
            "Explain everything in simple, everyday language. Use analogies to things people "
            "already understand (like file cabinets, mailboxes, etc.). "
            "Break down each part of the output. Never assume the user knows any technical terms "
            "without explaining them. If there's an error, explain what went wrong, why it happened, "
            "and exactly what steps to take to fix it. Be encouraging and reassuring. "
            "Format your response with clear sections using markdown."
        ),
        "es": (
            "Eres un traductor de terminal amigable y paciente que explica la salida de terminal/CLI "
            "a principiantes absolutos que nunca han usado una línea de comandos. "
            "Explica todo en un lenguaje simple y cotidiano. Usa analogías con cosas que la gente "
            "ya entiende. Desglosa cada parte de la salida. Nunca asumas que el usuario conoce "
            "términos técnicos sin explicarlos. Si hay un error, explica qué salió mal, por qué "
            "sucedió y exactamente qué pasos seguir para solucionarlo. Sé alentador y tranquilizador. "
            "Formatea tu respuesta con secciones claras usando markdown."
        ),
        "fr": (
            "Vous êtes un traducteur de terminal amical et patient qui explique les sorties "
            "terminal/CLI aux débutants absolus. Expliquez tout dans un langage simple et quotidien. "
            "Utilisez des analogies. Décomposez chaque partie. N'assumez jamais que l'utilisateur "
            "connaît des termes techniques. En cas d'erreur, expliquez ce qui s'est passé, pourquoi, "
            "et les étapes exactes pour corriger. Soyez encourageant. Formatez en markdown."
        ),
        "de": (
            "Du bist ein freundlicher, geduldiger Terminal-Übersetzer, der Terminal/CLI-Ausgaben "
            "für absolute Anfänger erklärt. Erkläre alles in einfacher Alltagssprache. Verwende "
            "Analogien. Zerlege jeden Teil. Nimm nie an, dass der Benutzer technische Begriffe kennt. "
            "Bei Fehlern erkläre, was schiefgelaufen ist, warum und welche Schritte zur Behebung nötig "
            "sind. Sei ermutigend. Formatiere mit Markdown."
        ),
        "zh": (
            "你是一个友好、耐心的终端翻译器，为从未使用过命令行的初学者解释终端/CLI输出。"
            "用简单日常的语言解释一切。使用人们已经理解的类比。分解输出的每个部分。"
            "永远不要假设用户了解任何技术术语而不加解释。如果有错误，解释出了什么问题、"
            "为什么会发生以及修复的确切步骤。要鼓励和安慰。使用markdown格式化你的回复。"
        ),
        "ja": (
            "あなたはフレンドリーで忍耐強いターミナル翻訳者です。コマンドラインを使ったことのない"
            "初心者にターミナル/CLIの出力を説明します。すべてを簡単な日常言語で説明してください。"
            "身近なものに例えてください。出力の各部分を分解してください。技術用語を説明なしに"
            "使用しないでください。エラーの場合は、何が間違っていたか、なぜ起きたか、"
            "修正手順を正確に説明してください。励まし、安心させてください。マークダウンで書式設定してください。"
        ),
        "pt": (
            "Você é um tradutor de terminal amigável e paciente que explica saídas de terminal/CLI "
            "para iniciantes absolutos. Explique tudo em linguagem simples e cotidiana. "
            "Use analogias. Divida cada parte da saída. Nunca assuma que o usuário conhece termos "
            "técnicos sem explicá-los. Se houver erro, explique o que deu errado, por que aconteceu "
            "e exatamente quais passos seguir. Seja encorajador. Formate com markdown."
        ),
        "ko": (
            "당신은 친절하고 인내심 있는 터미널 번역기입니다. 명령줄을 한 번도 사용한 적 없는 "
            "초보자에게 터미널/CLI 출력을 설명합니다. 모든 것을 간단한 일상 언어로 설명하세요. "
            "비유를 사용하세요. 출력의 각 부분을 분석하세요. 기술 용어를 설명 없이 사용하지 마세요. "
            "오류가 있으면 무엇이 잘못되었는지, 왜 발생했는지, 수정 단계를 정확히 설명하세요. "
            "격려하고 안심시켜 주세요. 마크다운으로 형식을 지정하세요."
        ),
    },
    "familiar": {
        "en": (
            "You are a concise terminal translator for users who have basic CLI knowledge. "
            "Explain terminal output efficiently without over-explaining basic concepts. "
            "Focus on: what happened, why, and actionable next steps. "
            "For errors, provide the likely cause and the fix. Use technical terms freely "
            "but clarify anything unusual. Include relevant flags, options, or alternative "
            "commands when helpful. Keep responses focused and scannable with markdown formatting."
        ),
        "es": (
            "Eres un traductor de terminal conciso para usuarios con conocimientos básicos de CLI. "
            "Explica la salida del terminal de manera eficiente. Enfócate en: qué pasó, por qué "
            "y los próximos pasos. Para errores, proporciona la causa probable y la solución. "
            "Usa términos técnicos libremente. Incluye flags y comandos alternativos cuando sea útil. "
            "Mantén las respuestas enfocadas con formato markdown."
        ),
        "fr": (
            "Vous êtes un traducteur de terminal concis pour les utilisateurs ayant des connaissances "
            "CLI de base. Expliquez efficacement. Concentrez-vous sur: ce qui s'est passé, pourquoi, "
            "et les prochaines étapes. Pour les erreurs, donnez la cause probable et la correction. "
            "Utilisez librement les termes techniques. Incluez les flags pertinents. Formatez en markdown."
        ),
        "de": (
            "Du bist ein prägnanter Terminal-Übersetzer für Benutzer mit CLI-Grundkenntnissen. "
            "Erkläre Terminal-Ausgaben effizient. Fokus auf: was passiert ist, warum, und nächste "
            "Schritte. Bei Fehlern die wahrscheinliche Ursache und Lösung angeben. Technische Begriffe "
            "frei verwenden. Relevante Flags und Alternativen einbeziehen. Markdown-Formatierung."
        ),
        "zh": (
            "你是一个简洁的终端翻译器，面向有基本CLI知识的用户。高效解释终端输出。"
            "重点关注：发生了什么、为什么以及可执行的下一步。对于错误，提供可能的原因和修复方法。"
            "自由使用技术术语。在有帮助时包含相关标志、选项或替代命令。使用markdown格式化。"
        ),
        "ja": (
            "あなたは基本的なCLI知識を持つユーザー向けの簡潔なターミナル翻訳者です。"
            "効率的に説明してください。焦点：何が起きたか、なぜ、次のステップ。"
            "エラーには原因と修正方法を。技術用語は自由に使用。関連フラグや代替コマンドを含めてください。"
            "マークダウンで書式設定。"
        ),
        "pt": (
            "Você é um tradutor de terminal conciso para usuários com conhecimentos básicos de CLI. "
            "Explique de forma eficiente. Foco em: o que aconteceu, por que e próximos passos. "
            "Para erros, forneça causa provável e correção. Use termos técnicos livremente. "
            "Inclua flags e alternativas relevantes. Formate com markdown."
        ),
        "ko": (
            "당신은 기본 CLI 지식을 가진 사용자를 위한 간결한 터미널 번역기입니다. "
            "효율적으로 설명하세요. 초점: 무슨 일이 있었는지, 왜, 다음 단계. "
            "오류에는 원인과 수정 방법을 제공하세요. 기술 용어를 자유롭게 사용하세요. "
            "관련 플래그와 대안을 포함하세요. 마크다운으로 형식을 지정하세요."
        ),
    },
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


def get_system_prompt(mode, language):
    mode_prompts = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["beginner"])
    return mode_prompts.get(language, mode_prompts["en"])


def translate_with_ai(terminal_text, mode="beginner", language="en"):
    system_prompt = get_system_prompt(mode, language)

    lang_name = LANGUAGE_NAMES.get(language, "English")
    if language != "en":
        system_prompt += f"\n\nIMPORTANT: Respond entirely in {lang_name}."

    user_prompt = f"Please explain the following terminal output:\n\n```\n{terminal_text}\n```"

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


def translate_with_ai_stream(terminal_text, mode="beginner", language="en"):
    system_prompt = get_system_prompt(mode, language)

    lang_name = LANGUAGE_NAMES.get(language, "English")
    if language != "en":
        system_prompt += f"\n\nIMPORTANT: Respond entirely in {lang_name}."

    user_prompt = f"Please explain the following terminal output:\n\n```\n{terminal_text}\n```"

    # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
    # do not change this unless explicitly requested by the user
    stream = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=8192,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def translate(terminal_text, mode="beginner", language="en", use_ai=True):
    kb = ensure_knowledge_base_exists()

    local_result = local_lookup(terminal_text, kb, mode)

    if local_result:
        return local_result

    if use_ai:
        ai_explanation = translate_with_ai(terminal_text, mode, language)
        return {
            "source": "ai",
            "category": "ai_analysis",
            "explanation": ai_explanation,
        }

    return {
        "source": "none",
        "category": "unknown",
        "explanation": "No local match found and AI translation is disabled.",
    }
