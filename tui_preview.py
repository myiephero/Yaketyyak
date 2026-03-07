from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Terminal Translator — UI Preview</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'JetBrains Mono', monospace;
    font-size: 13px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.theme-switch {
    position: fixed; top: 12px; right: 16px; z-index: 100;
    display: flex; gap: 8px;
}
.theme-switch button {
    padding: 6px 14px; border-radius: 6px; border: 1px solid;
    font-family: inherit; font-size: 12px; cursor: pointer;
    transition: all 0.2s;
}

/* ── TERMINAL THEME ── */
.terminal { background: #0a0e17; color: #e2e8f0; }

.terminal .header {
    background: #0a0e17; color: #10b981; text-align: center;
    padding: 4px; font-weight: bold; border-bottom: 1px solid #1e293b;
}

.terminal .main { display: flex; flex: 1; min-height: 0; }

.terminal .panel {
    flex: 1; display: flex; flex-direction: column;
    border: 2px solid #10b981; margin: 2px;
}
.terminal .panel-title {
    background: #10b981; color: #0a0e17;
    text-align: center; padding: 2px; font-weight: bold; font-size: 12px;
}
.terminal .panel-content {
    flex: 1; overflow-y: auto; padding: 8px 12px;
    background: #0a0e17; color: #e2e8f0;
}
.terminal .shell-input-row {
    border-top: 2px solid #10b981; background: #111827;
    padding: 8px 12px; color: #64748b;
}
.terminal .shell-input-row input {
    width: 100%; background: transparent; border: none; outline: none;
    color: #e2e8f0; font-family: inherit; font-size: 13px;
}
.terminal .settings-bar {
    background: #111827; padding: 4px 12px;
    display: flex; align-items: center; gap: 12px;
    font-size: 12px; color: #94a3b8;
    border-top: 1px solid #1e293b;
}
.terminal .settings-bar .accent { color: #10b981; }
.terminal .settings-bar .dim { color: #64748b; }
.terminal .settings-bar select {
    background: #1e293b; color: #e2e8f0; border: 1px solid #334155;
    border-radius: 4px; padding: 2px 6px; font-family: inherit; font-size: 12px;
}
.terminal .footer {
    background: #111827; color: #64748b; text-align: center;
    padding: 3px; font-size: 11px; border-top: 1px solid #1e293b;
}

.terminal .theme-switch button {
    background: #111827; color: #10b981; border-color: #10b981;
}
.terminal .theme-switch button:hover { background: #10b981; color: #0a0e17; }
.terminal .theme-switch button.active { background: #10b981; color: #0a0e17; }

/* Shell output styling */
.terminal .prompt { color: #10b981; }
.terminal .cmd { color: #e2e8f0; font-weight: bold; }
.terminal .output { color: #94a3b8; }
.terminal .dir { color: #60a5fa; }
.terminal .file { color: #e2e8f0; }

/* Translation styling */
.terminal .welcome-title { color: #10b981; font-weight: bold; }
.terminal .bold { font-weight: bold; color: #e2e8f0; }
.terminal .cyan { color: #22d3ee; font-weight: bold; }
.terminal .dimmed { color: #64748b; }
.terminal .yellow { color: #facc15; }
.terminal .green { color: #10b981; }

/* ── GLASS THEME ── */
.glass { background: #0f0a2e; color: #c7d2fe; }

.glass .header {
    background: #0f0a2e; color: #a78bfa; text-align: center;
    padding: 4px; font-weight: bold; border-bottom: 1px solid #2e1065;
}

.glass .main { display: flex; flex: 1; min-height: 0; }

.glass .panel {
    flex: 1; display: flex; flex-direction: column;
    border: 2px solid #6366f1; border-radius: 12px; margin: 4px;
}
.glass .shell-panel { border-color: #6366f1; }
.glass .trans-panel { border-color: #818cf8; }

.glass .panel-title.shell-title {
    background: #4f46e5; color: #e0e7ff;
    text-align: center; padding: 2px; font-weight: bold; font-size: 12px;
    border-radius: 10px 10px 0 0;
}
.glass .panel-title.trans-title {
    background: #6366f1; color: #e0e7ff;
    text-align: center; padding: 2px; font-weight: bold; font-size: 12px;
    border-radius: 10px 10px 0 0;
}
.glass .panel-content {
    flex: 1; overflow-y: auto; padding: 8px 12px;
    background: #0f0a2e; color: #c7d2fe;
}
.glass .shell-input-row {
    border-top: 2px solid #818cf8; background: #1a1545;
    padding: 8px 12px; border-radius: 0 0 10px 10px;
}
.glass .shell-input-row input {
    width: 100%; background: transparent; border: none; outline: none;
    color: #e0e7ff; font-family: inherit; font-size: 13px;
}
.glass .settings-bar {
    background: #1a1545; padding: 4px 12px;
    display: flex; align-items: center; gap: 12px;
    font-size: 12px; color: #a5b4fc;
    border-top: 1px solid #2e1065;
}
.glass .settings-bar .accent { color: #a78bfa; }
.glass .settings-bar .dim { color: #6366f1; }
.glass .settings-bar select {
    background: #2e1065; color: #e0e7ff; border: 1px solid #4c1d95;
    border-radius: 4px; padding: 2px 6px; font-family: inherit; font-size: 12px;
}
.glass .footer {
    background: #1a1545; color: #6366f1; text-align: center;
    padding: 3px; font-size: 11px; border-top: 1px solid #2e1065;
}

.glass .theme-switch button {
    background: #1a1545; color: #a78bfa; border-color: #6366f1;
}
.glass .theme-switch button:hover { background: #6366f1; color: #e0e7ff; }
.glass .theme-switch button.active { background: #6366f1; color: #e0e7ff; }

/* Shell output styling */
.glass .prompt { color: #818cf8; }
.glass .cmd { color: #e0e7ff; font-weight: bold; }
.glass .output { color: #a5b4fc; }
.glass .dir { color: #a78bfa; }
.glass .file { color: #c7d2fe; }

/* Translation styling */
.glass .welcome-title { color: #a78bfa; font-weight: bold; }
.glass .bold { font-weight: bold; color: #e0e7ff; }
.glass .cyan { color: #67e8f9; font-weight: bold; }
.glass .dimmed { color: #6366f1; }
.glass .yellow { color: #fbbf24; }
.glass .green { color: #a78bfa; }

/* ── Scrollbar ── */
.panel-content::-webkit-scrollbar { width: 6px; }
.panel-content::-webkit-scrollbar-track { background: transparent; }
.terminal .panel-content::-webkit-scrollbar-thumb { background: #10b981; border-radius: 3px; }
.glass .panel-content::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 3px; }

.line { line-height: 1.6; white-space: pre-wrap; }
.spacer { height: 8px; }
</style>
</head>
<body class="terminal" id="app">

<div class="theme-switch">
    <button class="active" onclick="setTheme('terminal')">Terminal</button>
    <button onclick="setTheme('glass')">Glass</button>
</div>

<div class="header">Terminal Translator</div>

<div class="main">
    <div class="panel shell-panel">
        <div class="panel-title shell-title">SHELL</div>
        <div class="panel-content" id="shell-content">
            <div class="line"><span class="prompt">~ $</span> <span class="cmd">ls -la</span></div>
            <div class="line"><span class="output">total 48</span></div>
            <div class="line"><span class="output">drwxr-xr-x  8 user staff   256 Mar  6 21:04 <span class="dir">.</span></span></div>
            <div class="line"><span class="output">drwxr-xr-x  5 user staff   160 Mar  1 10:22 <span class="dir">..</span></span></div>
            <div class="line"><span class="output">-rw-r--r--  1 user staff  2048 Mar  6 21:04 <span class="file">app.py</span></span></div>
            <div class="line"><span class="output">-rw-r--r--  1 user staff   512 Mar  5 14:30 <span class="file">build.py</span></span></div>
            <div class="line"><span class="output">drwxr-xr-x  3 user staff    96 Mar  4 09:15 <span class="dir">src/</span></span></div>
            <div class="line"><span class="output">-rw-r--r--  1 user staff  1024 Mar  6 20:11 <span class="file">README.md</span></span></div>
            <div class="spacer"></div>
            <div class="line"><span class="prompt">~ $</span> <span class="cmd">git status</span></div>
            <div class="line"><span class="output">On branch main</span></div>
            <div class="line"><span class="output">Changes not staged for commit:</span></div>
            <div class="line"><span class="output">  modified:   app.py</span></div>
            <div class="line"><span class="output">  modified:   themes.py</span></div>
            <div class="spacer"></div>
            <div class="line"><span class="prompt">~ $</span> <span class="cmd">whoami</span></div>
            <div class="line"><span class="output">user</span></div>
            <div class="spacer"></div>
            <div class="line"><span class="prompt">~ $</span> <span class="cmd">pwd</span></div>
            <div class="line"><span class="output">/Users/user/projects/terminal-translator</span></div>
        </div>
        <div class="shell-input-row">
            <input type="text" placeholder="Type a command, /git <url>, or 'help'" readonly>
        </div>
    </div>

    <div class="panel trans-panel">
        <div class="panel-title trans-title">TRANSLATION</div>
        <div class="panel-content" id="trans-content">
            <div class="line"><span class="welcome-title">Welcome to Terminal Translator!</span></div>
            <div class="spacer"></div>
            <div class="line">This tool explains everything that happens in your</div>
            <div class="line">terminal, in plain language. No experience needed!</div>
            <div class="spacer"></div>
            <div class="line"><span class="bold">Get started:</span></div>
            <div class="line">  Type <span class="cyan">try 1</span> to run your first command</div>
            <div class="line">  Type <span class="cyan">/git owner/repo</span> to analyze a GitHub repo</div>
            <div class="line">  Type <span class="cyan">help</span> for full instructions</div>
            <div class="spacer"></div>
            <div class="line"><span class="bold">Try these yourself:</span></div>
            <div class="line">  <span class="cyan">1.</span> <span class="bold">ls</span> — List files in current folder</div>
            <div class="line">  <span class="cyan">2.</span> <span class="bold">pwd</span> — Print working directory</div>
            <div class="line">  <span class="cyan">3.</span> <span class="bold">whoami</span> — Show your username</div>
            <div class="line">  <span class="cyan">4.</span> <span class="bold">date</span> — Show current date and time</div>
            <div class="line">  <span class="cyan">5.</span> <span class="bold">echo "Hello!"</span> — Print text to the screen</div>
            <div class="spacer"></div>
            <div class="line"><span class="dimmed">Ctrl+B: Mode  |  Ctrl+T: AI  |  Ctrl+S: Theme  |  Ctrl+L: Clear  |  Ctrl+Q: Quit</span></div>
            <div class="spacer"></div>
            <div class="line"><span class="green">AI powered by Ollama (local, private, free)</span></div>

            <div class="spacer"></div>
            <div class="line"><span class="dimmed">─────────────────────────────────────────</span></div>
            <div class="spacer"></div>

            <div class="line"><span class="bold">📂 ls -la</span></div>
            <div class="spacer"></div>
            <div class="line"><span class="bold">What this does:</span></div>
            <div class="line">Lists all files and folders in the current directory,</div>
            <div class="line">including hidden ones (starting with a dot).</div>
            <div class="spacer"></div>
            <div class="line"><span class="bold">Breaking it down:</span></div>
            <div class="line">  <span class="cyan">ls</span> — "list" — shows what's in the folder</div>
            <div class="line">  <span class="cyan">-l</span> — "long format" — shows details like size,</div>
            <div class="line">        owner, permissions, and date modified</div>
            <div class="line">  <span class="cyan">-a</span> — "all" — includes hidden files too</div>
            <div class="spacer"></div>
            <div class="line"><span class="bold">What the output means:</span></div>
            <div class="line">  <span class="dimmed">drwxr-xr-x</span> — This is a directory you can read & enter</div>
            <div class="line">  <span class="dimmed">-rw-r--r--</span> — This is a regular file you can read</div>
            <div class="line">  <span class="dimmed">user staff</span> — You own this file</div>
            <div class="line">  <span class="dimmed">2048</span> — File size in bytes (~2 KB)</div>
            <div class="spacer"></div>
            <div class="line"><span class="green">Source: Built-in Knowledge Base (instant)</span></div>
        </div>
    </div>
</div>

<div class="settings-bar">
    <span>Mode:</span>
    <select><option>Beginner</option><option>Familiar</option></select>
    <span>Lang:</span>
    <select><option>English</option><option>Spanish</option><option>French</option><option>German</option><option>Japanese</option><option>Chinese</option><option>Korean</option><option>Portuguese</option></select>
    <span class="accent">AI: Ollama</span>
    <span class="accent">Theme: Terminal</span>
    <span class="dim" style="margin-left:auto;">Ready</span>
</div>

<div class="footer">
    Ctrl+B Mode | Ctrl+T AI Toggle | Ctrl+S Theme | Ctrl+L Clear | Ctrl+Q Quit
</div>

<script>
function setTheme(theme) {
    document.getElementById('app').className = theme;
    document.querySelectorAll('.theme-switch button').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    var themeLabel = document.querySelector('.settings-bar .accent:nth-child(5)');
    if (themeLabel) themeLabel.textContent = 'Theme: ' + (theme === 'terminal' ? 'Terminal' : 'Glass');
}
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
