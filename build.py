#!/usr/bin/env python3
import subprocess
import sys
import platform
import os
import shutil
import stat
import plistlib


APP_NAME = "Terminal Translator"
EXECUTABLE_NAME = "terminal-translator"
BUNDLE_ID = "com.terminaltranslator.app"
VERSION = "1.0.0"

HIDDEN_IMPORTS = [
    "textual",
    "textual.app",
    "textual.widgets",
    "textual.containers",
    "textual.binding",
    "textual.reactive",
    "textual.message",
    "textual._xterm_parser",
    "textual.css",
    "textual.css.query",
    "textual.css.stylesheet",
    "textual.dom",
    "textual.screen",
    "textual.widget",
    "textual.driver",
    "textual.drivers",
    "textual.drivers.linux_driver",
    "textual._linux_driver",
    "textual._animator",
    "textual._timer",
    "textual._worker_manager",
    "textual.worker",
    "textual.events",
    "textual.geometry",
    "textual.strip",
    "textual.renderables",
    "textual.renderables.gradient",
    "textual.widgets._header",
    "textual.widgets._footer",
    "textual.widgets._static",
    "textual.widgets._input",
    "textual.widgets._label",
    "textual.widgets._select",
    "textual.widgets._rich_log",
    "rich",
    "rich.text",
    "rich.console",
    "rich.markup",
    "rich.segment",
    "rich.style",
    "rich.color",
    "rich.terminal_theme",
    "openai",
    "pexpect",
    "translator",
    "knowledge_base",
]


def build_executable():
    system = platform.system().lower()
    if system == "windows":
        print("Error: Terminal Translator requires a Unix-like terminal (pty, fork).")
        print("It works on macOS, Linux, and Windows WSL.")
        print("To build for Windows, use WSL (Windows Subsystem for Linux).")
        sys.exit(1)

    print(f"Building Terminal Translator for {platform.system()} ({platform.machine()})...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", EXECUTABLE_NAME,
        "--console",
        "--clean",
        "--noconfirm",
        "app.py",
    ]

    for imp in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", imp])

    textual_path = None
    try:
        import textual as _t
        textual_path = os.path.dirname(_t.__file__)
    except ImportError:
        pass

    if textual_path:
        css_dir = os.path.join(textual_path, "css")
        if os.path.isdir(css_dir):
            cmd.extend(["--add-data", f"{css_dir}{os.pathsep}textual/css"])

    print("Compiling executable...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    exe_path = os.path.join("dist", EXECUTABLE_NAME)
    if result.returncode != 0 or not os.path.exists(exe_path):
        print("Build failed!")
        print(result.stderr[-2000:] if result.stderr else "No error output")
        sys.exit(1)

    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"Executable built: {exe_path} ({size_mb:.1f} MB)")
    return exe_path


