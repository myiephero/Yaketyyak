from flask import Flask, render_template_string, request, jsonify
import os
import urllib.request
import json
from datetime import datetime, timezone

app = Flask(__name__)

def parse_github_url(url):
    import re
    patterns = [
        r"(?:https?://)?github\.com/([^/]+)/([^/\s#?]+)",
        r"^([^/\s]+)/([^/\s]+)$",
    ]
    for pattern in patterns:
        m = re.match(pattern, url.strip().rstrip("/"))
        if m:
            return m.group(1), m.group(2).replace(".git", "")
    return None, None

def analyze_repo(owner, repo):
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "YaketyYak/1.0",
    }
    req = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())

    contrib_url = f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=1&anon=true"
    contributor_count = 0
    try:
        req2 = urllib.request.Request(contrib_url, headers=headers)
        with urllib.request.urlopen(req2, timeout=5) as resp2:
            link_header = resp2.headers.get("Link", "")
            if 'rel="last"' in link_header:
                import re
                m = re.search(r'page=(\d+)>; rel="last"', link_header)
                if m:
                    contributor_count = int(m.group(1))
            else:
                contributors = json.loads(resp2.read())
                contributor_count = len(contributors)
    except Exception:
        contributor_count = 0

    releases_count = 0
    try:
        rel_url = f"https://api.github.com/repos/{owner}/{repo}/releases?per_page=1"
        req3 = urllib.request.Request(rel_url, headers=headers)
        with urllib.request.urlopen(req3, timeout=5) as resp3:
            link_header = resp3.headers.get("Link", "")
            if 'rel="last"' in link_header:
                import re
                m = re.search(r'page=(\d+)>; rel="last"', link_header)
                if m:
                    releases_count = int(m.group(1))
            else:
                releases = json.loads(resp3.read())
                releases_count = len(releases)
    except Exception:
        releases_count = 0

    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    watchers = data.get("subscribers_count", data.get("watchers_count", 0))
    open_issues = data.get("open_issues_count", 0)
    size_kb = data.get("size", 0)
    lang = data.get("language") or "Not specified"
    license_info = data.get("license")
    license_name = license_info.get("spdx_id", "Unknown") if license_info else "None"
    desc = data.get("description") or "No description provided"
    created = data.get("created_at", "")[:10]
    updated = data.get("pushed_at", "")[:10]
    default_branch = data.get("default_branch", "main")
    is_fork = data.get("fork", False)
    archived = data.get("archived", False)
    topics = data.get("topics", [])
    homepage = data.get("homepage") or ""
    has_wiki = data.get("has_wiki", False)
    has_pages = data.get("has_pages", False)

    score = 0
    risk_flags = []
    reward_flags = []

    if stars >= 5000:
        score += 25
        reward_flags.append("Highly starred project")
    elif stars >= 1000:
        score += 20
        reward_flags.append("Strong community interest")
    elif stars >= 100:
        score += 12
        reward_flags.append("Growing community")
    elif stars >= 10:
        score += 5
    else:
        risk_flags.append("Very low star count — may be experimental")

    if desc and desc != "No description provided":
        score += 5
        reward_flags.append("Has description")
    else:
        risk_flags.append("No description — purpose unclear")

    if license_name not in ("None", "Unknown", "NOASSERTION"):
        score += 10
        reward_flags.append(f"Licensed ({license_name})")
    else:
        risk_flags.append("No license — legally risky to use")

    days_since_update = None
    if data.get("pushed_at"):
        try:
            last_push = datetime.fromisoformat(data["pushed_at"].replace("Z", "+00:00"))
            days_since_update = (datetime.now(timezone.utc) - last_push).days
            if days_since_update < 30:
                score += 15
                reward_flags.append("Actively maintained (updated within 30 days)")
            elif days_since_update < 90:
                score += 10
                reward_flags.append("Recently maintained")
            elif days_since_update < 365:
                score += 5
                risk_flags.append(f"Not updated in {days_since_update} days")
            else:
                risk_flags.append(f"Stale — last updated {days_since_update} days ago")
        except Exception:
            pass

    if forks >= 500:
        score += 10
        reward_flags.append("Heavily forked — widely used")
    elif forks >= 50:
        score += 7
        reward_flags.append("Good fork count")
    elif forks >= 5:
        score += 3

    if contributor_count >= 50:
        score += 10
        reward_flags.append(f"{contributor_count}+ contributors")
    elif contributor_count >= 10:
        score += 7
        reward_flags.append(f"{contributor_count} contributors")
    elif contributor_count >= 2:
        score += 3
    elif contributor_count == 1:
        risk_flags.append("Single contributor — bus factor of 1")

    if archived:
        score -= 15
        risk_flags.append("Repository is ARCHIVED — no longer maintained")

    if is_fork:
        score -= 5
        risk_flags.append("This is a fork, not the original")

    if open_issues > 500:
        score -= 5
        risk_flags.append(f"{open_issues:,} open issues — may have unresolved problems")
    elif open_issues > 100:
        risk_flags.append(f"{open_issues:,} open issues")

    if releases_count > 0:
        score += 5
        reward_flags.append(f"{releases_count} release(s) published")
    else:
        risk_flags.append("No releases — may not have stable versions")

    if not data.get("fork", False):
        score += 3

    if has_wiki:
        score += 2
    if has_pages:
        score += 2
        reward_flags.append("Has GitHub Pages site")

    if size_kb > 500000:
        risk_flags.append(f"Very large repo ({size_kb // 1024} MB)")

    score = max(0, min(score, 100))

    if score >= 75:
        verdict = "Excellent"
        verdict_color = "#10b981"
        verdict_summary = "This repository is well-maintained, widely used, and safe to integrate."
    elif score >= 55:
        verdict = "Good"
        verdict_color = "#22d3ee"
        verdict_summary = "Solid project with good fundamentals. Worth using with normal caution."
    elif score >= 35:
        verdict = "Fair"
        verdict_color = "#facc15"
        verdict_summary = "Some concerns. Review the risk flags before depending on this project."
    else:
        verdict = "Caution"
        verdict_color = "#ef4444"
        verdict_summary = "Significant risks. Carefully evaluate if this meets your needs."

    return {
        "name": data.get("full_name", f"{owner}/{repo}"),
        "description": desc,
        "stars": stars,
        "forks": forks,
        "watchers": watchers,
        "open_issues": open_issues,
        "language": lang,
        "license": license_name,
        "created": created,
        "updated": updated,
        "default_branch": default_branch,
        "is_fork": is_fork,
        "archived": archived,
        "topics": topics[:10],
        "homepage": homepage,
        "size_kb": size_kb,
        "contributors": contributor_count,
        "releases": releases_count,
        "has_wiki": has_wiki,
        "has_pages": has_pages,
        "score": score,
        "verdict": verdict,
        "verdict_color": verdict_color,
        "verdict_summary": verdict_summary,
        "risk_flags": risk_flags,
        "reward_flags": reward_flags,
        "days_since_update": days_since_update,
        "url": f"https://github.com/{owner}/{repo}",
    }

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    body = request.get_json(silent=True)
    if not body or not isinstance(body, dict):
        return jsonify({"error": "Invalid request body"}), 400
    url = str(body.get("url", "")).strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    owner, repo = parse_github_url(url)
    if not owner or not repo:
        return jsonify({"error": "Could not parse GitHub URL. Use format: https://github.com/owner/repo"}), 400
    try:
        result = analyze_repo(owner, repo)
        return jsonify(result)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return jsonify({"error": f"Repository not found: {owner}/{repo}"}), 404
        elif e.code == 403:
            return jsonify({"error": "GitHub API rate limit exceeded. Try again in a few minutes."}), 429
        return jsonify({"error": f"GitHub API error: {e.code}"}), 502
    except Exception as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Yakety Yak — UI Preview</title>
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32.png">
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

