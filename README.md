# YakkityYak - Terminal Translator

**Google Translate for your Terminal** — A split-pane app that shows real-time, plain-English explanations as you use the command line.

![YakkityYak Screenshot](https://raw.githubusercontent.com/myiephero/yakkityyak/main/screenshot.png)

## Download

Download the latest release for your operating system:

| OS | Download |
|----|----------|
| **macOS** | [TerminalTranslator-macos](https://github.com/myiephero/yakkityyak/releases/latest/download/TerminalTranslator-macos) |
| **Windows** | [TerminalTranslator-windows.exe](https://github.com/myiephero/yakkityyak/releases/latest/download/TerminalTranslator-windows.exe) |
| **Linux** | [TerminalTranslator-linux](https://github.com/myiephero/yakkityyak/releases/latest/download/TerminalTranslator-linux) |

## Features

- **Real Terminal Integration** — Not a copy-paste tool. A real shell runs inside.
- **76+ Built-in Patterns** — Instant explanations for git, npm, python, docker, and common errors
- **AI Fallback** — GPT-5.2 steps in when the knowledge base doesn't know something
- **Beginner & Familiar Modes** — Toggle between detailed explanations or concise summaries
- **Zero Configuration** — Download, open, and start learning. No API keys needed.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+B` | Toggle Beginner/Familiar mode |
| `Ctrl+T` | Toggle translation panel |
| `Ctrl+L` | Clear terminal |
| `Ctrl+Q` | Quit |

## For Developers

### Install via pip

```bash
pip install terminal-translator
termtranslate
```

### Run from source

```bash
git clone https://github.com/myiephero/yakkityyak.git
cd yakkityyak
pip install -e .
python -m terminal_translator
```

## How It Works

1. Type commands in the left pane (real shell)
2. Translations appear instantly in the right pane
3. Local knowledge base handles common patterns (<0.03ms)
4. AI fills in gaps for unknown commands

## License

MIT — Free and open source.
