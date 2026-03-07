#!/bin/bash
echo "Uninstalling Yakety Yak..."

rm -f "$HOME/.local/bin/yakety-yak"
rm -f "$HOME/.local/share/applications/yakety-yak.desktop"
rm -rf "$HOME/.yakety-yak"

echo "Uninstalled successfully!"
