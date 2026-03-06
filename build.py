#!/usr/bin/env python3
import subprocess
import sys
import platform
import os

def build():
    system = platform.system().lower()
    if system == "windows":
        print("Error: Terminal Translator requires a Unix-like terminal (pty, fork).")
        print("It works on macOS, Linux, and Windows WSL.")
        print("To build for Windows, use WSL (Windows Subsystem for Linux).")
        sys.exit(1)
    print(f"Building Terminal Translator for {platform.system()} ({platform.machine()})...")

    name = "terminal-translator"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", name,
        "--console",
        "--clean",
        "--noconfirm",
        "app.py",
    ]

    hidden_imports = [
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

    for imp in hidden_imports:
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

    print(f"Running: {' '.join(cmd[:6])}...")
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        exe_path = os.path.join("dist", name)

        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\nBuild successful!")
            print(f"Executable: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            print(f"\nTo run: ./{exe_path}")
        else:
            print(f"\nBuild completed but executable not found at {exe_path}")
    else:
        print(f"\nBuild failed with exit code {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build()
