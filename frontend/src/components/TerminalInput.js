import { useState, useRef, useEffect } from 'react';
import { Terminal, Loader2, Copy, Check, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const TerminalInput = ({ onTranslate, isLoading, mode }) => {
  const [input, setInput] = useState('');
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef(null);

  // Example commands for placeholder rotation
  const examples = [
    'git commit -m "fix: resolve merge conflict"',
    'npm ERR! ERESOLVE unable to resolve dependency tree',
    'fatal: not a git repository',
    'docker build -t myapp:latest .',
    'ModuleNotFoundError: No module named "requests"',
    'permission denied: ./script.sh',
  ];

  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % examples.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onTranslate(input.trim());
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit(e);
    }
  };

  const handleClear = () => {
    setInput('');
    textareaRef.current?.focus();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(input);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="h-full flex flex-col" data-testid="terminal-input-container">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-neon-rose/80" />
            <div className="w-3 h-3 rounded-full bg-neon-amber/80" />
            <div className="w-3 h-3 rounded-full bg-neon-green/80" />
          </div>
          <span className="text-sm font-mono text-slate-400">terminal</span>
        </div>
        <div className="flex items-center gap-2">
          {input && (
            <>
              <button
                onClick={handleCopy}
                className="p-1.5 rounded-md hover:bg-surface-highlight transition-colors text-slate-400 hover:text-slate-200"
                data-testid="copy-input-btn"
              >
                {copied ? <Check className="w-4 h-4 text-neon-green" /> : <Copy className="w-4 h-4" />}
              </button>
              <button
                onClick={handleClear}
                className="p-1.5 rounded-md hover:bg-surface-highlight transition-colors text-slate-400 hover:text-slate-200"
                data-testid="clear-input-btn"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Terminal Area */}
      <form onSubmit={handleSubmit} className="flex-1 flex flex-col">
        <div className="flex-1 relative bg-terminal-bg rounded-xl border border-white/5 overflow-hidden shadow-inner">
          {/* Prompt indicator */}
          <div className="absolute top-4 left-4 flex items-center gap-2 pointer-events-none">
            <span className="text-neon-green font-mono text-sm">$</span>
          </div>
          
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={examples[placeholderIndex]}
            className="w-full h-full min-h-[200px] lg:min-h-[300px] bg-transparent terminal-input text-sm p-4 pl-8 resize-none focus:outline-none"
            data-testid="terminal-textarea"
            disabled={isLoading}
          />
          
          {/* Character count */}
          <div className="absolute bottom-3 right-3 text-xs text-slate-600 font-mono">
            {input.length} / 10000
          </div>
        </div>

        {/* Submit Button */}
        <div className="mt-4 flex items-center justify-between">
          <p className="text-xs text-slate-500">
            Press <kbd className="px-1.5 py-0.5 bg-surface rounded text-slate-400">⌘</kbd> + <kbd className="px-1.5 py-0.5 bg-surface rounded text-slate-400">Enter</kbd> to translate
          </p>
          
          <motion.button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex items-center gap-2 px-6 py-2.5 bg-neon-purple rounded-full font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed btn-hover-lift"
            whileHover={{ scale: input.trim() && !isLoading ? 1.02 : 1 }}
            whileTap={{ scale: 0.98 }}
            data-testid="translate-btn"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Translating...
              </>
            ) : (
              <>
                <Terminal className="w-4 h-4" />
                Translate
              </>
            )}
          </motion.button>
        </div>
      </form>
    </div>
  );
};

export default TerminalInput;
