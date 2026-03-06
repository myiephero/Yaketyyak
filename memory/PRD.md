# Terminal Translator - PRD

## Original Problem Statement
Build a "Terminal Translator" that functions like Google Translate for the command line. It will sit alongside the terminal, providing real-time, plain-language explanations. Features include:
- Web dashboard with embedded terminal input
- Translation from terminal text to plain English
- Git Translator for GitHub repo analysis with KPIs
- Toggle between "Beginner" and "Familiar" modes
- Fast local knowledge base with AI fallback

## Architecture

### Backend (FastAPI)
- **server.py**: Main API with translate, github analyze, and knowledge base endpoints
- **knowledge_base.py**: Local pattern matching with 70+ patterns (sub-millisecond lookup)
- **ai_translator.py**: OpenAI GPT-5.2 integration via Emergent integrations
- **github_analyzer.py**: GitHub API client for repo analysis

### Frontend (React)
- **App.js**: Main dashboard with tabs and mode toggle
- **TerminalInput.js**: Terminal-style input component
- **TranslationPanel.js**: AI/KB explanation display with markdown
- **GitAnalyzer.js**: GitHub repo analysis with stat cards
- **ModeToggle.js**: Beginner/Familiar mode switch
- **Navbar.js**: Navigation with KB stats

## User Personas
1. **Beginner Coder**: Needs detailed, friendly explanations with analogies
2. **Familiar Developer**: Wants concise, technical explanations

## Core Requirements
- [x] Fast local knowledge base lookup (<1ms)
- [x] AI fallback for unknown patterns
- [x] Beginner mode (detailed) / Familiar mode (concise)
- [x] Git repo analyzer with quality scoring
- [x] GitHub KPIs (stars, forks, issues, license, etc.)

## What's Been Implemented (Jan 2026)

### Backend
- FastAPI server with /api prefix routing
- MongoDB for translation history
- Knowledge base with 70+ patterns covering:
  - Git commands (15 patterns)
  - npm/yarn commands (5 patterns)
  - Python commands (4 patterns)
  - Docker commands (4 patterns)
  - Linux/Unix commands (14 patterns)
  - Common errors (16 patterns)
  - Regex pattern matchers for complex cases
- OpenAI GPT-5.2 integration for AI fallback
- GitHub API integration for repo analysis

### Frontend
- Dark "Glass Console" theme with neon accents
- Split-pane layout (Terminal | Translation)
- Animated mode toggle (Beginner/Familiar)
- GitHub repo analyzer with:
  - Quality assessment scoring (0-100)
  - Stats grid (stars, forks, watchers, issues)
  - License, contributors, release info
  - Plain-English summary
- Toast notifications via Sonner

## P0/P1/P2 Features

### P0 (Implemented)
- Terminal text translation
- Local knowledge base
- AI fallback
- Mode toggle
- Git repo analysis

### P1 (Future)
- Translation history view
- Editable knowledge base UI
- Multi-language support

### P2 (Backlog)
- Custom pattern addition
- Export/share translations
- Batch analysis

## Next Tasks
1. Add more patterns to knowledge base (containerization, cloud CLIs)
2. Implement history view with search
3. Add pattern contribution feature
4. Multi-language translation support
