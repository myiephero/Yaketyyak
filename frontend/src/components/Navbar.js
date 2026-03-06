import { Terminal, GitBranch, Database, Settings } from 'lucide-react';
import { motion } from 'framer-motion';

export const Navbar = ({ activeTab, onTabChange, patternCount }) => {
  const tabs = [
    { id: 'terminal', label: 'Terminal', icon: Terminal },
    { id: 'github', label: 'Git Analyzer', icon: GitBranch },
  ];

  return (
    <nav 
      className="border-b border-white/5 bg-surface-dark/80 backdrop-blur-md sticky top-0 z-50"
      data-testid="navbar"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-neon-purple/20 flex items-center justify-center">
              <Terminal className="w-5 h-5 text-neon-purple" />
            </div>
            <div>
              <h1 className="font-heading font-bold text-lg text-slate-100">
                Terminal Translator
              </h1>
              <p className="text-xs text-slate-500 hidden sm:block">
                Plain English for your command line
              </p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex items-center gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface-highlight/50'
                }`}
                data-testid={`tab-${tab.id}`}
              >
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="tab-indicator"
                    className="absolute inset-0 bg-surface rounded-lg"
                    initial={false}
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                )}
                <tab.icon className="w-4 h-4 relative z-10" />
                <span className="relative z-10 hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-4">
            {/* Knowledge Base Stats */}
            <div 
              className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-surface rounded-lg border border-white/5"
              data-testid="kb-stats"
            >
              <Database className="w-4 h-4 text-neon-green" />
              <span className="text-xs text-slate-400">
                <span className="text-slate-200 font-medium">{patternCount}</span> patterns
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