.header {
    display: flex; align-items: center; justify-content: center; gap: 10px;
    padding: 14px 0 12px; font-weight: 700;
    font-size: 17px; letter-spacing: 2px; text-transform: uppercase;
    transition: all var(--transition);
    position: relative;
}
.header .header-logo {
    width: 48px; height: 48px; border-radius: 0;
    object-fit: contain; flex-shrink: 0;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,0.35));
}
.header::after {
    content: ''; position: absolute; bottom: 0; left: 5%; right: 5%;
    height: 1px; transition: background var(--transition);
}

/* ═══ VIEW TOGGLE ═══ */
.view-toggle {
    display: flex; justify-content: center; padding: 6px 0 4px;
    gap: 2px;
}
.view-toggle button {
    padding: 6px 22px; border: none;
    font-family: inherit; font-size: 11px; cursor: pointer;
    transition: all 0.25s var(--ease);
    font-weight: 600; letter-spacing: 0.5px;
    text-transform: uppercase;
    position: relative;
}
.view-toggle button:first-child { border-radius: 6px 0 0 6px; }
.view-toggle button:last-child { border-radius: 0 6px 6px 0; }
.view-toggle button:hover { filter: brightness(1.15); }

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
.panel.focus-glow { z-index: 1; }

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

.panel-content-wrap { position: relative; flex: 1; display: flex; flex-direction: column; min-height: 0; }
.scroll-fade {
    position: absolute; bottom: 0; left: 0; right: 0; height: 32px;
    pointer-events: none; z-index: 2;
    opacity: 0; transition: opacity 0.3s;
}
.scroll-fade.visible { opacity: 1; }

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

.footer {
    text-align: center; padding: 4px 12px;
    font-size: 10.5px; letter-spacing: 0.2px;
    transition: all var(--transition);
    display: flex; justify-content: center; gap: 6px;
    flex-wrap: wrap;
}
.footer .kbd {
    padding: 1px 5px; border-radius: 3px;
    font-size: 9.5px; font-weight: 600;
    transition: all var(--transition);
}

.line {
    line-height: 1.7; white-space: pre-wrap;
    transition: color var(--transition);
}
.spacer { height: 6px; }

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

.cmd-header {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 12px; border-radius: 8px; margin: 6px 0;
    transition: all var(--transition);
}
.cmd-header-icon { font-size: 18px; }
.cmd-header-text { font-weight: 700; font-size: 14px; letter-spacing: 0.3px; }
.cmd-header .line-ref {
    margin-left: auto;
}

.line-ref {
    display: inline-flex; align-items: center;
    padding: 1px 7px; border-radius: 4px;
    font-size: 9.5px; font-weight: 600;
    letter-spacing: 0.3px; white-space: nowrap;
    vertical-align: middle; margin-right: 5px;
    transition: all var(--transition);
}

.shell-line {
    display: flex; gap: 0; line-height: 1.7;
}
.line-num {
    width: 28px; text-align: right; padding-right: 8px;
    font-size: 10px; opacity: 0.25; flex-shrink: 0;
    user-select: none; line-height: 1.7;
}
.line-content { flex: 1; white-space: pre-wrap; }

/* ═══ GIT TRANSLATOR VIEW ═══ */
#git-view {
    display: none; flex-direction: column; flex: 1; min-height: 0; padding: 6px;
    animation: fadeSlideUp 0.3s var(--ease) both;
}
.git-panel {
    flex: 1; min-height: 0;
}
#git-view.active { display: flex; }
#terminal-view {
    display: none;
    animation: fadeSlideUp 0.3s var(--ease) both;
}
#terminal-view.active { display: flex; }

