# Yakety Yak

A split-pane TUI tool that translates terminal/CLI output into plain-language explanations in real time. Built with Python's Textual framework and pty for real shell integration. Includes a landing page for downloads and supports both local AI (Ollama) and cloud AI (OpenAI). Features two switchable visual themes (Terminal and Glass).

## Architecture

- **Textual TUI** with split-pane layout (shell left, translations right)
- **Real shell** spawned via `pty` + `os.fork()` — no copy-paste needed
- **Three-tier translation**: local knowledge base → Ollama (local AI) → OpenAI (cloud AI)
- **Ollama integration**: auto-detects local Ollama with Qwen2.5-Coder model
- **Dual themes**: Terminal (hacker green) and Glass (glassmorphic purple/blue), toggled via Ctrl+S
- **Standalone app** built with PyInstaller — macOS .app bundle, Linux .desktop launcher
- **Landing page** served by Flask for downloads

## Key Files

- `app.py` — Main Textual TUI application with shell integration, welcome tutorial, starter commands, help system, theme toggle
- `themes.py` — Theme CSS definitions (Terminal + Glass), theme preference persistence to `~/.yakety-yak/preferences.json`
- `translator.py` — Translation engine: local KB → Ollama → OpenAI fallback chain; auto-detects AI backends
- `knowledge_base.py` — 507 commands, 52 error patterns, 6 output patterns; stores user KB at `~/.yakety-yak/` when bundled
- `terminal_knowledge_base.json` — User-editable JSON (auto-generated on first run)
- `build.py` — PyInstaller build script with --lite and --full modes; creates macOS .app, Linux .desktop, Ollama setup scripts
- `server.py` — Flask web server for the landing/download page
- `tui_preview.py` — Interactive UI preview with animated demo content, Git Translator view, theme toggle
- `templates/index.html` — Landing page template with animated terminal demo, theme showcase, download cards
- `static/style.css` — Landing page styles (dark theme, bento grid, glassmorphic elements)

## GitHub Repo

- **URL**: https://github.com/myiephero/Yaketyyak
- **Branch**: replit

## Themes

- **Terminal**: Dark background (#0a0e17), green accents (#10b981), sharp borders — classic hacker aesthetic
- **Glass**: Deep indigo background (#0f0a2e), purple/blue accents (#6366f1, #a78bfa), rounded borders — iOS glassmorphic aesthetic
- Toggle with Ctrl+S, preference saved to `~/.yakety-yak/preferences.json`
- Landing page showcases both themes with interactive toggle preview

## Translation Priority

1. **Local knowledge base** (instant, always works, 507 commands + 52 error patterns)
2. **Ollama** (local AI via qwen2.5-coder:1.5b, free, private, no internet)
3. **OpenAI cloud** (GPT-5 via Replit AI Integrations or OPENAI_API_KEY)

## Building

```bash
python build.py          # Both Lite and Full editions
python build.py --lite   # Lite only (~24 MB)
python build.py --full   # Full edition with Ollama setup scripts
```

### Lite Edition (~24 MB)
- App executable with 507-command knowledge base
- macOS .app bundle or Linux .desktop launcher
- Works offline, no AI required

### Full Edition (~24 MB + ~1 GB AI model)
- Everything in Lite
- Ollama setup scripts (setup-ai-mac.sh / setup-ai-linux.sh)
- Auto-installs Ollama + Qwen2.5-Coder model

## Workflows

- **TUI Preview** — `python tui_preview.py` (webview, port 5000) — interactive UI preview

## In-App Commands

- `help` — Full help/instructions
- `/git <url>` — Git Translator: analyze any GitHub repo (stars, forks, license, quality score)
- `translate <command>` — Explain a command without running it
- `try` — List 25 beginner-friendly starter commands
- `try N` — Auto-run starter command N (1-25)
- Paste any `https://github.com/owner/repo` URL — auto-detected, launches Git Translator
- `/git owner/repo` — shorthand for Git Translator

## Git Translator
- Toggle between Terminal and Git Translator views in the preview
- Paste any GitHub URL to get a full KPI analysis: stars, forks, watchers, open issues, contributors, releases
- Risk/Reward assessment with score out of 100 and verdict (Excellent/Good/Fair/Caution)
- Risk flags: no license, stale repo, archived, single contributor, many open issues, etc.
- Reward flags: actively maintained, many contributors, proper licensing, releases published, etc.

## Modes
- **Noob**: Never seen a terminal. Full hand-holding, real-world analogies, celebrates wins
- **Beginner**: Just starting out. Simple, clear, supportive explanations
- **Intermediate**: Comfortable with basics. Focused, practical, uses technical terms
- **Advanced**: Experienced dev. Terse, expert-level, edge cases and pro tips only

## Keyboard Shortcuts

- **Ctrl+B**: Cycle through modes (Noob → Beginner → Intermediate → Advanced)
- **Ctrl+T**: Toggle AI on/off
- **Ctrl+S**: Switch theme (Terminal / Glass)
- **Ctrl+L**: Clear translation panel
- **Ctrl+Q**: Quit

## Dependencies

- `textual` — TUI framework
- `pexpect` — Cross-platform pty utilities
- `openai` — AI API client (Ollama + OpenAI both use OpenAI-compatible API)
- `flask` — Landing page web server
- `pyinstaller` — Build standalone executables (dev dependency)
