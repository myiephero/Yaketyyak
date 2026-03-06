# Terminal Translator

A "Google Translate for your Terminal" - a split-pane TUI that shows real-time plain-English explanations as you use the command line.

## Features

- **Split-pane interface**: Real shell on the left, live translations on the right
- **70+ built-in patterns**: Instant explanations for common commands and errors
- **AI fallback**: GPT-5.2 powered explanations for unknown patterns
- **Beginner/Familiar modes**: Toggle between detailed or concise explanations
- **Zero config**: Works out of the box, no API keys required

## Installation

### Download (Recommended for beginners)

Download from [GitHub Releases](https://github.com/myiephero/yakkityyak/releases/latest):

- **macOS**: `TerminalTranslator-macos`
- **Windows**: `TerminalTranslator-windows.exe`
- **Linux**: `TerminalTranslator-linux`

### Install via pip (For developers)

```bash
pip install terminal-translator
termtranslate
```

## Usage

Launch the app and start typing commands. The right pane automatically shows explanations for:
- Commands you type
- Output from programs
- Error messages

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+B` | Toggle Beginner/Familiar mode |
| `Ctrl+T` | Toggle translation panel |
| `Ctrl+Q` | Quit |
| `Ctrl+L` | Clear terminal |

## Development

```bash
# Clone the repo
git clone https://github.com/myiephero/yakkityyak.git
cd yakkityyak

# Install dependencies
pip install -e ".[dev]"

# Run locally
python -m terminal_translator
```

## Building Binaries

Binaries are automatically built via GitHub Actions on each release. To build manually:

```bash
# macOS
pyinstaller terminal_translator.spec

# Windows
pyinstaller terminal_translator.spec

# Linux
pyinstaller terminal_translator.spec
```

## License

MIT
