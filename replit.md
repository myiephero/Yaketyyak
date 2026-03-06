# Terminal Translator

A split-pane TUI (Text User Interface) tool that translates terminal/CLI output into plain-language explanations in real time. Built with Python's Textual framework and pty for real shell integration. Distributed as a standalone executable via PyInstaller.

## Architecture

- **Textual TUI** with split-pane layout (shell left, translations right)
- **Real shell** spawned via `pty` + `os.fork()` — no copy-paste needed
- **Two-tier translation**: local knowledge base first, AI (OpenAI) fallback second
- **OpenAI integration** via Replit AI Integrations (no API key needed)
- **Standalone executable** built with PyInstaller — no Python installation required for end users

## Key Files

- `app.py` — Main Textual TUI application with shell integration, pty management, UI, welcome tutorial, starter commands, and help system
- `translator.py` — Translation engine with local KB lookup and AI fallback (OpenAI GPT-5)
- `knowledge_base.py` — Local knowledge base with 79 commands, 20+ error patterns, output patterns; stores user KB at `~/.terminal-translator/knowledge_base.json` when running as executable
- `terminal_knowledge_base.json` — User-editable JSON file (auto-generated on first run)
- `build.py` — PyInstaller build script; produces standalone executable in `dist/`

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
- **Standalone executable** — download and run, no Python needed

## Building the Executable

```bash
python build.py
```

Produces `dist/terminal-translator` (Linux/macOS) or `dist/terminal-translator.exe` (Windows). ~24 MB single file.

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
- `openai` — AI API client (via Replit AI Integrations)
- `pyinstaller` — Build standalone executables (dev dependency)

## Running

Development:
```bash
python app.py
```

Standalone:
```bash
./dist/terminal-translator
```

The app runs as a console TUI, not a web server.
