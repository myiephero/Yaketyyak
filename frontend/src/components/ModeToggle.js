import { motion } from 'framer-motion';
import { GraduationCap, Zap } from 'lucide-react';

export const ModeToggle = ({ mode, onModeChange }) => {
  return (
    <div 
      className="flex items-center bg-surface/80 p-1 rounded-full border border-white/10"
      data-testid="mode-toggle"
    >
      <button
        onClick={() => onModeChange('beginner')}
        className={`relative flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
          mode === 'beginner' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
        }`}
        data-testid="mode-beginner-btn"
      >
        {mode === 'beginner' && (
          <motion.div
            layoutId="mode-indicator"
            className="absolute inset-0 bg-neon-purple rounded-full"
            initial={false}
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          />
        )}
        <GraduationCap className="w-4 h-4 relative z-10" />
        <span className="relative z-10">Beginner</span>
      </button>
      
      <button
        onClick={() => onModeChange('familiar')}
        className={`relative flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
          mode === 'familiar' ? 'text-white' : 'text-slate-400 hover:text-slate-200'
        }`}
        data-testid="mode-familiar-btn"
      >
        {mode === 'familiar' && (
          <motion.div
            layoutId="mode-indicator"
            className="absolute inset-0 bg-neon-green rounded-full"
            initial={false}
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          />
        )}
        <Zap className="w-4 h-4 relative z-10" />
        <span className="relative z-10">Familiar</span>
      </button>
    </div>
  );
};

export default ModeToggle;