.git-input-area {
    display: flex; gap: 8px; padding: 10px 14px;
    align-items: center;
}
.git-input-area input {
    flex: 1; padding: 10px 14px; border-radius: 8px;
    font-family: inherit; font-size: 12.5px;
    border: none; outline: none;
    transition: all var(--transition);
}
.git-input-area button {
    padding: 10px 20px; border-radius: 8px; border: none;
    font-family: inherit; font-size: 12px; font-weight: 600;
    cursor: pointer; letter-spacing: 0.3px;
    transition: all 0.25s var(--ease);
    text-transform: uppercase;
}
.git-input-area button:hover { transform: translateY(-1px); }
.git-input-area button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.git-results {
    flex: 1; overflow-y: auto; padding: 8px;
    scroll-behavior: smooth;
    min-height: 0;
}

.git-card {
    border-radius: 12px; padding: 16px 20px; margin-bottom: 10px;
    transition: all var(--transition);
}
.git-card h2 {
    font-size: 16px; margin-bottom: 4px; font-weight: 700;
}
.git-card .desc {
    font-size: 11.5px; opacity: 0.7; margin-bottom: 12px; line-height: 1.5;
}

.kpi-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 8px; margin-bottom: 14px;
}
.kpi-item {
    border-radius: 8px; padding: 10px 12px; text-align: center;
    transition: all var(--transition);
}
.kpi-item .kpi-val { font-size: 18px; font-weight: 700; }
.kpi-item .kpi-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.8px; opacity: 0.6; margin-top: 2px; }

.verdict-bar {
    border-radius: 10px; padding: 14px 18px; margin-bottom: 14px;
    display: flex; align-items: center; gap: 14px;
    transition: all var(--transition);
}
.verdict-score {
    font-size: 28px; font-weight: 800; line-height: 1;
}
.verdict-label { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.verdict-summary { font-size: 11px; opacity: 0.8; line-height: 1.4; margin-top: 2px; }

.flag-section { margin-bottom: 10px; }
.flag-section h3 {
    font-size: 10px; text-transform: uppercase; letter-spacing: 1px;
    font-weight: 600; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;
}
.flag-item {
    font-size: 11px; line-height: 1.8; padding-left: 18px;
    position: relative;
}
.flag-item::before {
    position: absolute; left: 0; top: 0;
}
.flag-risk::before { content: "⚠"; }
.flag-reward::before { content: "✓"; }

.meta-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 4px 20px; font-size: 11px; margin-top: 12px;
    padding-top: 12px;
}
.meta-grid .meta-key { opacity: 0.5; }
.meta-grid .meta-val { font-weight: 600; }

.topics-wrap { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 4px; }
.topic-tag {
    padding: 2px 8px; border-radius: 12px;
    font-size: 10px; font-weight: 500;
    transition: all var(--transition);
}

