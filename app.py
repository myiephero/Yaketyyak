import streamlit as st
from knowledge_base import (
    ensure_knowledge_base_exists,
    save_knowledge_base,
    local_lookup,
    validate_regex,
)
from translator import (
    translate_with_ai_stream,
    LANGUAGE_NAMES,
)

EXAMPLE_SNIPPETS = {
    "Permission denied error": "bash: ./deploy.sh: Permission denied",
    "Module not found (Python)": "Traceback (most recent call last):\n  File \"app.py\", line 1, in <module>\n    import flask\nModuleNotFoundError: No module named 'flask'",
    "Git merge conflict": "Auto-merging src/index.js\nCONFLICT (content): Merge conflict in src/index.js\nAutomatic merge failed; fix conflicts and then commit the result.",
    "Server started": "INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)\nINFO:     Started reloader process [28720]",
    "Command not found": "zsh: command not found: nmp",
    "Port in use": "Error: listen EADDRINUSE: address already in use :::3000\n    at Server.setupListenHandle [as _setupListenHandle] (net.js:1380:14)",
    "npm install error": "npm ERR! code ERESOLVE\nnpm ERR! ERESOLVE unable to resolve dependency tree\nnpm ERR! Found: react@18.2.0\nnpm ERR! peer react@\"^17.0.0\" from react-beautiful-dnd@13.1.1",
    "Successful build": "webpack 5.88.2 compiled successfully in 3456 ms\n\n  VITE v4.4.9  ready in 892 ms\n\n  ➜  Local:   http://localhost:5173/",
    "Segmentation fault": "Segmentation fault (core dumped)",
    "SSH connection refused": "ssh: connect to host 192.168.1.100 port 22: Connection refused",
    "Python traceback": "Traceback (most recent call last):\n  File \"main.py\", line 42, in <module>\n    result = process_data(data)\n  File \"main.py\", line 28, in process_data\n    return data['users'][0]['name']\nKeyError: 'users'",
    "Docker build output": "Step 1/8 : FROM node:18-alpine\n ---> 7e17a7c1234d\nStep 2/8 : WORKDIR /app\n ---> Using cache\n ---> 8f3a2b4c5d6e\nStep 3/8 : COPY package*.json ./\n ---> 9a0b1c2d3e4f\nSuccessfully built a1b2c3d4e5f6\nSuccessfully tagged myapp:latest",
    "ls -la output": "total 48\ndrwxr-xr-x  12 user  staff   384 Mar  6 10:23 .\ndrwxr-xr-x   5 user  staff   160 Mar  1 09:00 ..\n-rw-r--r--   1 user  staff   220 Mar  6 10:23 .gitignore\n-rw-r--r--   1 user  staff  1234 Mar  6 10:23 package.json\ndrwxr-xr-x   8 user  staff   256 Mar  6 10:23 src",
    "Test results": "FAIL src/components/Button.test.js\n  ● Button component › renders correctly\n    expect(received).toBe(expected)\n    Expected: \"Submit\"\n    Received: \"Click me\"\n\nTests: 3 passed, 1 failed, 4 total",
    "SSL certificate error": "curl: (60) SSL certificate problem: certificate has expired\nMore details here: https://curl.se/docs/sslcerts.html",
}

st.set_page_config(
    page_title="Terminal Translator",
    page_icon="🖥️",
    layout="wide",
)

if "history" not in st.session_state:
    st.session_state.history = []
if "mode" not in st.session_state:
    st.session_state.mode = "beginner"
if "language" not in st.session_state:
    st.session_state.language = "en"
if "use_ai" not in st.session_state:
    st.session_state.use_ai = True
if "kb" not in st.session_state:
    st.session_state.kb = ensure_knowledge_base_exists()
if "prev_example" not in st.session_state:
    st.session_state.prev_example = "(paste your own)"

