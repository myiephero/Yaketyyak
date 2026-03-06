"""Terminal Translator - A Google Translate for your Terminal"""

from terminal_translator.main import main, TerminalTranslatorApp
from terminal_translator.knowledge_base import lookup, get_pattern_count

__version__ = "1.0.0"
__all__ = ["main", "TerminalTranslatorApp", "lookup", "get_pattern_count"]