.git-loading {
    display: none; align-items: center; justify-content: center;
    flex: 1; flex-direction: column; gap: 12px;
}
.git-loading.active { display: flex; }
.git-loading .spinner {
    width: 32px; height: 32px; border-radius: 50%;
    border: 3px solid transparent;
    animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.git-loading .loading-text { font-size: 12px; opacity: 0.6; }

.git-placeholder {
    display: flex; align-items: center; justify-content: center;
    flex: 1; flex-direction: column; gap: 8px; opacity: 0.4;
}
.git-placeholder .ph-icon { font-size: 36px; }
.git-placeholder .ph-text { font-size: 12px; text-align: center; line-height: 1.6; }

.git-error {
    display: none; border-radius: 10px; padding: 16px 20px; margin: 8px;
    text-align: center;
}
.git-error.active { display: block; }
.git-error .err-icon { font-size: 24px; margin-bottom: 6px; }
.git-error .err-text { font-size: 12px; }

/* ═══ TERMINAL THEME ═══ */
.terminal { background: #060a13; color: #e2e8f0; }
.terminal .header { background: #060a13; color: #10b981; }
.terminal .header::after { background: linear-gradient(90deg, transparent, #10b98140, transparent); }
.terminal .panel { border: 1px solid #10b98130; background: #0a0e17; box-shadow: 0 0 0 1px #10b98108; }
.terminal .panel.focus-glow { box-shadow: 0 0 20px #10b98115, 0 0 0 1px #10b98125; }
.terminal .panel-title { background: linear-gradient(135deg, #10b981, #059669); color: #0a0e17; }
.terminal .panel-content { background: #0a0e17; color: #cbd5e1; }
.terminal .scroll-fade { background: linear-gradient(transparent, #0a0e17); }
.terminal .shell-input-row { background: #0d1420; border-top: 1px solid #10b98120; }
.terminal .input-prompt { color: #10b981; }
.terminal .shell-input-row input { color: #e2e8f0; }
.terminal .shell-input-row input::placeholder { color: #475569; }
.terminal .cursor-blink { background: #10b981; }
.terminal .settings-bar { background: #0b1019; color: #94a3b8; border-top: 1px solid #1e293b40; }
.terminal .settings-bar select { background: #131b2e; color: #e2e8f0; border: 1px solid #1e293b; }
.terminal .ai-badge { background: #10b98118; color: #10b981; }
.terminal .ai-dot { background: #10b981; box-shadow: 0 0 6px #10b981; }
.terminal .footer { background: #060a13; color: #475569; border-top: 1px solid #1e293b30; }
.terminal .footer .kbd { background: #131b2e; color: #64748b; border: 1px solid #1e293b; }
.terminal .theme-switch button.active { background: #10b981; color: #0a0e17; }
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
.terminal .trans-section { background: #0d1420; border: 1px solid #1e293b40; }
.terminal .trans-section-title { color: #10b981; }
.terminal .cmd-header { background: linear-gradient(135deg, #10b98112, #10b98108); border: 1px solid #10b98120; }
.terminal .cmd-header-text { color: #10b981; }
.terminal .source-badge { background: #10b98115; color: #10b981; }
.terminal .source-badge .dot { background: #10b981; }
.terminal .line-ref { background: #38bdf815; color: #38bdf8; border: 1px solid #38bdf820; }
.terminal .panel-content::-webkit-scrollbar { width: 5px; }
.terminal .panel-content::-webkit-scrollbar-track { background: transparent; }
.terminal .panel-content::-webkit-scrollbar-thumb { background: #10b98140; border-radius: 3px; }
.terminal .panel-content::-webkit-scrollbar-thumb:hover { background: #10b98170; }

.terminal .view-toggle button { background: #0b1019; color: #475569; border: 1px solid #1e293b; }
.terminal .view-toggle button.active { background: #10b981; color: #0a0e17; border-color: #10b981; }

.terminal .git-input-area input { background: #0d1420; color: #e2e8f0; border: 1px solid #1e293b; }
.terminal .git-input-area input::placeholder { color: #475569; }
.terminal .git-input-area input:focus { border-color: #10b98160; box-shadow: 0 0 12px #10b98115; }
.terminal .git-input-area button { background: #10b981; color: #0a0e17; }
.terminal .git-card { background: #0d1420; border: 1px solid #1e293b40; }
.terminal .git-card h2 { color: #10b981; }
.terminal .kpi-item { background: #0d1420; border: 1px solid #1e293b30; }
.terminal .kpi-item .kpi-val { color: #e2e8f0; }
.terminal .verdict-bar { background: #0d1420; border: 1px solid #1e293b30; }
.terminal .flag-section h3.risk-title { color: #ef4444; }
.terminal .flag-section h3.reward-title { color: #10b981; }
.terminal .flag-risk { color: #fca5a5; }
.terminal .flag-reward { color: #6ee7b7; }
.terminal .meta-grid { border-top: 1px solid #1e293b40; }
.terminal .meta-grid .meta-val { color: #e2e8f0; }
.terminal .meta-grid .meta-key { color: #64748b; }
.terminal .topic-tag { background: #10b98115; color: #10b981; border: 1px solid #10b98125; }
.terminal .git-loading .spinner { border-top-color: #10b981; border-right-color: #10b98140; }
.terminal .git-loading .loading-text { color: #10b981; }
.terminal .git-error { background: #1c0a0a; border: 1px solid #ef444430; color: #fca5a5; }
.terminal .git-results::-webkit-scrollbar { width: 5px; }
.terminal .git-results::-webkit-scrollbar-track { background: transparent; }
.terminal .git-results::-webkit-scrollbar-thumb { background: #10b98140; border-radius: 3px; }

/* ═══ GLASS THEME ═══ */
.glass {
    background: #080518;
    background-image:
        radial-gradient(ellipse at 20% 50%, #6366f108 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, #a78bfa06 0%, transparent 50%),
        radial-gradient(ellipse at 50% 80%, #818cf805 0%, transparent 50%);
    color: #c7d2fe;
}
.glass .header { background: transparent; color: #a78bfa; }
.glass .header::after { background: linear-gradient(90deg, transparent, #a78bfa30, transparent); }
.glass .panel { border: 1px solid #6366f130; background: rgba(15, 10, 46, 0.7); backdrop-filter: blur(16px); box-shadow: 0 4px 24px rgba(99, 102, 241, 0.06); border-radius: 14px; }
.glass .panel.focus-glow { box-shadow: 0 0 30px #6366f115, 0 4px 24px rgba(99, 102, 241, 0.1), inset 0 1px 0 #818cf815; }
.glass .shell-panel { border-color: #6366f125; }
.glass .trans-panel { border-color: #818cf825; }
.glass .panel-title { background: linear-gradient(135deg, #4f46e5cc, #6366f1cc); color: #e0e7ff; backdrop-filter: blur(8px); }
.glass .panel-title.trans-title { background: linear-gradient(135deg, #6366f1cc, #818cf8cc); }
.glass .panel-content { background: transparent; color: #c7d2fe; }
.glass .scroll-fade { background: linear-gradient(transparent, #0f0a2e); }
.glass .shell-input-row { background: rgba(26, 21, 69, 0.6); border-top: 1px solid #818cf820; backdrop-filter: blur(8px); }
.glass .input-prompt { color: #818cf8; }
.glass .shell-input-row input { color: #e0e7ff; }
.glass .shell-input-row input::placeholder { color: #4c1d95; }
.glass .cursor-blink { background: #818cf8; }
.glass .settings-bar { background: rgba(26, 21, 69, 0.5); color: #a5b4fc; border-top: 1px solid #6366f115; backdrop-filter: blur(8px); }
.glass .settings-bar select { background: rgba(46, 16, 101, 0.5); color: #e0e7ff; border: 1px solid #6366f130; }
.glass .ai-badge { background: #a78bfa18; color: #a78bfa; }
.glass .ai-dot { background: #a78bfa; box-shadow: 0 0 6px #a78bfa; }
.glass .footer { background: rgba(8, 5, 24, 0.8); color: #6366f1; border-top: 1px solid #6366f115; }
.glass .footer .kbd { background: rgba(99, 102, 241, 0.1); color: #818cf8; border: 1px solid #6366f125; }
.glass .theme-switch button.active { background: linear-gradient(135deg, #6366f1, #818cf8); color: #e0e7ff; }
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
.glass .trans-section { background: rgba(99, 102, 241, 0.06); border: 1px solid #6366f118; backdrop-filter: blur(4px); }
.glass .trans-section-title { color: #a78bfa; }
.glass .cmd-header { background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(129, 140, 248, 0.06)); border: 1px solid #6366f120; }
.glass .cmd-header-text { color: #a78bfa; }
.glass .source-badge { background: #a78bfa15; color: #a78bfa; }
.glass .source-badge .dot { background: #a78bfa; }
.glass .line-ref { background: #67e8f912; color: #67e8f9; border: 1px solid #67e8f920; }
.glass .panel-content::-webkit-scrollbar { width: 5px; }
.glass .panel-content::-webkit-scrollbar-track { background: transparent; }
.glass .panel-content::-webkit-scrollbar-thumb { background: #6366f140; border-radius: 3px; }
.glass .panel-content::-webkit-scrollbar-thumb:hover { background: #6366f170; }

.glass .view-toggle button { background: rgba(26, 21, 69, 0.6); color: #6366f1; border: 1px solid #6366f130; backdrop-filter: blur(8px); }
.glass .view-toggle button.active { background: linear-gradient(135deg, #6366f1, #818cf8); color: #e0e7ff; border-color: #818cf8; }

.glass .git-input-area input { background: rgba(26, 21, 69, 0.6); color: #e0e7ff; border: 1px solid #6366f130; backdrop-filter: blur(8px); }
.glass .git-input-area input::placeholder { color: #4c1d95; }
.glass .git-input-area input:focus { border-color: #818cf860; box-shadow: 0 0 16px #6366f120; }
.glass .git-input-area button { background: linear-gradient(135deg, #6366f1, #818cf8); color: #e0e7ff; }
.glass .git-card { background: rgba(15, 10, 46, 0.7); border: 1px solid #6366f120; backdrop-filter: blur(12px); }
.glass .git-card h2 { color: #a78bfa; }
.glass .kpi-item { background: rgba(99, 102, 241, 0.08); border: 1px solid #6366f118; }
.glass .kpi-item .kpi-val { color: #e0e7ff; }
.glass .verdict-bar { background: rgba(99, 102, 241, 0.06); border: 1px solid #6366f118; }
.glass .flag-section h3.risk-title { color: #f87171; }
.glass .flag-section h3.reward-title { color: #a78bfa; }
.glass .flag-risk { color: #fca5a5; }
.glass .flag-reward { color: #c4b5fd; }
.glass .meta-grid { border-top: 1px solid #6366f118; }
.glass .meta-grid .meta-val { color: #e0e7ff; }
.glass .meta-grid .meta-key { color: #7c6bbf; }
.glass .topic-tag { background: rgba(167, 139, 250, 0.12); color: #a78bfa; border: 1px solid #a78bfa25; }
.glass .git-loading .spinner { border-top-color: #a78bfa; border-right-color: #a78bfa40; }
.glass .git-loading .loading-text { color: #a78bfa; }
.glass .git-error { background: rgba(239, 68, 68, 0.08); border: 1px solid #ef444425; color: #fca5a5; backdrop-filter: blur(8px); }
.glass .git-results::-webkit-scrollbar { width: 5px; }
.glass .git-results::-webkit-scrollbar-track { background: transparent; }
.glass .git-results::-webkit-scrollbar-thumb { background: #6366f140; border-radius: 3px; }

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-in {
    animation: fadeSlideUp 0.4s var(--ease) both;
}
.animate-in:nth-child(1) { animation-delay: 0s; }
.animate-in:nth-child(2) { animation-delay: 0.04s; }
.animate-in:nth-child(3) { animation-delay: 0.08s; }
.animate-in:nth-child(4) { animation-delay: 0.12s; }
.animate-in:nth-child(5) { animation-delay: 0.16s; }
.animate-in:nth-child(6) { animation-delay: 0.2s; }
.animate-in:nth-child(7) { animation-delay: 0.24s; }
.animate-in:nth-child(8) { animation-delay: 0.28s; }
.animate-in:nth-child(9) { animation-delay: 0.32s; }
.animate-in:nth-child(10) { animation-delay: 0.36s; }
.animate-in:nth-child(11) { animation-delay: 0.4s; }
.animate-in:nth-child(12) { animation-delay: 0.44s; }
.animate-in:nth-child(13) { animation-delay: 0.48s; }
.animate-in:nth-child(14) { animation-delay: 0.52s; }
.animate-in:nth-child(15) { animation-delay: 0.56s; }
.animate-in:nth-child(16) { animation-delay: 0.6s; }
.animate-in:nth-child(17) { animation-delay: 0.64s; }
.animate-in:nth-child(18) { animation-delay: 0.68s; }
.animate-in:nth-child(19) { animation-delay: 0.72s; }
.animate-in:nth-child(20) { animation-delay: 0.76s; }
.animate-in:nth-child(n+21) { animation-delay: 0.8s; }

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
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
</head>
<body class="terminal" id="app">

<div class="theme-switch">
    <button class="active" id="btn-terminal" onclick="setTheme('terminal')">Terminal</button>
    <button id="btn-glass" onclick="setTheme('glass')">Glass</button>
</div>

<div class="header"><img src="/static/logo-icon.png" alt="" class="header-logo">Yakety Yak</div>

<!-- VIEW TOGGLE -->
<div class="view-toggle">
    <button class="active" id="btn-terminal-view" onclick="switchView('terminal')">Terminal</button>
    <button id="btn-git-view" onclick="switchView('git')">Git Translator</button>
</div>

<!-- ═══════════════ TERMINAL VIEW ═══════════════ -->
<div class="main active" id="terminal-view">
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
                <div class="shell-line animate-in"><span class="line-num">17</span><span class="line-content"><span class="output">/Users/user/projects/yakety-yak</span></span></div>
            </div>
            <div class="scroll-fade" id="shell-scroll-fade"></div>
        </div>
        <div class="shell-input-row">
            <span class="input-prompt">~$</span>
            <input type="text" placeholder="Type a command, paste a GitHub URL, or 'help'" readonly>
            <span class="cursor-blink"></span>
        </div>
    </div>

    <div class="panel trans-panel">
        <div class="panel-title trans-title">TRANSLATION</div>
        <div class="panel-content-wrap">
            <div class="panel-content" id="trans-content">
                <div class="line animate-in"><span class="welcome-title">Welcome to Yakety Yak</span></div>
                <div class="spacer"></div>
                <div class="line animate-in">This tool explains everything that happens in your</div>
                <div class="line animate-in">terminal, in plain language. No experience needed!</div>
                <div class="spacer"></div>
                <div class="line animate-in"><span class="bold">Get started:</span></div>
                <div class="line animate-in">  Type <span class="cyan">try 1</span> to run your first command</div>
                <div class="line animate-in">  Paste a <span class="cyan">GitHub URL</span> to analyze a repo</div>
                <div class="line animate-in">  Type <span class="cyan">help</span> for full instructions</div>
                <div class="spacer"></div>

                <div class="line animate-in"><span class="bold">Quick start:</span></div>
                <div class="line animate-in">  <span class="cyan">1.</span> <span class="bold">ls</span> <span class="dimmed">—</span> List files in current folder</div>
                <div class="line animate-in">  <span class="cyan">2.</span> <span class="bold">pwd</span> <span class="dimmed">—</span> Print working directory</div>
                <div class="line animate-in">  <span class="cyan">3.</span> <span class="bold">whoami</span> <span class="dimmed">—</span> Show your username</div>
                <div class="line animate-in">  <span class="cyan">4.</span> <span class="bold">date</span> <span class="dimmed">—</span> Show current date and time</div>
                <div class="line animate-in">  <span class="cyan">5.</span> <span class="bold">echo "Hello!"</span> <span class="dimmed">—</span> Print text to the screen</div>
                <div class="spacer"></div>

                <div style="height:1px;margin:8px 0;opacity:0.15;background:currentColor;"></div>

                <div class="cmd-header animate-in">
                    <span class="cmd-header-icon">&#128194;</span>
                    <span class="cmd-header-text">ls -la</span>
                    <span class="line-ref">Line 1</span>
                </div>
                <div class="source-badge animate-in"><span class="dot"></span> Knowledge Base</div>
                <div class="spacer"></div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128218;</span> What it does</div>
                    <div class="line">Lists all files and folders in the current directory,</div>
                    <div class="line">including hidden ones (starting with a dot). The -l flag</div>
                    <div class="line">shows detailed info like permissions, owner, and file size.</div>
                </div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128065;</span> What you see</div>
                    <div class="line"><span class="line-ref">Line 2</span> The total count of disk blocks used.</div>
                    <div class="line"><span class="line-ref">Lines 3–4</span> The <span class="cyan">.</span> and <span class="cyan">..</span> entries — current folder and parent folder. Every directory has these.</div>
                    <div class="line"><span class="line-ref">Lines 5–6</span> Regular files (<span class="cyan">app.py</span>, <span class="cyan">build.py</span>). The <span class="dimmed">-rw-r--r--</span> means you can read and write them.</div>
                    <div class="line"><span class="line-ref">Line 7</span> A folder (<span class="cyan">src/</span>). The <span class="dimmed">d</span> at the start means directory.</div>
                    <div class="line"><span class="line-ref">Line 8</span> Another file (<span class="cyan">README.md</span>). The size column shows 1024 bytes.</div>
                </div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128161;</span> Try next</div>
                    <div class="line"><span class="cyan">ls -lh</span> <span class="dimmed">—</span> Same thing but with human-readable sizes (KB, MB)</div>
                    <div class="line"><span class="cyan">ls src/</span> <span class="dimmed">—</span> List files inside the src folder</div>
                </div>

                <div style="height:1px;margin:10px 0;opacity:0.1;background:currentColor;"></div>

                <div class="cmd-header animate-in">
                    <span class="cmd-header-icon">&#128736;</span>
                    <span class="cmd-header-text">git status</span>
                    <span class="line-ref">Line 9</span>
                </div>
                <div class="source-badge animate-in"><span class="dot"></span> Knowledge Base</div>
                <div class="spacer"></div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128218;</span> What it does</div>
                    <div class="line">Checks the current state of your Git project — which</div>
                    <div class="line">files you've changed, what's ready to commit, and what branch you're on.</div>
                </div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128065;</span> What you see</div>
                    <div class="line"><span class="line-ref">Line 10</span> You're on the <span class="cyan">main</span> branch — the primary version of your code.</div>
                    <div class="line"><span class="line-ref">Line 11</span> "Changes not staged" means you edited files but haven't told Git to track those edits yet.</div>
                    <div class="line"><span class="line-ref">Lines 12–13</span> The modified files: <span class="cyan">app.py</span> and <span class="cyan">themes.py</span>. Run <span class="cyan">git add .</span> to stage them.</div>
                </div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128161;</span> Try next</div>
                    <div class="line"><span class="cyan">git diff</span> <span class="dimmed">—</span> See exactly what changed in those files</div>
                    <div class="line"><span class="cyan">git add . && git commit -m "update"</span> <span class="dimmed">—</span> Save your changes</div>
                </div>

                <div style="height:1px;margin:10px 0;opacity:0.1;background:currentColor;"></div>

                <div class="cmd-header animate-in">
                    <span class="cmd-header-icon">&#128100;</span>
                    <span class="cmd-header-text">whoami</span>
                    <span class="line-ref">Line 14</span>
                </div>
                <div class="source-badge animate-in"><span class="dot"></span> Knowledge Base</div>
                <div class="spacer"></div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128218;</span> What it does</div>
                    <div class="line">Prints the username of the account currently logged in.</div>
                </div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128065;</span> What you see</div>
                    <div class="line"><span class="line-ref">Line 15</span> Your username is <span class="cyan">user</span>. This is the account running commands on this system.</div>
                </div>

                <div style="height:1px;margin:10px 0;opacity:0.1;background:currentColor;"></div>

                <div class="cmd-header animate-in">
                    <span class="cmd-header-icon">&#128204;</span>
                    <span class="cmd-header-text">pwd</span>
                    <span class="line-ref">Line 16</span>
                </div>
                <div class="source-badge animate-in"><span class="dot"></span> Knowledge Base</div>
                <div class="spacer"></div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128218;</span> What it does</div>
                    <div class="line">Prints the full path of the folder you're currently in.</div>
                </div>

                <div class="trans-section animate-in">
                    <div class="trans-section-title"><span class="icon">&#128065;</span> What you see</div>
                    <div class="line"><span class="line-ref">Line 17</span> You're in <span class="cyan">/Users/user/projects/yakety-yak</span>. Think of it like the address of the folder you have open.</div>
                </div>
            </div>
            <div class="scroll-fade" id="trans-scroll-fade"></div>
        </div>
    </div>
</div>

<!-- ═══════════════ GIT TRANSLATOR VIEW ═══════════════ -->
<div id="git-view">
    <div class="panel git-panel">
        <div class="panel-title trans-title">GIT TRANSLATOR</div>
        <div class="git-input-area">
            <input type="text" id="git-url-input" placeholder="https://github.com/owner/repo" spellcheck="false">
            <button id="git-analyze-btn" onclick="analyzeRepo()">Analyze</button>
        </div>

        <div class="git-loading" id="git-loading">
            <div class="spinner"></div>
            <div class="loading-text">Analyzing repository...</div>
        </div>

        <div class="git-error" id="git-error">
            <div class="err-icon">&#9888;</div>
            <div class="err-text" id="git-error-text"></div>
        </div>

        <div class="git-results" id="git-results">
            <div class="git-placeholder" id="git-placeholder">
                <div class="ph-icon">&#128269;</div>
                <div class="ph-text">Paste any GitHub URL above to get a<br>full risk/reward analysis before you clone</div>
            </div>
        </div>
    </div>
</div>

<!-- SETTINGS BAR -->
<div class="settings-bar">
    <span class="s-label">Mode</span>
    <select id="mode-select"><option value="noob">Noob</option><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select>
    <span class="s-label">Lang</span>
    <select><option>English</option><option>Spanish</option><option>French</option><option>German</option><option>Japanese</option><option>Chinese</option><option>Korean</option><option>Portuguese</option></select>
    <div class="ai-badge"><span class="ai-dot"></span> Ollama</div>
    <span class="s-label" id="theme-label">Terminal</span>
    <div class="s-spacer"></div>
</div>

<div class="footer" id="footer">
    <span><span class="kbd">Ctrl+B</span> Toggle Mode</span>
    <span><span class="kbd">Ctrl+T</span> AI Toggle</span>
    <span><span class="kbd">Ctrl+S</span> Switch Theme</span>
    <span><span class="kbd">Ctrl+G</span> Git Translator</span>
    <span><span class="kbd">Ctrl+L</span> Clear Panel</span>
    <span><span class="kbd">Ctrl+Q</span> Quit App</span>
</div>

<script>
(function() {
    function setTheme(t) {
        var app = document.getElementById('app');
        app.className = t;
        document.getElementById('btn-terminal').classList.toggle('active', t === 'terminal');
        document.getElementById('btn-glass').classList.toggle('active', t === 'glass');
        document.getElementById('theme-label').textContent = t === 'terminal' ? 'Terminal' : 'Glass';
    }
    window.setTheme = setTheme;

    function switchView(v) {
        var tv = document.getElementById('terminal-view');
        var gv = document.getElementById('git-view');
        var btnT = document.getElementById('btn-terminal-view');
        var btnG = document.getElementById('btn-git-view');
        if (v === 'git') {
            tv.classList.remove('active');
            gv.classList.add('active');
            btnT.classList.remove('active');
            btnG.classList.add('active');
            setTimeout(function() { document.getElementById('git-url-input').focus(); }, 100);
        } else {
            gv.classList.remove('active');
            tv.classList.add('active');
            btnT.classList.add('active');
            btnG.classList.remove('active');
        }
    }
    window.switchView = switchView;

    function updateFooter(mode) {
        var footer = document.getElementById('footer');
        if (mode === 'intermediate' || mode === 'advanced') {
            footer.innerHTML =
                '<span><span class="kbd">^B</span> Mode</span>' +
                '<span><span class="kbd">^T</span> AI</span>' +
                '<span><span class="kbd">^S</span> Theme</span>' +
                '<span><span class="kbd">^G</span> Git</span>' +
                '<span><span class="kbd">^L</span> Clear</span>' +
                '<span><span class="kbd">^Q</span> Quit</span>';
        } else {
            footer.innerHTML =
                '<span><span class="kbd">Ctrl+B</span> Toggle Mode</span>' +
                '<span><span class="kbd">Ctrl+T</span> AI Toggle</span>' +
                '<span><span class="kbd">Ctrl+S</span> Switch Theme</span>' +
                '<span><span class="kbd">Ctrl+G</span> Git Translator</span>' +
                '<span><span class="kbd">Ctrl+L</span> Clear Panel</span>' +
                '<span><span class="kbd">Ctrl+Q</span> Quit App</span>';
        }
    }

    function numberWithCommas(n) {
        return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    function esc(s) {
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    function safeHref(url) {
        if (/^https?:\/\//i.test(url)) return esc(url);
        return '#';
    }

    function renderResults(d) {
        var html = '<div class="git-card animate-in">';
        html += '<h2>' + esc(d.name) + '</h2>';
        html += '<div class="desc">' + esc(d.description) + '</div>';

        html += '<div class="verdict-bar" style="border-left: 4px solid ' + esc(d.verdict_color) + ';">';
        html += '<div class="verdict-score" style="color:' + esc(d.verdict_color) + ';">' + parseInt(d.score) + '</div>';
        html += '<div>';
        html += '<div class="verdict-label" style="color:' + esc(d.verdict_color) + ';">' + esc(d.verdict) + '</div>';
        html += '<div class="verdict-summary">' + esc(d.verdict_summary) + '</div>';
        html += '</div></div>';

        html += '<div class="kpi-grid">';
        var kpis = [
            {v: numberWithCommas(d.stars), l: "Stars"},
            {v: numberWithCommas(d.forks), l: "Forks"},
            {v: numberWithCommas(d.watchers), l: "Watchers"},
            {v: numberWithCommas(d.open_issues), l: "Open Issues"},
            {v: d.contributors > 0 ? numberWithCommas(d.contributors) : "?", l: "Contributors"},
            {v: d.releases > 0 ? numberWithCommas(d.releases) : "0", l: "Releases"},
            {v: esc(d.language), l: "Language"},
            {v: esc(d.license), l: "License"},
        ];
        for (var i = 0; i < kpis.length; i++) {
            html += '<div class="kpi-item"><div class="kpi-val">' + kpis[i].v + '</div><div class="kpi-label">' + kpis[i].l + '</div></div>';
        }
        html += '</div>';

        if (d.risk_flags.length > 0) {
            html += '<div class="flag-section"><h3 class="risk-title">&#9888; Risk Flags</h3>';
            for (var i = 0; i < d.risk_flags.length; i++) {
                html += '<div class="flag-item flag-risk">' + esc(d.risk_flags[i]) + '</div>';
            }
            html += '</div>';
        }

        if (d.reward_flags.length > 0) {
            html += '<div class="flag-section"><h3 class="reward-title">&#10003; Rewards</h3>';
            for (var i = 0; i < d.reward_flags.length; i++) {
                html += '<div class="flag-item flag-reward">' + esc(d.reward_flags[i]) + '</div>';
            }
            html += '</div>';
        }

        html += '<div class="meta-grid">';
        html += '<div class="meta-key">Created</div><div class="meta-val">' + esc(d.created) + '</div>';
        html += '<div class="meta-key">Last Push</div><div class="meta-val">' + esc(d.updated) + '</div>';
        html += '<div class="meta-key">Default Branch</div><div class="meta-val">' + esc(d.default_branch) + '</div>';
        html += '<div class="meta-key">Size</div><div class="meta-val">' + numberWithCommas(d.size_kb) + ' KB</div>';
        if (d.is_fork) { html += '<div class="meta-key">Type</div><div class="meta-val" style="color:#facc15;">Fork</div>'; }
        if (d.archived) { html += '<div class="meta-key">Status</div><div class="meta-val" style="color:#ef4444;">Archived</div>'; }
        if (d.homepage) { html += '<div class="meta-key">Homepage</div><div class="meta-val"><a href="' + safeHref(d.homepage) + '" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline;">' + esc(d.homepage) + '</a></div>'; }
        html += '</div>';

        if (d.topics && d.topics.length > 0) {
            html += '<div class="topics-wrap">';
            for (var i = 0; i < d.topics.length; i++) {
                html += '<span class="topic-tag">' + esc(d.topics[i]) + '</span>';
            }
            html += '</div>';
        }

        html += '<div style="margin-top:12px;font-size:10px;opacity:0.4;"><a href="' + safeHref(d.url) + '" target="_blank" rel="noopener" style="color:inherit;">' + esc(d.url) + '</a></div>';
        html += '</div>';
        return html;
    }

    function analyzeRepo() {
        var input = document.getElementById('git-url-input');
        var url = input.value.trim();
        if (!url) return;

        var loading = document.getElementById('git-loading');
        var results = document.getElementById('git-results');
        var error = document.getElementById('git-error');
        var btn = document.getElementById('git-analyze-btn');

        error.classList.remove('active');
        results.innerHTML = '';
        loading.classList.add('active');
        btn.disabled = true;

        fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url: url})
        })
        .then(function(resp) { return resp.json().then(function(data) { return {ok: resp.ok, data: data}; }); })
        .then(function(res) {
            loading.classList.remove('active');
            btn.disabled = false;
            if (!res.ok) {
                error.classList.add('active');
                document.getElementById('git-error-text').textContent = res.data.error || 'Unknown error';
            } else {
                results.innerHTML = renderResults(res.data);
            }
        })
        .catch(function(err) {
            loading.classList.remove('active');
            btn.disabled = false;
            error.classList.add('active');
            document.getElementById('git-error-text').textContent = 'Network error — check your connection';
        });
    }
    window.analyzeRepo = analyzeRepo;

    var gitInput = document.getElementById('git-url-input');
    gitInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') analyzeRepo();
    });

    var scrollEls = document.querySelectorAll('.panel-content');
    scrollEls.forEach(function(el) {
        var fade = el.parentElement.querySelector('.scroll-fade');
        if (!fade) return;
        el.addEventListener('scroll', function() {
            var atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 10;
            fade.classList.toggle('visible', !atBottom);
        });
        setTimeout(function() {
            fade.classList.toggle('visible', el.scrollHeight > el.clientHeight);
        }, 500);
    });

    document.querySelectorAll('.panel').forEach(function(panel) {
        panel.addEventListener('click', function() {
            document.querySelectorAll('.panel').forEach(function(p) { p.classList.remove('focus-glow'); });
            panel.classList.add('focus-glow');
        });
    });

    var modeSelect = document.getElementById('mode-select');
    if (modeSelect) {
        modeSelect.addEventListener('change', function() {
            updateFooter(this.value);
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