with st.sidebar:
    st.title("Settings")

    st.subheader("Explanation Mode")
    mode = st.radio(
        "Choose your experience level:",
        options=["beginner", "familiar"],
        format_func=lambda x: {
            "beginner": "Beginner — Detailed, assumes zero knowledge",
            "familiar": "Familiar — Concise, assumes basic CLI concepts",
        }[x],
        index=0 if st.session_state.mode == "beginner" else 1,
        key="mode_radio",
    )
    st.session_state.mode = mode

    st.divider()

    st.subheader("Language")
    lang_options = list(LANGUAGE_NAMES.keys())
    language = st.selectbox(
        "Explanation language:",
        options=lang_options,
        format_func=lambda x: LANGUAGE_NAMES[x],
        index=lang_options.index(st.session_state.language),
        key="lang_select",
    )
    st.session_state.language = language

    st.divider()

    st.subheader("Translation Source")
    use_ai = st.toggle(
        "Enable AI translations",
        value=st.session_state.use_ai,
        key="ai_toggle",
        help="When enabled, uses AI for text not found in the local knowledge base. "
        "Uses Replit AI Integrations (billed to your credits).",
    )
    st.session_state.use_ai = use_ai

    st.divider()

    st.subheader("Knowledge Base")
    kb = st.session_state.kb
    kb_stats = (
        f"**{len(kb.get('commands', {}))}** commands, "
        f"**{len(kb.get('error_patterns', {}))}** error patterns, "
        f"**{len(kb.get('output_patterns', {}))}** output patterns"
    )
    st.markdown(kb_stats)

    with st.expander("Add Custom Entry"):
        entry_type = st.selectbox(
            "Entry type:",
            ["commands", "error_patterns", "output_patterns"],
            format_func=lambda x: x.replace("_", " ").title(),
        )
        entry_key = st.text_input("Key/Name:")

        if entry_type == "commands":
            entry_beginner = st.text_area("Beginner explanation:")
            entry_familiar = st.text_area("Familiar explanation:")
            if st.button("Add Entry", use_container_width=True):
                if entry_key and entry_beginner:
                    kb.setdefault("commands", {})[entry_key] = {
                        "beginner": entry_beginner,
                        "familiar": entry_familiar or entry_beginner,
                    }
                    save_knowledge_base(kb)
                    st.session_state.kb = kb
                    st.success(f"Added command: {entry_key}")
                else:
                    st.error("Key and beginner explanation are required.")
        else:
            entry_pattern = st.text_input("Regex pattern:")
            entry_beginner = st.text_area("Beginner explanation:")
            entry_familiar = st.text_area("Familiar explanation:")
            if st.button("Add Entry", use_container_width=True):
                if entry_key and entry_pattern and entry_beginner:
                    if not validate_regex(entry_pattern):
                        st.error("Invalid regex pattern. Please check the syntax and try again.")
                    else:
                        kb.setdefault(entry_type, {})[entry_key] = {
                            "pattern": entry_pattern,
                            "beginner": entry_beginner,
                            "familiar": entry_familiar or entry_beginner,
                        }
                        save_knowledge_base(kb)
                        st.session_state.kb = kb
                        st.success(f"Added {entry_type}: {entry_key}")
                else:
                    st.error("All fields are required.")

    if st.button("Reload Knowledge Base", use_container_width=True):
        st.session_state.kb = ensure_knowledge_base_exists()
        st.success("Knowledge base reloaded.")

    st.divider()

    if st.button("Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

st.title("Terminal Translator")
st.markdown(
    "Paste any terminal output, command, or error message and get a plain-language explanation."
)

col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("Terminal Input")

    example = st.selectbox(
        "Try an example:",
        options=["(paste your own)"] + list(EXAMPLE_SNIPPETS.keys()),
        index=0,
        key="example_select",
    )

    if example != st.session_state.prev_example:
        st.session_state.prev_example = example
        if example != "(paste your own)":
            st.session_state.terminal_input = EXAMPLE_SNIPPETS[example]
        else:
            st.session_state.terminal_input = ""

    terminal_text = st.text_area(
        "Paste terminal output here:",
        height=250,
        placeholder="$ npm run build\n\nnpm ERR! Missing script: \"build\"\nnpm ERR! \nnpm ERR! To see a list of scripts, run:\nnpm ERR!   npm run",
        key="terminal_input",
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        translate_btn = st.button(
            "Translate",
            type="primary",
            use_container_width=True,
            disabled=not terminal_text.strip(),
        )
    with col_btn2:
        mode_label = "Beginner" if st.session_state.mode == "beginner" else "Familiar"
        lang_label = LANGUAGE_NAMES[st.session_state.language]
        st.markdown(
            f"**Mode:** {mode_label} &nbsp;|&nbsp; **Lang:** {lang_label}"
        )

with col_output:
    st.subheader("Translation")

    if translate_btn and terminal_text.strip():
        text = terminal_text.strip()
        kb = st.session_state.kb
        local_result = local_lookup(text, kb, st.session_state.mode)

        if local_result:
            source_badge = ":green[Local Knowledge Base]"
            category = local_result["category"].replace("_", " ").title()

            st.markdown(f"**Source:** {source_badge} &nbsp;|&nbsp; **Category:** {category}")
            st.divider()
            st.markdown(local_result["explanation"])

            st.session_state.history.insert(0, {
                "input": text[:100] + ("..." if len(text) > 100 else ""),
                "source": "Local KB",
                "category": category,
                "mode": st.session_state.mode,
                "explanation": local_result["explanation"],
            })

        elif st.session_state.use_ai:
            source_badge = ":blue[AI (OpenAI)]"
            st.markdown(f"**Source:** {source_badge}")
            st.divider()

            response_container = st.empty()
            full_response = ""

            try:
                for chunk in translate_with_ai_stream(
                    text,
                    st.session_state.mode,
                    st.session_state.language,
                ):
                    full_response += chunk
                    response_container.markdown(full_response + "▌")

                response_container.markdown(full_response)

                st.session_state.history.insert(0, {
                    "input": text[:100] + ("..." if len(text) > 100 else ""),
                    "source": "AI",
                    "category": "AI Analysis",
                    "mode": st.session_state.mode,
                    "explanation": full_response[:200] + ("..." if len(full_response) > 200 else ""),
                })
            except Exception as e:
                error_msg = str(e)
                if "FREE_CLOUD_BUDGET_EXCEEDED" in error_msg:
                    st.error(
                        "Your free cloud budget has been exceeded. "
                        "Please upgrade your Replit plan to continue using AI translations."
                    )
                else:
                    st.error(f"AI translation failed: {error_msg}")
        else:
            st.warning(
                "No match found in the local knowledge base, and AI translation is disabled. "
                "Enable AI translations in the sidebar or add this pattern to your knowledge base."
            )
    elif not translate_btn:
        st.markdown(
            "*Paste terminal text on the left and click **Translate** to get started.*"
        )

st.divider()

if st.session_state.history:
    st.subheader("Recent Translations")
    for i, entry in enumerate(st.session_state.history[:10]):
        with st.expander(
            f"`{entry['input']}` — {entry['source']} ({entry['mode'].title()})",
            expanded=False,
        ):
            st.markdown(entry["explanation"])

st.divider()

with st.expander("About Terminal Translator"):
    st.markdown(
        """
**Terminal Translator** is like Google Translate for your command line. It takes confusing 
terminal output \u2014 commands, errors, status messages \u2014 and explains them in plain language.

**How it works:**

1. **Paste** any terminal text into the input area
2. The tool first checks a **local knowledge base** of common commands and error patterns
3. If no match is found, it uses **AI** to provide a detailed explanation
4. Choose between **Beginner** (very detailed) and **Familiar** (concise) modes

**Features:**
- Built-in knowledge base with 30+ commands and 20+ error patterns
- AI-powered explanations for anything not in the knowledge base
- 8 languages supported for AI translations
- Customizable knowledge base \u2014 add your own entries
- Translation history for easy reference

**Cross-platform:** Works anywhere you can open a browser. Designed for macOS, Linux, 
and Windows users alike.
"""
    )