def create_macos_app(exe_path):
    print("\nCreating macOS app bundle...")

    app_dir = os.path.join("dist", f"{APP_NAME}.app")
    contents_dir = os.path.join(app_dir, "Contents")
    macos_dir = os.path.join(contents_dir, "MacOS")
    resources_dir = os.path.join(contents_dir, "Resources")

    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)

    os.makedirs(macos_dir)
    os.makedirs(resources_dir)

    shutil.copy2(exe_path, os.path.join(macos_dir, EXECUTABLE_NAME))

    launcher_path = os.path.join(macos_dir, "launcher")
    with open(launcher_path, "w") as f:
        f.write(f"""#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
EXEC="$DIR/{EXECUTABLE_NAME}"

if [ -t 0 ] && [ -t 1 ]; then
    exec "$EXEC"
else
    osascript -e '
        tell application "Terminal"
            activate
            do script "clear && \\"'"$EXEC"'\\" ; exit"
        end tell
    '
fi
""")
    os.chmod(launcher_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    info_plist = {
        "CFBundleName": APP_NAME,
        "CFBundleDisplayName": APP_NAME,
        "CFBundleIdentifier": BUNDLE_ID,
        "CFBundleVersion": VERSION,
        "CFBundleShortVersionString": VERSION,
        "CFBundleExecutable": "launcher",
        "CFBundlePackageType": "APPL",
        "CFBundleSignature": "????",
        "CFBundleInfoDictionaryVersion": "6.0",
        "LSMinimumSystemVersion": "10.15",
        "NSHighResolutionCapable": True,
        "LSApplicationCategoryType": "public.app-category.developer-tools",
        "NSHumanReadableCopyright": f"Terminal Translator {VERSION}",
    }

    plist_path = os.path.join(contents_dir, "Info.plist")
    with open(plist_path, "wb") as f:
        plistlib.dump(info_plist, f)

    print(f"macOS app bundle created: {app_dir}")
    print(f"  To install: drag '{APP_NAME}.app' to your Applications folder")
    print(f"  To run: double-click '{APP_NAME}' in Applications")
    return app_dir


def create_linux_launcher(exe_path):
    print("\nCreating Linux launcher...")

    launcher_dir = os.path.join("dist", "linux-package")
    bin_dir = os.path.join(launcher_dir, "bin")
    apps_dir = os.path.join(launcher_dir, "share", "applications")

    if os.path.exists(launcher_dir):
        shutil.rmtree(launcher_dir)

    os.makedirs(bin_dir)
    os.makedirs(apps_dir)

    shutil.copy2(exe_path, os.path.join(bin_dir, EXECUTABLE_NAME))

    desktop_entry = f"""[Desktop Entry]
Name={APP_NAME}
Comment=Learn the terminal with real-time command explanations
Exec={EXECUTABLE_NAME}
Terminal=true
Type=Application
Categories=Development;Education;
Keywords=terminal;cli;learn;translate;command;
StartupNotify=false
"""
    desktop_path = os.path.join(apps_dir, f"{EXECUTABLE_NAME}.desktop")
    with open(desktop_path, "w") as f:
        f.write(desktop_entry)

    install_script_path = os.path.join(launcher_dir, "install.sh")
    with open(install_script_path, "w") as f:
        f.write(f"""#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local"
BIN_DIR="$INSTALL_DIR/bin"
APPS_DIR="$INSTALL_DIR/share/applications"

echo "Installing {APP_NAME}..."
echo ""

mkdir -p "$BIN_DIR"
mkdir -p "$APPS_DIR"

cp "$SCRIPT_DIR/bin/{EXECUTABLE_NAME}" "$BIN_DIR/{EXECUTABLE_NAME}"
chmod +x "$BIN_DIR/{EXECUTABLE_NAME}"

cat > "$APPS_DIR/{EXECUTABLE_NAME}.desktop" << 'DESKTOP'
[Desktop Entry]
Name={APP_NAME}
Comment=Learn the terminal with real-time command explanations
Exec=$HOME/.local/bin/{EXECUTABLE_NAME}
Terminal=true
Type=Application
Categories=Development;Education;
Keywords=terminal;cli;learn;translate;command;
StartupNotify=false
DESKTOP

sed -i "s|\\$HOME|$HOME|g" "$APPS_DIR/{EXECUTABLE_NAME}.desktop"

echo "Installed successfully!"
echo ""
echo "You can now:"
echo "  1. Find '{APP_NAME}' in your application menu"
echo "  2. Or run it from terminal: {EXECUTABLE_NAME}"
echo ""

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Note: Add $BIN_DIR to your PATH if the command isn't found:"
    echo "  echo 'export PATH=\\\"$BIN_DIR:\\$PATH\\\"' >> ~/.bashrc"
    echo ""
fi

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi
""")
    os.chmod(install_script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    uninstall_script_path = os.path.join(launcher_dir, "uninstall.sh")
    with open(uninstall_script_path, "w") as f:
        f.write(f"""#!/bin/bash
echo "Uninstalling {APP_NAME}..."

rm -f "$HOME/.local/bin/{EXECUTABLE_NAME}"
rm -f "$HOME/.local/share/applications/{EXECUTABLE_NAME}.desktop"
rm -rf "$HOME/.terminal-translator"

echo "Uninstalled successfully!"
""")
    os.chmod(uninstall_script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    print(f"Linux package created: {launcher_dir}/")
    print(f"  To install: cd {launcher_dir} && ./install.sh")
    print(f"  To uninstall: ./uninstall.sh")
    print(f"  After install, find '{APP_NAME}' in your app menu or run: {EXECUTABLE_NAME}")
    return launcher_dir


def build():
    system = platform.system().lower()

    exe_path = build_executable()

    if system == "darwin":
        create_macos_app(exe_path)
    elif system == "linux":
        create_linux_launcher(exe_path)

    print("\n" + "=" * 50)
    print(f"BUILD COMPLETE — {APP_NAME} v{VERSION}")
    print("=" * 50)

    if system == "darwin":
        print(f"\nFor Mac users:")
        print(f"  1. Open the 'dist' folder")
        print(f"  2. Drag '{APP_NAME}.app' to Applications")
        print(f"  3. Double-click to open — it launches Terminal automatically")
    elif system == "linux":
        print(f"\nFor Linux users:")
        print(f"  1. Open a terminal in 'dist/linux-package'")
        print(f"  2. Run: ./install.sh")
        print(f"  3. Find '{APP_NAME}' in your app menu, or run: {EXECUTABLE_NAME}")

    print(f"\nStandalone executable: dist/{EXECUTABLE_NAME}")


if __name__ == "__main__":
    build()
