# Terminal Translator - PRD

## Original Problem Statement
Build a "Terminal Translator" that functions like Google Translate for the command line - a split-pane TUI app where users type commands in one pane and see real-time plain-English explanations in the other. No copy-paste needed.

## Architecture

### TUI Application (Textual)
- **main.py**: Main Textual app with split-pane layout
- **shell_manager.py**: PTY-based shell subprocess management  
- **knowledge_base.py**: 76+ patterns with sub-millisecond lookup
- **ai_translator.py**: OpenAI GPT-5.2 fallback via Emergent integrations
- **styles.tcss**: Textual CSS styling

### Distribution
- **PyInstaller**: Builds standalone executables
- **GitHub Actions**: Auto-builds Mac/Windows/Linux binaries on release tags
- **Landing Page**: React site with OS-specific download buttons

### Landing Page (React)
- OS detection for primary download button
- Feature showcase
- App preview with split-pane mockup

## User Personas
1. **Complete Beginner**: First time opening terminal, needs detailed analogies
2. **Familiar Developer**: Knows basics, wants quick reminders

## What's Been Implemented (Jan 2026)

### TUI Application
- [x] Split-pane interface (shell left, translations right)
- [x] PTY-spawned real shell subprocess
- [x] 76 pattern local knowledge base (<0.025ms lookup)
- [x] AI fallback for unknown patterns
- [x] Beginner/Familiar mode toggle (Ctrl+B)
- [x] Command history navigation
- [x] Zero-config startup (built-in API key)

### Build Pipeline
- [x] pyproject.toml for pip install
- [x] PyInstaller spec file
- [x] GitHub Actions workflow for multi-OS builds

### Landing Page
- [x] OS detection (shows "Download for macOS/Windows/Linux")
- [x] Feature cards
- [x] App preview mockup
- [x] GitHub link

## Distribution Flow
1. User visits landing page
2. Clicks "Download for [their OS]"
3. Downloads binary from GitHub Releases
4. Double-clicks to run (no install needed)
5. Starts using terminal with live translations

## Next Tasks
1. Push to GitHub and create first release tag (v1.0.0)
2. Add code signing for Mac/Windows (reduces security warnings)
3. Create onboarding tutorial on first launch
4. Add "safe mode" - shows translations without executing
