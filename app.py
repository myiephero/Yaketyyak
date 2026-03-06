import asyncio
import os
import re
import pty
import signal
import struct
import fcntl
import termios
import threading
from collections import deque

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import (
    Header,
    Footer,
    Static,
    RichLog,
    Input,
    Label,
    Select,
)
from textual.reactive import reactive
from textual.message import Message

from translator import translate, LANGUAGE_NAMES, AI_AVAILABLE, get_ai_status
from knowledge_base import ensure_knowledge_base_exists
from themes import (
    APP_CSS,
    load_theme_preference,
    save_theme_preference,
    THEME_NAMES,
)

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\].*?\x07|\x1b\[.*?[@-~]|\r")

STARTER_COMMANDS = [
    ("pwd", "See what folder you're currently in"),
    ("ls", "List files and folders here"),
    ("ls -la", "List ALL files with details (including hidden)"),
    ("echo 'Hello World!'", "Print a message to the screen"),
    ("date", "Show the current date and time"),
    ("whoami", "Show your username"),
    ("uname -a", "Show info about your operating system"),
    ("cat /etc/os-release", "Show which Linux/OS version you have"),
    ("df -h", "Show how much disk space you have"),
    ("free -h", "Show how much memory (RAM) is available"),
    ("env | head -5", "Show first 5 environment variables"),
    ("history", "Show your recent command history"),
    ("mkdir test_folder", "Create a new folder called test_folder"),
    ("touch test_file.txt", "Create an empty file called test_file.txt"),
    ("echo 'hello' > test_file.txt", "Write 'hello' into test_file.txt"),
    ("cat test_file.txt", "Read the contents of test_file.txt"),
    ("cp test_file.txt backup.txt", "Copy test_file.txt to backup.txt"),
    ("ls -la test_*", "List all files starting with 'test_'"),
    ("rm test_file.txt backup.txt", "Delete the test files"),
    ("rmdir test_folder", "Remove the test folder"),
    ("which python", "Find where Python is installed"),
    ("python --version", "Check your Python version"),
    ("pip list | head -10", "Show first 10 installed Python packages"),
    ("git status", "Check if you're in a git repository"),
    ("uptime", "Show how long the system has been running"),
]

HELP_TEXT = """[bold green]Terminal Translator \u2014 Help[/]

[bold]What is this?[/]
This tool sits alongside a real terminal shell. You type commands
on the left, and plain-language explanations appear on the right
automatically. No copy-paste needed!

[bold]How to use it:[/]
  1. Type a command in the input box on the left and press Enter
  2. The command runs in a real shell
  3. An explanation appears on the right automatically

[bold]Quick-try commands:[/]
  Type [bold cyan]try[/] to see a list of beginner-friendly commands
  Type [bold cyan]try 1[/] through [bold cyan]try 25[/] to auto-run one

[bold]Keyboard shortcuts:[/]
  [dim]Ctrl+B[/]  Toggle between Beginner and Familiar mode
  [dim]Ctrl+T[/]  Toggle AI translations on/off
  [dim]Ctrl+S[/]  Switch theme (Terminal / Glass)
  [dim]Ctrl+L[/]  Clear the translation panel
  [dim]Ctrl+Q[/]  Quit the app

[bold]Tip:[/]
  All 25 starter commands are safe to run. They won't break
  anything and are great for learning!

[bold]Modes:[/]
  [green]Beginner[/]   Very detailed, assumes no prior knowledge
  [yellow]Familiar[/]   Concise, assumes you know the basics

[bold]How translations work:[/]
  1. Your command/output is checked against a built-in knowledge
     base of 500+ commands and 50+ common error patterns
  2. If no match is found, AI provides a detailed explanation
  3. Toggle AI off with Ctrl+T for offline/local-only mode

[dim]\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500[/]"""

TRY_LIST_TEXT_HEADER = """[bold cyan]Quick-Try Commands[/]
[dim]Type \"try N\" to run a command (e.g. \"try 1\")[/]
"""


def strip_ansi(text):
    return ANSI_ESCAPE.sub("", text)


class ShellProcess:
    def __init__(self, on_output):
        self.on_output = on_output
        self.master_fd = None
        self.pid = None
        self.running = False

    def start(self):
        shell = os.environ.get("SHELL", "/bin/bash")
        self.master_fd, slave_fd = pty.openpty()

        self.pid = os.fork()
        if self.pid == 0:
            os.close(self.master_fd)
            os.setsid()
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            if slave_fd > 2:
                os.close(slave_fd)
            env = os.environ.copy()
            env["TERM"] = "dumb"
            env["PS1"] = "$ "
            env["PROMPT_COMMAND"] = ""
            os.execvpe(shell, [shell, "--norc", "--noprofile"], env)
        else:
            os.close(slave_fd)
            self.running = True
            self._reader_thread = threading.Thread(
                target=self._read_output, daemon=True
            )
            self._reader_thread.start()

    def _read_output(self):
        while self.running:
            try:
                data = os.read(self.master_fd, 4096)
                if not data:
                    break
                text = data.decode("utf-8", errors="replace")
                self.on_output(text)
            except OSError:
                break
        self.running = False

    def write(self, data):
        if self.master_fd is not None and self.running:
            os.write(self.master_fd, data.encode("utf-8"))

    def send_line(self, line):
        self.write(line + "\n")

    def resize(self, rows, cols):
        if self.master_fd is not None:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            try:
                fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
            except OSError:
                pass

    def stop(self):
        self.running = False
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None
        if self.pid and self.pid > 0:
            try:
                os.kill(self.pid, signal.SIGTERM)
            except OSError:
                pass
            for _ in range(10):
                try:
                    pid, _ = os.waitpid(self.pid, os.WNOHANG)
                    if pid != 0:
                        break
                except ChildProcessError:
                    break
                import time
                time.sleep(0.1)
            else:
                try:
                    os.kill(self.pid, signal.SIGKILL)
                    os.waitpid(self.pid, 0)
                except (OSError, ChildProcessError):
                    pass
            self.pid = None


class ShellOutput(RichLog):
    pass


class TerminalTranslator(App):

    CSS = APP_CSS

    TITLE = "Terminal Translator"
    SUB_TITLE = "Type commands in the shell \u2014 get plain-language explanations"

    BINDINGS = [
        Binding("ctrl+b", "toggle_mode", "Beginner/Familiar"),
        Binding("ctrl+t", "toggle_ai", "Toggle AI"),
        Binding("ctrl+l", "clear_translations", "Clear Translations"),
        Binding("ctrl+s", "toggle_theme", "Switch Theme"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    mode = reactive("beginner")
    use_ai = reactive(True)
    language = reactive("en")

    def __init__(self):
        super().__init__()
        self.shell = None
        self.output_buffer = deque(maxlen=100)
        self._debounce_task = None
        self._last_command = ""
        self._pending_lines = []
        self._translation_id = 0
        self._shown_welcome = False
        self.current_theme = load_theme_preference()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            with Container(id="shell-panel"):
                with Vertical(id="shell-panel-inner"):
                    yield Label("SHELL", id="shell-title")
                    yield ShellOutput(id="shell-output", highlight=False, markup=False, wrap=True)
                    yield Input(
                        placeholder="Type a command and press Enter (or type 'help')",
                        id="shell-input",
                    )
            with Container(id="translation-panel"):
                with Vertical(id="translation-panel-inner"):
                    yield Label("TRANSLATION", id="translation-title")
                    yield RichLog(
                        id="translation-output", highlight=False, markup=True, wrap=True
                    )

        with Horizontal(id="settings-bar"):
            yield Label("Mode:")
            yield Select(
                [
                    ("Beginner", "beginner"),
                    ("Familiar", "familiar"),
                ],
                value="beginner",
                id="mode-select",
                allow_blank=False,
            )
            yield Label("Lang:")
            yield Select(
                [(name, code) for code, name in LANGUAGE_NAMES.items()],
                value="en",
                id="lang-select",
                allow_blank=False,
            )
            yield Label("AI: ON", id="ai-label")
            yield Label(f"Theme: {THEME_NAMES.get(self.current_theme, 'Terminal')}", id="theme-label")
            yield Label("Ready", id="status-label")

        yield Footer()

    def on_mount(self) -> None:
        self.kb = ensure_knowledge_base_exists()
        self._apply_theme_class()
        ai_status, ai_desc = get_ai_status()
        if not AI_AVAILABLE:
            self.use_ai = False
        self.shell = ShellProcess(on_output=self._on_shell_output)
        self.shell.start()
        shell_input = self.query_one("#shell-input", Input)
        shell_input.focus()
        ai_label = self.query_one("#ai-label", Label)
        if not AI_AVAILABLE:
            ai_label.update("AI: OFF")
        elif ai_status == "ollama_ready":
            ai_label.update("AI: Ollama")
        else:
            ai_label.update("AI: ON")
        self._ai_status = ai_status
        self._ai_desc = ai_desc
        self._show_welcome()

    def _apply_theme_class(self) -> None:
        screen = self.screen
        screen.remove_class("theme-terminal", "theme-glass")
        screen.add_class(f"theme-{self.current_theme}")

    def _show_welcome(self) -> None:
        trans = self.query_one("#translation-output", RichLog)
        trans.write("[bold green]Welcome to Terminal Translator![/]")
        trans.write("")
        trans.write("This tool explains everything that happens in your")
        trans.write("terminal, in plain language. No experience needed!")
        trans.write("")
        trans.write("[bold]Get started:[/]")
        trans.write("  Type [bold cyan]try 1[/] to run your first command")
        trans.write("  Type [bold cyan]try[/] to see all beginner commands")
        trans.write("  Type [bold cyan]help[/] for full instructions")
        trans.write("")
        trans.write("[bold]Try these yourself:[/]")
        trans.write(f"  [cyan]1.[/] [bold]{STARTER_COMMANDS[0][0]}[/] \u2014 {STARTER_COMMANDS[0][1]}")
        trans.write(f"  [cyan]2.[/] [bold]{STARTER_COMMANDS[1][0]}[/] \u2014 {STARTER_COMMANDS[1][1]}")
        trans.write(f"  [cyan]3.[/] [bold]{STARTER_COMMANDS[2][0]}[/] \u2014 {STARTER_COMMANDS[2][1]}")
        trans.write(f"  [cyan]4.[/] [bold]{STARTER_COMMANDS[3][0]}[/] \u2014 {STARTER_COMMANDS[3][1]}")
        trans.write(f"  [cyan]5.[/] [bold]{STARTER_COMMANDS[4][0]}[/] \u2014 {STARTER_COMMANDS[4][1]}")
        trans.write("")
        trans.write("[dim]Ctrl+B: Mode  |  Ctrl+T: AI  |  Ctrl+S: Theme  |  Ctrl+L: Clear  |  Ctrl+Q: Quit[/]")
        if not AI_AVAILABLE:
            trans.write("")
            trans.write("[yellow]AI is off \u2014 no AI backend detected.[/]")
            trans.write("[dim]Install Ollama + qwen2.5-coder for free local AI,[/]")
            trans.write("[dim]or set OPENAI_API_KEY for cloud AI.[/]")
            trans.write("[dim]The built-in knowledge base (500+ commands) works without AI![/]")
        elif hasattr(self, '_ai_status') and self._ai_status == "ollama_ready":
            trans.write("")
            trans.write(f"[green]AI powered by Ollama (local, private, free)[/]")
        elif hasattr(self, '_ai_status') and self._ai_status == "ollama_no_model":
            trans.write("")
            trans.write(f"[yellow]Ollama is running but model not installed.[/]")
            trans.write(f"[dim]Run: ollama pull qwen2.5-coder:1.5b[/]")
        trans.write("[dim]" + "\u2500" * 50 + "[/]")
        self._shown_welcome = True

    def _show_try_list(self) -> None:
        trans = self.query_one("#translation-output", RichLog)
        trans.write("")
        trans.write(TRY_LIST_TEXT_HEADER)
        trans.write("")
        for i, (cmd, desc) in enumerate(STARTER_COMMANDS, 1):
            trans.write(f"  [cyan]{i:2d}.[/] [bold]{cmd}[/]")
            trans.write(f"      [dim]{desc}[/]")
        trans.write("")
        trans.write("[dim]" + "\u2500" * 50 + "[/]")

    def _show_help(self) -> None:
        trans = self.query_one("#translation-output", RichLog)
        trans.write("")
        for line in HELP_TEXT.split("\n"):
            trans.write(line)

    def _handle_app_command(self, command: str) -> bool:
        cmd = command.strip().lower()

        if cmd == "help":
            self._show_help()
            return True

        if cmd == "try":
            self._show_try_list()
            return True

        try_match = re.match(r"^try\s+(\d+)$", cmd)
        if try_match:
            num = int(try_match.group(1))
            if 1 <= num <= len(STARTER_COMMANDS):
                actual_cmd = STARTER_COMMANDS[num - 1][0]
                desc = STARTER_COMMANDS[num - 1][1]
                trans = self.query_one("#translation-output", RichLog)
                trans.write("")
                trans.write(f"[bold cyan]Running:[/] {actual_cmd}")
                trans.write(f"[dim]{desc}[/]")
                trans.write("")
                self._last_command = actual_cmd
                if self.shell and self.shell.running:
                    self.shell.send_line(actual_cmd)
                return True
            else:
                trans = self.query_one("#translation-output", RichLog)
                trans.write(f"[yellow]No command #{num}. Type 'try' to see the list (1-{len(STARTER_COMMANDS)}).[/]")
                return True

        return False

    def _on_shell_output(self, text: str) -> None:
        self.call_from_thread(self._handle_output, text)

    def _handle_output(self, text: str) -> None:
        shell_out = self.query_one("#shell-output", ShellOutput)
        clean = strip_ansi(text)
        for line in clean.split("\n"):
            stripped = line.rstrip()
            if stripped:
                shell_out.write(stripped)
                self._pending_lines.append(stripped)

        if self._debounce_task is not None:
            self._debounce_task.cancel()
        self._debounce_task = asyncio.get_event_loop().call_later(
            0.8, self._trigger_translation
        )

    def _normalize_for_translation(self, lines):
        prompt_re = re.compile(r"^\$\s*")
        normalized = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped == "$":
                continue
            cleaned = prompt_re.sub("", stripped)
            if cleaned:
                normalized.append(cleaned)
        return normalized

    def _trigger_translation(self) -> None:
        if not self._pending_lines:
            return

        lines = list(self._pending_lines)
        self._pending_lines.clear()

        normalized = self._normalize_for_translation(lines)
        if not normalized:
            return

        combined = "\n".join(normalized)

        if combined == self._last_command:
            return

        self._translation_id += 1
        self._do_translate(combined, self._translation_id)

    @work(thread=True, exclusive=True)
    def _do_translate(self, text: str, tid: int = 0) -> None:
        status = self.query_one("#status-label", Label)
        self.call_from_thread(status.update, "Translating...")

        result = translate(
            text,
            mode=self.mode,
            language=self.language,
            use_ai=self.use_ai,
        )

        if tid != self._translation_id:
            self.call_from_thread(status.update, "Ready")
            return

        explanation = result.get("explanation", "")
        source = result.get("source", "")
        category = result.get("category", "")

        if source == "local_db":
            source_tag = "[green][Local KB][/green]"
        elif source == "ai" and category == "ollama":
            source_tag = "[cyan][Ollama AI][/cyan]"
        elif source == "ai":
            source_tag = "[blue][Cloud AI][/blue]"
        elif source == "error":
            source_tag = "[red][Error][/red]"
        else:
            source_tag = "[dim][No match][/dim]"

        preview = text[:80].replace("\n", " ")
        if len(text) > 80:
            preview += "..."

        trans_out = self.query_one("#translation-output", RichLog)
        self.call_from_thread(
            self._write_translation, trans_out, source_tag, category, preview, explanation
        )
        self.call_from_thread(status.update, "Ready")

    def _write_translation(self, trans_out, source_tag, category, preview, explanation):
        trans_out.write("")
        trans_out.write(f"{source_tag} [dim]{category}[/dim]")
        trans_out.write(f"[bold]> {preview}[/bold]")
        trans_out.write("")
        for line in explanation.split("\n"):
            trans_out.write(line)
        trans_out.write("[dim]" + "\u2500" * 50 + "[/dim]")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "shell-input":
            command = event.value
            event.input.clear()

            if not command.strip():
                return

            if self._handle_app_command(command):
                return

            if self.shell and self.shell.running:
                self._last_command = command
                self.shell.send_line(command)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "mode-select":
            self.mode = event.value
        elif event.select.id == "lang-select":
            self.language = event.value

    def action_toggle_mode(self) -> None:
        mode_select = self.query_one("#mode-select", Select)
        if self.mode == "beginner":
            self.mode = "familiar"
            mode_select.value = "familiar"
        else:
            self.mode = "beginner"
            mode_select.value = "beginner"
        status = self.query_one("#status-label", Label)
        status.update(f"Mode: {self.mode.title()}")

    def action_toggle_ai(self) -> None:
        self.use_ai = not self.use_ai
        ai_label = self.query_one("#ai-label", Label)
        ai_label.update(f"AI: {'ON' if self.use_ai else 'OFF'}")
        status = self.query_one("#status-label", Label)
        status.update(f"AI {'enabled' if self.use_ai else 'disabled'}")

    def action_toggle_theme(self) -> None:
        if self.current_theme == "terminal":
            self.current_theme = "glass"
        else:
            self.current_theme = "terminal"
        save_theme_preference(self.current_theme)
        self._apply_theme_class()
        theme_label = self.query_one("#theme-label", Label)
        theme_label.update(f"Theme: {THEME_NAMES[self.current_theme]}")
        status = self.query_one("#status-label", Label)
        status.update(f"Switched to {THEME_NAMES[self.current_theme]} theme")

    def action_clear_translations(self) -> None:
        self._pending_lines.clear()
        if self._debounce_task is not None:
            self._debounce_task.cancel()
            self._debounce_task = None
        self._translation_id += 1
        trans = self.query_one("#translation-output", RichLog)
        trans.clear()
        trans.write("[dim]Translation panel cleared. Type a command to continue.[/]")

    def on_unmount(self) -> None:
        if self.shell:
            self.shell.stop()

    def action_quit(self) -> None:
        if self.shell:
            self.shell.stop()
        self.exit()


if __name__ == "__main__":
    app = TerminalTranslator()
    app.run()
