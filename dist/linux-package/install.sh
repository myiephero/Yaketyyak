#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local"
BIN_DIR="$INSTALL_DIR/bin"
APPS_DIR="$INSTALL_DIR/share/applications"

echo "Installing Yakety Yak..."
echo ""

mkdir -p "$BIN_DIR"
mkdir -p "$APPS_DIR"

cp "$SCRIPT_DIR/bin/yakety-yak" "$BIN_DIR/yakety-yak"
chmod +x "$BIN_DIR/yakety-yak"

cat > "$APPS_DIR/yakety-yak.desktop" << 'DESKTOP'
[Desktop Entry]
Name=Yakety Yak
Comment=Learn the terminal with real-time command explanations
Exec=$HOME/.local/bin/yakety-yak
Terminal=true
Type=Application
Categories=Development;Education;
Keywords=terminal;cli;learn;translate;command;
StartupNotify=false
DESKTOP

sed -i "s|\$HOME|$HOME|g" "$APPS_DIR/yakety-yak.desktop"

echo "Installed successfully!"
echo ""
echo "You can now:"
echo "  1. Find 'Yakety Yak' in your application menu"
echo "  2. Or run it from terminal: yakety-yak"
echo ""

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Note: Add $BIN_DIR to your PATH if the command isn't found:"
    echo "  echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.bashrc"
    echo ""
fi

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi
