# Terminal Translator

A split-pane TUI (Text User Interface) tool that translates terminal/CLI output into plain-language explanations in real time. Built with Python's Textual framework and pty for real shell integration. Distributed as a standalone app — double-click to open on macOS, installable via app menu on Linux.

## Architecture

- **Textual TUI** with split-pane layout (shell left, translations right)
- **Real shell** spawned via `pty` + `os.fork()` — no copy-paste needed
- **Two-tier translation**: local knowledge base first, AI (OpenAI) fallback second
- **OpenAI integration** via Replit AI Integrations (or user's own OPENAI_API_KEY)
- **Standalone app** built with PyInstaller — no Python installation required for end users
- **macOS .app bundle** — drag to Applications, double-click to open (launches Terminal automatically)
- **Linux .desktop launcher** — install script adds to app menu, double-click to open

## Key Files

- `app.py` — Main Textual TUI application with shell integration, pty management, UI, welcome tutorial, starter commands, and help system
- `translator.py` — Translation engine with local KB lookup and AI fallback (OpenAI GPT-5); auto-detects missing API keys and defaults AI to OFF
- `knowledge_base.py` — Local knowledge base with 79 commands, 20+ error patterns, output patterns; stores user KB at `~/.terminal-translator/knowledge_base.json` when running as executable
- `terminal_knowledge_base.json` — User-editable JSON file (auto-generated on first run)
- `build.py` — Build script: compiles PyInstaller executable + creates macOS .app bundle or Linux .desktop launcher

## How It Works

1. User types commands in the left shell pane (real bash shell via pty)
2. Shell output is captured in real-time and displayed
3. Output is debounced (0.8s) then sent to the translation engine
4. Local KB is checked first for instant matches; AI is used as fallback
5. Translation appears in the right pane automatically

## Features

- **Split-pane TUI**: Real shell on left, live translations on right
- **No copy-paste**: Commands run in a real shell, output captured automatically via pty
- **Welcome tutorial**: Guided introduction on launch with 5 suggested commands
- **25 starter commands**: Type `try` to see list, `try N` to auto-run one
- **Built-in help**: Type `help` for full instructions
- **Beginner / Familiar modes** (Ctrl+B to toggle)
- **AI toggle** (Ctrl+T) — disable AI for offline/local-only use
- **Clear translations** (Ctrl+L) — clear the translation panel
- **8 languages** for AI translations: EN, ES, FR, DE, ZH, JA, PT, KO
- **79 commands** and **20+ error patterns** in local knowledge base
- **Debounced translation** — waits for output to settle before translating
- **Cross-platform** — works on macOS, Linux, Windows WSL
- **Double-click to open** — macOS .app bundle and Linux .desktop launcher

## Building

```bash
python build.py
```

On macOS: produces `dist/Terminal Translator.app` — drag to Applications, double-click to open
On Linux: produces `dist/linux-package/` — run `./install.sh` to add to app menu
Both: also produces `dist/terminal-translator` standalone executable (~24 MB)

## Distribution (End User Flow)

**macOS:**
1. Download `Terminal Translator.app`
2. Drag to Applications folder
3. Double-click to open — Terminal.app launches automatically with the tool running

**Linux:**
1. Download the linux-package folder
2. Run `./install.sh`
3. Find "Terminal Translator" in your app menu, or run `terminal-translator` from any terminal

## In-App Commands

- `help` — Show full help/instructions
- `try` — Show all 25 beginner-friendly starter commands
- `try N` — Auto-run starter command number N (1-25)

## Keyboard Shortcuts

- **Ctrl+B**: Toggle Beginner/Familiar mode
- **Ctrl+T**: Toggle AI on/off
- **Ctrl+L**: Clear translation panel
- **Ctrl+Q**: Quit

## Dependencies

- `textual` — TUI framework
- `pexpect` — Cross-platform pty utilities
- `openai` — AI API client (via Replit AI Integrations or OPENAI_API_KEY)
- `pyinstaller` — Build standalone executables (dev dependency)

## Running (Development)

```bash
python app.py
```

The app runs as a console TUI, not a web server.
