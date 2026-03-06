#!/bin/bash
echo "Uninstalling Terminal Translator..."

rm -f "$HOME/.local/bin/terminal-translator"
rm -f "$HOME/.local/share/applications/terminal-translator.desktop"
rm -rf "$HOME/.terminal-translator"

echo "Uninstalled successfully!"
