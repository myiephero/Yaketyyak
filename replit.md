# Terminal Translator

A web-based tool that translates terminal/CLI output into plain-language explanations, designed for new coders and "vibe coders" who find terminal output intimidating.

## Architecture

- **Streamlit web app** on port 5000
- **Two-tier translation engine**: local knowledge base first, AI fallback second
- **OpenAI integration** via Replit AI Integrations (no API key needed)

## Key Files

- `app.py` — Main Streamlit application with UI, input handling, and translation display
- `translator.py` — Translation engine with AI integration (OpenAI GPT-5 via Replit AI Integrations)
- `knowledge_base.py` — Local knowledge base with 30+ commands, 20+ error patterns, output patterns
- `terminal_knowledge_base.json` — User-editable JSON file (auto-generated on first run)
- `.streamlit/config.toml` — Streamlit server configuration

## Features

- **Beginner / Familiar modes** — Toggle explanation depth
- **Local knowledge base** — Instant pattern matching for common commands/errors
- **AI fallback** — OpenAI-powered explanations for unknown terminal text
- **8 languages** — EN, ES, FR, DE, ZH, JA, PT, KO
- **Streaming AI responses** — Real-time token display
- **Custom entries** — Users can add their own patterns to the knowledge base
- **Example snippets** — 15 pre-built examples to try
- **Translation history** — Last 10 translations tracked in session

## Dependencies

- `streamlit` — Web UI framework
- `openai` — AI API client (via Replit AI Integrations, no API key required)
