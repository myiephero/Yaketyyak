#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local"
BIN_DIR="$INSTALL_DIR/bin"
APPS_DIR="$INSTALL_DIR/share/applications"

echo "Installing Terminal Translator..."
echo ""

mkdir -p "$BIN_DIR"
mkdir -p "$APPS_DIR"

cp "$SCRIPT_DIR/bin/terminal-translator" "$BIN_DIR/terminal-translator"
chmod +x "$BIN_DIR/terminal-translator"

cat > "$APPS_DIR/terminal-translator.desktop" << 'DESKTOP'
[Desktop Entry]
Name=Terminal Translator
Comment=Learn the terminal with real-time command explanations
Exec=$HOME/.local/bin/terminal-translator
Terminal=true
Type=Application
Categories=Development;Education;
Keywords=terminal;cli;learn;translate;command;
StartupNotify=false
DESKTOP

sed -i "s|\$HOME|$HOME|g" "$APPS_DIR/terminal-translator.desktop"

echo "Installed successfully!"
echo ""
echo "You can now:"
echo "  1. Find 'Terminal Translator' in your application menu"
echo "  2. Or run it from terminal: terminal-translator"
echo ""

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Note: Add $BIN_DIR to your PATH if the command isn't found:"
    echo "  echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.bashrc"
    echo ""
fi

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi
