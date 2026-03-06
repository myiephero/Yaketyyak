import { useState } from 'react';
import { Copy, Check, Sparkles, Database, Cpu, Clock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

export const TranslationPanel = ({ result, isLoading }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (result?.explanation) {
      navigator.clipboard.writeText(result.explanation);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getSourceInfo = () => {
    if (!result) return null;
    
    if (result.source === 'local') {
      return {
        icon: Database,
        label: 'Knowledge Base',
        color: 'text-neon-green',
        bgColor: 'bg-neon-green/10',
      };
    } else if (result.source === 'ai') {
      return {
        icon: Sparkles,
        label: result.model || 'AI',
        color: 'text-neon-purple',
        bgColor: 'bg-neon-purple/10',
      };
    } else if (result.source === 'error') {
      return {
        icon: Cpu,
        label: 'Error',
        color: 'text-neon-rose',
        bgColor: 'bg-neon-rose/10',
      };
    }
    return null;
  };

  const sourceInfo = getSourceInfo();

  return (
    <div 
      className="h-full flex flex-col glass rounded-xl overflow-hidden"
      data-testid="translation-panel"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/5">
        <div className="flex items-center gap-3">
          <Sparkles className="w-5 h-5 text-neon-purple" />
          <span className="font-heading font-semibold text-slate-200">Translation</span>
        </div>
        
        {result && (
          <div className="flex items-center gap-3">
            {/* Source badge */}
            {sourceInfo && (
              <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full ${sourceInfo.bgColor}`}>
                <sourceInfo.icon className={`w-3.5 h-3.5 ${sourceInfo.color}`} />
                <span className={`text-xs font-medium ${sourceInfo.color}`}>
                  {sourceInfo.label}
                </span>
              </div>
            )}
            
            {/* Lookup time for local results */}
            {result.lookup_time_ms != null && (
              <div className="flex items-center gap-1 text-xs text-slate-500">
                <Clock className="w-3 h-3" />
                {Number(result.lookup_time_ms).toFixed(2)}ms
              </div>
            )}
            
            {/* Copy button */}
            <button
              onClick={handleCopy}
              className="p-1.5 rounded-md hover:bg-surface-highlight transition-colors text-slate-400 hover:text-slate-200"
              data-testid="copy-translation-btn"
            >
              {copied ? (
                <Check className="w-4 h-4 text-neon-green" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4"
            >
              <div className="h-4 shimmer rounded w-3/4" />
              <div className="h-4 shimmer rounded w-full" />
              <div className="h-4 shimmer rounded w-5/6" />
              <div className="h-4 shimmer rounded w-2/3" />
            </motion.div>
          ) : result ? (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="markdown-content"
              data-testid="translation-content"
            >
              <ReactMarkdown>{result.explanation}</ReactMarkdown>
              
              {/* Matched pattern info */}
              {result.matched_pattern && (
                <div className="mt-6 pt-4 border-t border-white/5">
                  <p className="text-xs text-slate-500">
                    Matched pattern: <code className="text-neon-purple">{result.matched_pattern}</code>
                  </p>
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex flex-col items-center justify-center text-center"
            >
              <div className="w-16 h-16 rounded-full bg-surface flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 text-neon-purple/50" />
              </div>
              <h3 className="font-heading text-lg font-semibold text-slate-300 mb-2">
                Ready to Translate
              </h3>
              <p className="text-sm text-slate-500 max-w-xs">
                Paste any terminal command, error message, or output on the left to get a plain-English explanation.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default TranslationPanel;
