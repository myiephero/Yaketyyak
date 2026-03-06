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

from translator import translate, LANGUAGE_NAMES
from knowledge_base import ensure_knowledge_base_exists

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\].*?\x07|\x1b\[.*?[@-~]|\r")


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


class TranslationPanel(Static):
    pass


class ShellOutput(RichLog):
    pass


class OutputReceived(Message):
    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__()


class TerminalTranslator(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    #main-container {
        layout: horizontal;
        height: 1fr;
    }

    #shell-panel {
        width: 1fr;
        border: solid $accent;
        height: 100%;
    }

    #shell-panel-inner {
        height: 1fr;
    }

    #shell-title {
        dock: top;
        height: 1;
        background: $accent;
        color: $text;
        text-align: center;
        text-style: bold;
        padding: 0 1;
    }

    #shell-output {
        height: 1fr;
        scrollbar-size: 1 1;
    }

    #shell-input {
        dock: bottom;
        height: 3;
    }

    #translation-panel {
        width: 1fr;
        border: solid $success;
        height: 100%;
    }

    #translation-panel-inner {
        height: 1fr;
    }

    #translation-title {
        dock: top;
        height: 1;
        background: $success;
        color: $text;
        text-align: center;
        text-style: bold;
        padding: 0 1;
    }

    #translation-output {
        height: 1fr;
        scrollbar-size: 1 1;
        padding: 0 1;
    }

    #settings-bar {
        dock: bottom;
        height: 3;
        layout: horizontal;
        background: $surface;
        padding: 0 1;
    }

    #settings-bar Label {
        padding: 1 1 0 0;
        width: auto;
    }

    #mode-select {
        width: 24;
    }

    #lang-select {
        width: 20;
    }

    #ai-label {
        padding: 1 1 0 2;
    }

    #status-label {
        padding: 1 1 0 2;
        color: $text-muted;
        width: 1fr;
        text-align: right;
    }
    """

    TITLE = "Terminal Translator"
    SUB_TITLE = "Type commands in the shell \u2014 get plain-language explanations"

    BINDINGS = [
        Binding("ctrl+b", "toggle_mode", "Toggle Beginner/Familiar"),
        Binding("ctrl+t", "toggle_ai", "Toggle AI"),
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

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            with Container(id="shell-panel"):
                with Vertical(id="shell-panel-inner"):
                    yield Label("SHELL", id="shell-title")
                    yield ShellOutput(id="shell-output", highlight=False, markup=False, wrap=True)
                    yield Input(
                        placeholder="Type your command here and press Enter...",
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
            yield Label("Ready", id="status-label")

        yield Footer()

    def on_mount(self) -> None:
        self.kb = ensure_knowledge_base_exists()
        self.shell = ShellProcess(on_output=self._on_shell_output)
        self.shell.start()
        shell_input = self.query_one("#shell-input", Input)
        shell_input.focus()

        trans = self.query_one("#translation-output", RichLog)
        trans.write("[bold green]Welcome to Terminal Translator![/]\n")
        trans.write("Type commands in the shell on the left.\n")
        trans.write("Explanations will appear here automatically.\n\n")
        trans.write("[dim]Ctrl+B: Toggle Beginner/Familiar mode[/]\n")
        trans.write("[dim]Ctrl+T: Toggle AI on/off[/]\n")
        trans.write("[dim]Ctrl+Q: Quit[/]\n")

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
        elif source == "ai":
            source_tag = "[blue][AI][/blue]"
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
