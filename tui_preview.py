from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Terminal Translator — UI Preview</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
    --ease: cubic-bezier(0.4, 0, 0.2, 1);
    --transition: 0.35s var(--ease);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'JetBrains Mono', 'SF Mono', monospace;
    font-size: 12.5px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transition: background var(--transition), color var(--transition);
}

/* ═══════════════════════════════════════════
   THEME TOGGLE (preview only)
   ═══════════════════════════════════════════ */
.theme-switch {
    position: fixed; top: 10px; right: 14px; z-index: 100;
    display: flex; gap: 0;
    background: rgba(0,0,0,0.4);
    border-radius: 8px; padding: 3px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
}
.theme-switch button {
    padding: 5px 14px; border-radius: 6px; border: none;
    font-family: inherit; font-size: 11px; cursor: pointer;
    transition: all 0.25s var(--ease);
    background: transparent; color: rgba(255,255,255,0.5);
    font-weight: 500; letter-spacing: 0.3px;
}
.theme-switch button.active {
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

/* ═══════════════════════════════════════════
   HEADER
   ═══════════════════════════════════════════ */
.header {
    text-align: center; padding: 6px 0; font-weight: 600;
    font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase;
    transition: all var(--transition);
    position: relative;
}
.header::after {
    content: ''; position: absolute; bottom: 0; left: 10%; right: 10%;
    height: 1px; transition: background var(--transition);
}

/* ═══════════════════════════════════════════
   MAIN LAYOUT
   ═══════════════════════════════════════════ */
.main {
    display: flex; flex: 1; min-height: 0;
    padding: 6px; gap: 6px;
}

.panel {
    flex: 1; display: flex; flex-direction: column;
    border-radius: 10px; overflow: hidden;
    transition: all var(--transition);
    position: relative;
}
.panel.focus-glow {
    z-index: 1;
}

.panel-title {
    text-align: center; padding: 5px 0; font-weight: 600;
    font-size: 10.5px; letter-spacing: 2px; text-transform: uppercase;
    transition: all var(--transition);
    position: relative;
}

.panel-content {
    flex: 1; overflow-y: auto; padding: 10px 14px;
    transition: all var(--transition);
    scroll-behavior: smooth;
}

/* Scroll indicator */
.panel-content-wrap { position: relative; flex: 1; display: flex; flex-direction: column; min-height: 0; }
.scroll-fade {
    position: absolute; bottom: 0; left: 0; right: 0; height: 32px;
    pointer-events: none; z-index: 2;
    opacity: 0; transition: opacity 0.3s;
}
.scroll-fade.visible { opacity: 1; }

/* ═══════════════════════════════════════════
   SHELL INPUT
   ═══════════════════════════════════════════ */
.shell-input-row {
    padding: 8px 14px; display: flex; align-items: center; gap: 8px;
    transition: all var(--transition);
}
.input-prompt {
    font-weight: 600; font-size: 12px; flex-shrink: 0;
    transition: color var(--transition);
}
.shell-input-row input {
    width: 100%; background: transparent; border: none; outline: none;
    font-family: inherit; font-size: 12.5px;
    transition: color var(--transition);
}
.cursor-blink {
    display: inline-block; width: 8px; height: 15px;
    animation: blink 1s step-end infinite;
    vertical-align: text-bottom; margin-left: 2px;
    transition: background var(--transition);
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

/* ═══════════════════════════════════════════
   SETTINGS BAR
   ═══════════════════════════════════════════ */
.settings-bar {
    padding: 5px 14px;
    display: flex; align-items: center; gap: 10px;
    font-size: 11px; font-weight: 400;
    transition: all var(--transition);
}
.settings-bar .s-label { opacity: 0.5; font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.5px; }
.settings-bar select {
    border-radius: 5px; padding: 3px 8px;
    font-family: inherit; font-size: 11px;
    transition: all var(--transition); cursor: pointer;
    -webkit-appearance: none; appearance: none;
}
.ai-badge {
    display: flex; align-items: center; gap: 5px;
    padding: 2px 10px; border-radius: 20px;
    font-size: 10.5px; font-weight: 600;
    transition: all var(--transition);
}
.ai-dot {
    width: 6px; height: 6px; border-radius: 50%;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}
.s-spacer { flex: 1; }

/* ═══════════════════════════════════════════
   FOOTER
   ═══════════════════════════════════════════ */
.footer {
    text-align: center; padding: 5px 0;
    font-size: 11px; letter-spacing: 0.3px;
    transition: all var(--transition);
    display: flex; justify-content: center; gap: 8px;
}
.footer .kbd {
    padding: 2px 6px; border-radius: 3px;
    font-size: 10px; font-weight: 600;
    transition: all var(--transition);
}

/* ═══════════════════════════════════════════
   CONTENT LINES
   ═══════════════════════════════════════════ */
.line {
    line-height: 1.7; white-space: pre-wrap;
    transition: color var(--transition);
}
.spacer { height: 6px; }

/* Translation section cards */
.trans-section {
    border-radius: 8px; padding: 10px 12px; margin: 6px 0;
    transition: all var(--transition);
}
.trans-section-title {
    font-size: 10px; text-transform: uppercase; letter-spacing: 1px;
    font-weight: 600; margin-bottom: 6px;
    display: flex; align-items: center; gap: 6px;
}
.trans-section-title .icon { font-size: 13px; }

.source-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 20px;
    font-size: 10px; font-weight: 600;
    transition: all var(--transition);
}
.source-badge .dot {
    width: 5px; height: 5px; border-radius: 50%;
}

/* Command header in translation */
.cmd-header {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 12px; border-radius: 8px; margin: 6px 0;
    transition: all var(--transition);
}
.cmd-header-icon { font-size: 18px; }
.cmd-header-text { font-weight: 700; font-size: 14px; letter-spacing: 0.3px; }

/* Shell line numbers */
.shell-line {
    display: flex; gap: 0; line-height: 1.7;
}
.line-num {
    width: 28px; text-align: right; padding-right: 8px;
    font-size: 10px; opacity: 0.25; flex-shrink: 0;
    user-select: none; line-height: 1.7;
}
.line-content { flex: 1; white-space: pre-wrap; }

/* ═══════════════════════════════════════════
   TERMINAL THEME
   ═══════════════════════════════════════════ */
.terminal {
    background: #060a13;
    color: #e2e8f0;
}
.terminal .header {
    background: #060a13; color: #10b981;
}
.terminal .header::after {
    background: linear-gradient(90deg, transparent, #10b98140, transparent);
}

.terminal .panel {
    border: 1px solid #10b98130;
    background: #0a0e17;
    box-shadow: 0 0 0 1px #10b98108;
}
.terminal .panel.focus-glow {
    box-shadow: 0 0 20px #10b98115, 0 0 0 1px #10b98125;
}
.terminal .panel-title {
    background: linear-gradient(135deg, #10b981, #059669);
    color: #0a0e17;
}
.terminal .panel-content { background: #0a0e17; color: #cbd5e1; }
.terminal .scroll-fade { background: linear-gradient(transparent, #0a0e17); }

.terminal .shell-input-row {
    background: #0d1420; border-top: 1px solid #10b98120;
}
.terminal .input-prompt { color: #10b981; }
.terminal .shell-input-row input { color: #e2e8f0; }
.terminal .shell-input-row input::placeholder { color: #475569; }
.terminal .cursor-blink { background: #10b981; }

.terminal .settings-bar {
    background: #0b1019; color: #94a3b8;
    border-top: 1px solid #1e293b40;
}
.terminal .settings-bar select {
    background: #131b2e; color: #e2e8f0; border: 1px solid #1e293b;
}
.terminal .ai-badge { background: #10b98118; color: #10b981; }
.terminal .ai-dot { background: #10b981; box-shadow: 0 0 6px #10b981; }

.terminal .footer {
    background: #060a13; color: #475569;
    border-top: 1px solid #1e293b30;
}
.terminal .footer .kbd {
    background: #131b2e; color: #64748b; border: 1px solid #1e293b;
}

.terminal .theme-switch button.active {
    background: #10b981; color: #0a0e17;
}

.terminal .prompt { color: #10b981; font-weight: 600; }
.terminal .cmd { color: #f1f5f9; font-weight: 600; }
.terminal .output { color: #7c8ca3; }
.terminal .dir { color: #38bdf8; }
.terminal .file { color: #cbd5e1; }

.terminal .welcome-title { color: #10b981; font-weight: 700; font-size: 14px; }
.terminal .bold { font-weight: 600; color: #e2e8f0; }
.terminal .cyan { color: #22d3ee; font-weight: 600; }
.terminal .dimmed { color: #475569; }
.terminal .yellow { color: #facc15; }
.terminal .green { color: #10b981; }

.terminal .trans-section {
    background: #0d1420; border: 1px solid #1e293b40;
}
.terminal .trans-section-title { color: #10b981; }
.terminal .cmd-header {
    background: linear-gradient(135deg, #10b98112, #10b98108);
    border: 1px solid #10b98120;
}
.terminal .cmd-header-text { color: #10b981; }
.terminal .source-badge { background: #10b98115; color: #10b981; }
.terminal .source-badge .dot { background: #10b981; }

.terminal .panel-content::-webkit-scrollbar { width: 5px; }
.terminal .panel-content::-webkit-scrollbar-track { background: transparent; }
.terminal .panel-content::-webkit-scrollbar-thumb { background: #10b98140; border-radius: 3px; }
.terminal .panel-content::-webkit-scrollbar-thumb:hover { background: #10b98170; }

/* ═══════════════════════════════════════════
   GLASS THEME
   ═══════════════════════════════════════════ */
.glass {
    background: #080518;
    background-image:
        radial-gradient(ellipse at 20% 50%, #6366f108 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, #a78bfa06 0%, transparent 50%),
        radial-gradient(ellipse at 50% 80%, #818cf805 0%, transparent 50%);
    color: #c7d2fe;
}
.glass .header {
    background: transparent; color: #a78bfa;
}
.glass .header::after {
    background: linear-gradient(90deg, transparent, #a78bfa30, transparent);
}

.glass .panel {
    border: 1px solid #6366f130;
    background: rgba(15, 10, 46, 0.7);
    backdrop-filter: blur(16px);
    box-shadow: 0 4px 24px rgba(99, 102, 241, 0.06);
    border-radius: 14px;
}
.glass .panel.focus-glow {
    box-shadow: 0 0 30px #6366f115, 0 4px 24px rgba(99, 102, 241, 0.1), inset 0 1px 0 #818cf815;
}
.glass .shell-panel { border-color: #6366f125; }
.glass .trans-panel { border-color: #818cf825; }

.glass .panel-title {
    background: linear-gradient(135deg, #4f46e5cc, #6366f1cc);
    color: #e0e7ff; backdrop-filter: blur(8px);
}
.glass .panel-title.trans-title {
    background: linear-gradient(135deg, #6366f1cc, #818cf8cc);
}
.glass .panel-content { background: transparent; color: #c7d2fe; }
.glass .scroll-fade { background: linear-gradient(transparent, #0f0a2e); }

.glass .shell-input-row {
    background: rgba(26, 21, 69, 0.6); border-top: 1px solid #818cf820;
    backdrop-filter: blur(8px);
}
.glass .input-prompt { color: #818cf8; }
.glass .shell-input-row input { color: #e0e7ff; }
.glass .shell-input-row input::placeholder { color: #4c1d95; }
.glass .cursor-blink { background: #818cf8; }

.glass .settings-bar {
    background: rgba(26, 21, 69, 0.5); color: #a5b4fc;
    border-top: 1px solid #6366f115;
    backdrop-filter: blur(8px);
}
.glass .settings-bar select {
    background: rgba(46, 16, 101, 0.5); color: #e0e7ff;
    border: 1px solid #6366f130;
}
.glass .ai-badge { background: #a78bfa18; color: #a78bfa; }
.glass .ai-dot { background: #a78bfa; box-shadow: 0 0 6px #a78bfa; }

.glass .footer {
    background: rgba(8, 5, 24, 0.8); color: #6366f1;
    border-top: 1px solid #6366f115;
}
.glass .footer .kbd {
    background: rgba(99, 102, 241, 0.1); color: #818cf8;
    border: 1px solid #6366f125;
}

.glass .theme-switch button.active {
    background: linear-gradient(135deg, #6366f1, #818cf8); color: #e0e7ff;
}

.glass .prompt { color: #818cf8; font-weight: 600; }
.glass .cmd { color: #e0e7ff; font-weight: 600; }
.glass .output { color: #8b92c7; }
.glass .dir { color: #a78bfa; }
.glass .file { color: #c7d2fe; }

.glass .welcome-title { color: #a78bfa; font-weight: 700; font-size: 14px; }
.glass .bold { font-weight: 600; color: #e0e7ff; }
.glass .cyan { color: #67e8f9; font-weight: 600; }
.glass .dimmed { color: #7c6bbf; }
.glass .yellow { color: #fbbf24; }
.glass .green { color: #a78bfa; }

.glass .trans-section {
    background: rgba(99, 102, 241, 0.06);
    border: 1px solid #6366f118;
    backdrop-filter: blur(4px);
}
.glass .trans-section-title { color: #a78bfa; }
.glass .cmd-header {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(129, 140, 248, 0.06));
    border: 1px solid #6366f120;
}
.glass .cmd-header-text { color: #a78bfa; }
.glass .source-badge { background: #a78bfa15; color: #a78bfa; }
.glass .source-badge .dot { background: #a78bfa; }

.glass .panel-content::-webkit-scrollbar { width: 5px; }
.glass .panel-content::-webkit-scrollbar-track { background: transparent; }
.glass .panel-content::-webkit-scrollbar-thumb { background: #6366f140; border-radius: 3px; }
.glass .panel-content::-webkit-scrollbar-thumb:hover { background: #6366f170; }

/* ═══════════════════════════════════════════
   ANIMATIONS
   ═══════════════════════════════════════════ */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-in {
    animation: fadeSlideUp 0.4s var(--ease) both;
}
.animate-in:nth-child(1) { animation-delay: 0s; }
.animate-in:nth-child(2) { animation-delay: 0.05s; }
.animate-in:nth-child(3) { animation-delay: 0.1s; }
.animate-in:nth-child(4) { animation-delay: 0.15s; }
.animate-in:nth-child(5) { animation-delay: 0.2s; }
.animate-in:nth-child(6) { animation-delay: 0.25s; }
.animate-in:nth-child(7) { animation-delay: 0.3s; }
.animate-in:nth-child(8) { animation-delay: 0.35s; }
.animate-in:nth-child(9) { animation-delay: 0.4s; }
.animate-in:nth-child(10) { animation-delay: 0.45s; }

/* Theme transition on panels */
.panel, .panel-title, .panel-content, .shell-input-row,
.settings-bar, .footer, .header, .cmd-header, .trans-section,
.ai-badge, .source-badge {
    transition: all var(--transition);
}

@media (max-width: 700px) {
    .main { flex-direction: column; }
    .panel { min-height: 40vh; }
    .settings-bar { flex-wrap: wrap; gap: 6px; }
    .footer { flex-wrap: wrap; gap: 4px; font-size: 10px; }
    .theme-switch { top: 6px; right: 8px; }
}
</style>
</head>
<body class="terminal" id="app">

<div class="theme-switch">
    <button class="active" id="btn-terminal" onclick="setTheme('terminal')">Terminal</button>
    <button id="btn-glass" onclick="setTheme('glass')">Glass</button>
</div>

<div class="header">Terminal Translator</div>

<div class="main">
    <!-- SHELL PANEL -->
    <div class="panel shell-panel focus-glow">
        <div class="panel-title shell-title">SHELL</div>
        <div class="panel-content-wrap">
            <div class="panel-content" id="shell-content">
                <div class="shell-line animate-in"><span class="line-num">1</span><span class="line-content"><span class="prompt">~ $</span> <span class="cmd">ls -la</span></span></div>
                <div class="shell-line animate-in"><span class="line-num">2</span><span class="line-content"><span class="output">total 48</span></span></div>
                <div class="shell-line animate-in"><span class="line-num">3</span><span class="line-content"><span class="output">drwxr-xr-x  8 user staff   256 Mar  6 21:04 <span class="dir">.</span></span></span></div>
                <div class="shell-line animate-in"><span class="line-num">4</span><span class="line-content"><span class="output">drwxr-xr-x  5 user staff   160 Mar  1 10:22 <span class="dir">..</span></span></span></div>
                <div class="shell-line animate-in"><span class="line-num">5</span><span class="line-content"><span class="output">-rw-r--r--  1 user staff  2048 Mar  6 21:04 <span class="file">app.py</span></span></span></div>
                <div class="shell-line animate-in"><span class="line-num">6</span><span class="line-content"><span class="output">-rw-r--r--  1 user staff   512 Mar  5 14:30 <span class="file">build.py</span></span></span></div>
                <div class="shell-line animate-in"><span class="line-num">7</span><span class="line-content"><span class="output">drwxr-xr-x  3 user staff    96 Mar  4 09:15 <span class="dir">src/</span></span></span></div>
                <div class="shell-line animate-in"><span class="line-num">8</span><span class="line-content"><span class="output">-rw-r--r--  1 user staff  1024 Mar  6 20:11 <span class="file">README.md</span></span></span></div>
                <div class="spacer"></div>
                <div class="shell-line animate-in"><span class="line-num">9</span><span class="line-content"><span class="prompt">~ $</span> <span class="cmd">git status</span></span></div>
                <div class="shell-line animate-in"><span class="line-num">10</span><span class="line-content"><span class="output">On branch main</span></span></div>
                <div class="shell-line animate-in"><span class="line-num">11</span><span class="line-content"><span class="output">Changes not staged for commit:</span></span></div>
                <div class="shell-line animate-in"><span class="line-num">12</span><span class="line-content"><span class="output">  modified:   <span class="file">app.py</span></span></span></div>
                <div class="shell-line animate-in"><span class="line-num">13</span><span class="line-content"><span class="output">  modified:   <span class="file">themes.py</span></span></span></div>
                <div class="spacer"></div>
                <div class="shell-line animate-in"><span class="line-num">14</span><span class="line-content"><span class="prompt">~ $</span> <span class="cmd">whoami</span></span></div>
                <div class="shell-line animate-in"><span class="line-num">15</span><span class="line-content"><span class="output">user</span></span></div>
                <div class="spacer"></div>
                <div class="shell-line animate-in"><span class="line-num">16</span><span class="line-content"><span class="prompt">~ $</span> <span class="cmd">pwd</span></span></div>
                <div class="shell-line animate-in"><span class="line-num">17</span><span class="line-content"><span class="output">/Users/user/projects/terminal-translator</span></span></div>
            </div>
            <div class="scroll-fade" id="shell-scroll-fade"></div>
        </div>
        <div class="shell-input-row">
            <span class="input-prompt">~$</span>
            <input type="text" placeholder="Type a command, /git <url>, or 'help'" readonly>
            <span class="cursor-blink"></span>
        </div>
    </div>

    <!-- TRANSLATION PANEL -->
    <div class="panel trans-panel">
        <div class="panel-title trans-title">TRANSLATION</div>
        <div class="panel-content-wrap">
            <div class="panel-content" id="trans-content">
                <div class="line animate-in"><span class="welcome-title">Welcome to Terminal Translator</span></div>
                <div class="spacer"></div>
                <div class="line animate-in">This tool explains everything that happens in your</div>
                <div class="line animate-in">terminal, in plain language. No experience needed!</div>
                <div class="spacer"></div>
                <div class="line animate-in"><span class="bold">Get started:</span></div>
                <div class="line animate-in">  Type <span class="cyan">try 1</span> to run your first command</div>
                <div class="line animate-in">  Type <span class="cyan">/git owner/repo</span> to analyze a GitHub repo</div>
                <div class="line animate-in">  Type <span class="cyan">help</span> for full instructions</div>
                <div class="spacer"></div>

                <div class="line animate-in"><span class="bold">Quick start:</span></div>
                <div class="line animate-in">  <span class="cyan">1.</span> <span class="bold">ls</span> <span class="dimmed">—</span> List files in current folder</div>
                <div class="line animate-in">  <span class="cyan">2.</span> <span class="bold">pwd</span> <span class="dimmed">—</span> Print working directory</div>
                <div class="line animate-in">  <span class="cyan">3.</span> <span class="bold">whoami</span> <span class="dimmed">—</span> Show your username</div>
                <div class="line animate-in">  <span class="cyan">4.</span> <span class="bold">date</span> <span class="dimmed">—</span> Show current date and time</div>
                <div class="line animate-in">  <span class="cyan">5.</span> <span class="bold">echo "Hello!"</span> <span class="dimmed">—</span> Print text to the screen</div>
                <div class="spacer"></div>

                <!-- SEPARATOR -->
                <div style="height:1px;margin:8px 0;opacity:0.15;background:currentColor;"></div>

                <!-- COMMAND EXPLANATION -->
                <div class="cmd-header animate-in">
                    <span class="cmd-header-icon">&#128194;</span>
                    <span class="cmd-header-text">ls -la</span>
                </div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128161;</span> What this does</div>
                    <div class="line">Lists all files and folders in the current directory,</div>
                    <div class="line">including hidden ones (starting with a dot).</div>
                </div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128268;</span> Breaking it down</div>
                    <div class="line">  <span class="cyan">ls</span> <span class="dimmed">—</span> "list" — shows what's in the folder</div>
                    <div class="line">  <span class="cyan">-l</span> <span class="dimmed">—</span> "long format" — details like size, owner,</div>
                    <div class="line">       permissions, and date modified</div>
                    <div class="line">  <span class="cyan">-a</span> <span class="dimmed">—</span> "all" — includes hidden files too</div>
                </div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128203;</span> Reading the output</div>
                    <div class="line">  <span class="dimmed">drwxr-xr-x</span>  Directory you can read & enter</div>
                    <div class="line">  <span class="dimmed">-rw-r--r--</span>  Regular file you can read</div>
                    <div class="line">  <span class="dimmed">user staff</span>  You own this file</div>
                    <div class="line">  <span class="dimmed">2048</span>        File size in bytes (~2 KB)</div>
                </div>

                <div style="margin-top:8px;" class="animate-in">
                    <span class="source-badge"><span class="dot"></span> Built-in Knowledge Base &mdash; instant</span>
                </div>
            </div>
            <div class="scroll-fade" id="trans-scroll-fade"></div>
        </div>
    </div>
</div>

<!-- SETTINGS BAR -->
<div class="settings-bar">
    <span class="s-label">Mode</span>
    <select><option value="noob">Noob</option><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select>
    <span class="s-label">Lang</span>
    <select><option>English</option><option>Spanish</option><option>French</option><option>German</option><option>Japanese</option><option>Chinese</option><option>Korean</option><option>Portuguese</option></select>
    <div class="ai-badge"><span class="ai-dot"></span> Ollama</div>
    <span class="s-label" id="theme-label">Terminal</span>
    <span class="s-spacer"></span>
    <span class="dimmed" style="font-size:10px;">Ready</span>
</div>

<!-- FOOTER -->
<div class="footer" id="footer-bar">
    <span><span class="kbd">Ctrl+B</span> Toggle Mode</span>
    <span><span class="kbd">Ctrl+T</span> AI Toggle</span>
    <span><span class="kbd">Ctrl+S</span> Switch Theme</span>
    <span><span class="kbd">Ctrl+L</span> Clear Panel</span>
    <span><span class="kbd">Ctrl+Q</span> Quit App</span>
</div>

<script>
function setTheme(theme) {
    document.getElementById('app').className = theme;
    document.querySelectorAll('.theme-switch button').forEach(function(b) {
        b.classList.remove('active');
    });
    document.getElementById('btn-' + theme).classList.add('active');
    document.getElementById('theme-label').textContent = theme === 'terminal' ? 'Terminal' : 'Glass';
}

function updateFooter(mode) {
    var footer = document.getElementById('footer-bar');
    if (mode === 'beginner') {
        footer.innerHTML =
            '<span><span class="kbd">Ctrl+B</span> Toggle Mode</span>' +
            '<span><span class="kbd">Ctrl+T</span> AI Toggle</span>' +
            '<span><span class="kbd">Ctrl+S</span> Switch Theme</span>' +
            '<span><span class="kbd">Ctrl+L</span> Clear Panel</span>' +
            '<span><span class="kbd">Ctrl+Q</span> Quit App</span>';
    } else {
        footer.innerHTML =
            '<span><span class="kbd">^B</span> Mode</span>' +
            '<span><span class="kbd">^T</span> AI</span>' +
            '<span><span class="kbd">^S</span> Theme</span>' +
            '<span><span class="kbd">^L</span> Clear</span>' +
            '<span><span class="kbd">^Q</span> Quit</span>';
    }
}

(function() {
    var panels = document.querySelectorAll('.panel-content');
    panels.forEach(function(panel) {
        var fade = panel.parentElement.querySelector('.scroll-fade');
        if (!fade) return;
        function check() {
            var diff = panel.scrollHeight - panel.clientHeight - panel.scrollTop;
            fade.classList.toggle('visible', diff > 20);
        }
        panel.addEventListener('scroll', check);
        setTimeout(check, 500);
    });

    document.querySelectorAll('.panel').forEach(function(panel) {
        panel.addEventListener('mouseenter', function() {
            document.querySelectorAll('.panel').forEach(function(p) { p.classList.remove('focus-glow'); });
            panel.classList.add('focus-glow');
        });
    });

    var modeSelect = document.querySelector('.settings-bar select');
    if (modeSelect) {
        modeSelect.addEventListener('change', function() {
            updateFooter(this.value.toLowerCase());
        });
    }
})();
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
