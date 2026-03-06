"""
Terminal Translator - Main Entry Point
A split-pane TUI with real shell integration and live translations
"""

import sys
import os

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Header, Footer, Static, RichLog, Input
from textual.binding import Binding
from textual.reactive import reactive
from textual import events
from rich.text import Text
from rich.markdown import Markdown
from rich.panel import Panel

from terminal_translator.shell_manager import ShellManager
from terminal_translator.knowledge_base import lookup, get_pattern_count
from terminal_translator.ai_translator import translate_with_ai

import asyncio


class TranslationPanel(Static):
    """Panel showing translations of terminal content"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "Translation"
    
    def update_translation(self, text: str, source: str = "local", pattern: str = None):
        """Update the translation display"""
        source_badge = "[green]Knowledge Base[/]" if source == "local" else "[magenta]AI (GPT-5.2)[/]"
        
        content = f"{source_badge}\n\n{text}"
        if pattern:
            content += f"\n\n[dim]Matched: {pattern}[/]"
        
        self.update(content)


class ShellPane(RichLog):
    """Interactive shell pane with PTY integration"""
    
    def __init__(self, **kwargs):
        super().__init__(highlight=True, markup=True, **kwargs)
        self.border_title = "Terminal"


class CommandInput(Input):
    """Command input field"""
    
    def __init__(self, **kwargs):
        super().__init__(placeholder="Type a command and press Enter...", **kwargs)


class TerminalTranslatorApp(App):
    """Main Terminal Translator Application"""
    
    CSS_PATH = "styles.tcss"
    TITLE = "Terminal Translator"
    SUB_TITLE = "Plain English for your command line"
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+b", "toggle_mode", "Toggle Mode"),
        Binding("ctrl+l", "clear_terminal", "Clear"),
        Binding("ctrl+t", "toggle_translation", "Toggle Panel"),
    ]
    
    # Reactive state
    mode = reactive("beginner")
    translation_visible = reactive(True)
    pattern_count = reactive(0)
    
    def __init__(self):
        super().__init__()
        self.shell_manager = None
        self.current_command = ""
        self.command_history = []
        self.history_index = -1
    
    def compose(self) -> ComposeResult:
        """Compose the UI layout"""
        yield Header()
        
        with Horizontal(id="main-container"):
            # Left pane - Terminal
            with Vertical(id="terminal-pane"):
                yield ShellPane(id="shell-output")
                yield CommandInput(id="command-input")
            
            # Right pane - Translation
            with Vertical(id="translation-pane"):
                yield Static(id="mode-indicator")
                yield TranslationPanel(id="translation-output")
                yield Static(id="stats", classes="stats-bar")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the app on mount"""
        self.pattern_count = get_pattern_count()
        
        # Update mode indicator
        self.update_mode_indicator()
        
        # Update stats
        stats = self.query_one("#stats", Static)
        stats.update(f"[dim]{self.pattern_count} patterns in knowledge base[/]")
        
        # Initialize shell
        self.shell_manager = ShellManager(self.on_shell_output)
        await self.shell_manager.start()
        
        # Show welcome message
        shell_output = self.query_one("#shell-output", ShellPane)
        shell_output.write(Text.from_markup(
            "[bold green]Terminal Translator[/] [dim]v1.0.0[/]\n"
            "[dim]Type commands below. Translations appear on the right.[/]\n"
            "[dim]Press Ctrl+B to toggle Beginner/Familiar mode, Ctrl+Q to quit.[/]\n\n"
        ))
        
        # Focus on input
        self.query_one("#command-input", CommandInput).focus()
    
    def update_mode_indicator(self):
        """Update the mode indicator display"""
        indicator = self.query_one("#mode-indicator", Static)
        if self.mode == "beginner":
            indicator.update("[on green] BEGINNER MODE [/] [dim]Detailed explanations[/]")
        else:
            indicator.update("[on blue] FAMILIAR MODE [/] [dim]Concise explanations[/]")
    
    def watch_mode(self, new_mode: str) -> None:
        """React to mode changes"""
        self.update_mode_indicator()
    
    async def on_shell_output(self, output: str) -> None:
        """Handle output from the shell"""
        if not output.strip():
            return
        
        # Display in shell pane
        shell_output = self.query_one("#shell-output", ShellPane)
        shell_output.write(output)
        
        # Translate the output
        await self.translate_text(output)
    
    async def translate_text(self, text: str) -> None:
        """Translate text and update the translation panel"""
        if not text.strip():
            return
        
        translation_panel = self.query_one("#translation-output", TranslationPanel)
        
        # Try local knowledge base first
        result = lookup(text, self.mode)
        
        if result:
            translation_panel.update_translation(
                result["explanation"],
                source="local",
                pattern=result.get("matched_pattern")
            )
        else:
            # Show loading state
            translation_panel.update("[dim]Asking AI...[/]")
            
            # Fall back to AI
            try:
                ai_result = await translate_with_ai(text, self.mode)
                if ai_result.get("error"):
                    translation_panel.update_translation(
                        ai_result["explanation"],
                        source="error"
                    )
                else:
                    translation_panel.update_translation(
                        ai_result["explanation"],
                        source="ai"
                    )
            except Exception as e:
                translation_panel.update_translation(
                    f"Could not get AI translation: {str(e)}",
                    source="error"
                )
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission"""
        command = event.value.strip()
        if not command:
            return
        
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Clear input
        event.input.value = ""
        
        # Display command in shell
        shell_output = self.query_one("#shell-output", ShellPane)
        shell_output.write(Text.from_markup(f"[bold cyan]$ {command}[/]\n"))
        
        # Translate the command itself
        await self.translate_text(command)
        
        # Send to shell
        if self.shell_manager:
            await self.shell_manager.send_command(command)
    
    async def on_key(self, event: events.Key) -> None:
        """Handle key events for command history"""
        input_widget = self.query_one("#command-input", CommandInput)
        
        if event.key == "up" and self.command_history:
            # Navigate history up
            if self.history_index > 0:
                self.history_index -= 1
                input_widget.value = self.command_history[self.history_index]
                input_widget.cursor_position = len(input_widget.value)
        
        elif event.key == "down" and self.command_history:
            # Navigate history down
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                input_widget.value = self.command_history[self.history_index]
                input_widget.cursor_position = len(input_widget.value)
            else:
                self.history_index = len(self.command_history)
                input_widget.value = ""
    
    def action_toggle_mode(self) -> None:
        """Toggle between beginner and familiar mode"""
        self.mode = "familiar" if self.mode == "beginner" else "beginner"
        self.notify(f"Switched to {self.mode.title()} mode")
    
    def action_clear_terminal(self) -> None:
        """Clear the terminal output"""
        shell_output = self.query_one("#shell-output", ShellPane)
        shell_output.clear()
        self.notify("Terminal cleared")
    
    def action_toggle_translation(self) -> None:
        """Toggle translation panel visibility"""
        panel = self.query_one("#translation-pane")
        panel.display = not panel.display
        self.notify("Translation panel " + ("shown" if panel.display else "hidden"))
    
    async def on_unmount(self) -> None:
        """Cleanup on exit"""
        if self.shell_manager:
            await self.shell_manager.stop()


def main():
    """Main entry point"""
    app = TerminalTranslatorApp()
    app.run()


if __name__ == "__main__":
    main()
