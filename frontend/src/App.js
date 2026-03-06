import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Terminal, 
  Download, 
  Apple, 
  Monitor,
  Laptop,
  CheckCircle,
  Sparkles,
  Zap,
  BookOpen,
  Github,
  ChevronRight,
  Database,
  Cpu
} from 'lucide-react';
import { Toaster, toast } from 'sonner';

import './App.css';

// Detect user's OS
const getOS = () => {
  const userAgent = window.navigator.userAgent;
  if (userAgent.includes('Mac')) return 'macos';
  if (userAgent.includes('Win')) return 'windows';
  if (userAgent.includes('Linux')) return 'linux';
  return 'unknown';
};

const features = [
  {
    icon: Terminal,
    title: "Real Terminal Integration",
    description: "Not a copy-paste tool. A real shell runs inside, and translations appear as you type."
  },
  {
    icon: Database,
    title: "70+ Built-in Patterns",
    description: "Instant explanations for git, npm, python, docker, and common errors. No internet needed."
  },
  {
    icon: Cpu,
    title: "AI Fallback",
    description: "When the knowledge base doesn't know something, GPT-5.2 steps in automatically."
  },
  {
    icon: BookOpen,
    title: "Beginner & Familiar Modes",
    description: "Toggle between detailed explanations with analogies, or concise technical summaries."
  },
  {
    icon: Zap,
    title: "Zero Configuration",
    description: "Download, open, and start learning. No API keys, no setup, no accounts."
  },
  {
    icon: Sparkles,
    title: "Beautiful TUI",
    description: "Split-pane interface with the shell on one side, translations on the other."
  }
];

const downloadLinks = {
  macos: "https://github.com/myiephero/yakkityyak/releases/latest/download/TerminalTranslator-macos",
  windows: "https://github.com/myiephero/yakkityyak/releases/latest/download/TerminalTranslator-windows.exe",
  linux: "https://github.com/myiephero/yakkityyak/releases/latest/download/TerminalTranslator-linux"
};

const osLabels = {
  macos: { name: "macOS", icon: Apple },
  windows: { name: "Windows", icon: Monitor },
  linux: { name: "Linux", icon: Laptop }
};

const DownloadButton = ({ os, primary = false }) => {
  const { name, icon: Icon } = osLabels[os] || { name: os, icon: Download };
  
  return (
    <motion.a
      href={downloadLinks[os]}
      className={`flex items-center gap-3 px-6 py-4 rounded-xl font-medium transition-colors ${
        primary 
          ? 'bg-neon-purple text-white hover:bg-neon-purple/90 shadow-glow' 
          : 'bg-surface border border-white/10 text-slate-200 hover:bg-surface-highlight'
      }`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      data-testid={`download-${os}`}
    >
      <Icon className="w-5 h-5" />
      <span>Download for {name}</span>
      <ChevronRight className="w-4 h-4 opacity-50" />
    </motion.a>
  );
};

const LandingPage = () => {
  const [detectedOS, setDetectedOS] = useState('macos');

  useEffect(() => {
    setDetectedOS(getOS());
  }, []);

  const otherOS = Object.keys(osLabels).filter(os => os !== detectedOS);

  return (
    <div className="min-h-screen bg-surface-dark" data-testid="landing-page">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background grid */}
        <div className="absolute inset-0 grid-pattern opacity-30" />
        
        {/* Glow effect */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-neon-purple/20 rounded-full blur-[120px]" />
        
        <div className="relative max-w-6xl mx-auto px-6 pt-20 pb-32">
          {/* Nav */}
          <nav className="flex items-center justify-between mb-20">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-neon-purple/20 flex items-center justify-center">
                <Terminal className="w-6 h-6 text-neon-purple" />
              </div>
              <span className="font-heading font-bold text-xl text-slate-100">
                Terminal Translator
              </span>
            </div>
            
            <a 
              href="https://github.com/myiephero/yakkityyak"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-surface/50 border border-white/10 text-slate-300 hover:text-white transition-colors"
              data-testid="github-link"
            >
              <Github className="w-4 h-4" />
              <span className="hidden sm:inline">View on GitHub</span>
            </a>
          </nav>

          {/* Hero Content */}
          <div className="text-center max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-neon-green/10 border border-neon-green/20 text-neon-green text-sm mb-8">
                <CheckCircle className="w-4 h-4" />
                Free & Open Source
              </div>
              
              <h1 className="font-heading text-5xl sm:text-6xl lg:text-7xl font-bold text-slate-100 mb-6 leading-tight">
                Google Translate for{' '}
                <span className="text-neon-purple">Your Terminal</span>
              </h1>
              
              <p className="text-lg sm:text-xl text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed">
                A split-pane app that shows real-time, plain-English explanations 
                as you use the command line. No copy-paste needed — it just works.
              </p>
            </motion.div>

            {/* Download Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8"
            >
              <DownloadButton os={detectedOS} primary />
            </motion.div>

            {/* Other OS options */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="flex items-center justify-center gap-4 text-sm text-slate-500"
            >
              <span>Also available for:</span>
              {otherOS.map(os => (
                <a 
                  key={os}
                  href={downloadLinks[os]}
                  className="text-slate-400 hover:text-neon-purple transition-colors underline underline-offset-2"
                >
                  {osLabels[os].name}
                </a>
              ))}
            </motion.div>
          </div>

          {/* App Preview */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="mt-20 relative"
          >
            <div className="relative bg-terminal-bg rounded-2xl border border-white/10 shadow-2xl overflow-hidden">
              {/* Window chrome */}
              <div className="flex items-center gap-2 px-4 py-3 bg-surface border-b border-white/5">
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-neon-rose/80" />
                  <div className="w-3 h-3 rounded-full bg-neon-amber/80" />
                  <div className="w-3 h-3 rounded-full bg-neon-green/80" />
                </div>
                <span className="text-xs text-slate-500 ml-2 font-mono">Terminal Translator</span>
              </div>
              
              {/* Split pane preview */}
              <div className="grid grid-cols-1 md:grid-cols-2 divide-x divide-white/5">
                {/* Terminal side */}
                <div className="p-6 font-mono text-sm">
                  <p className="text-slate-500 mb-4"># Type commands here</p>
                  <p className="text-neon-green mb-2">$ <span className="text-slate-200">git push origin main</span></p>
                  <p className="text-slate-400 text-xs mt-4">
                    Enumerating objects: 5, done.<br />
                    Counting objects: 100% (5/5), done.<br />
                    Writing objects: 100% (3/3), 328 bytes | 328.00 KiB/s, done.
                  </p>
                </div>
                
                {/* Translation side */}
                <div className="p-6 bg-surface/30">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="px-2 py-1 rounded bg-neon-green/10 text-neon-green text-xs">Knowledge Base</span>
                    <span className="text-xs text-slate-500">0.02ms</span>
                  </div>
                  <p className="text-slate-300 leading-relaxed">
                    This uploads your saved changes (commits) to the internet (like GitHub). 
                    It's like syncing your local photo album to the cloud so others can see 
                    your photos. Your teammates will be able to see your changes after you push.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-surface/50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="font-heading text-3xl sm:text-4xl font-bold text-slate-100 mb-4">
              Built for Beginners, Useful for Everyone
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Whether you're opening a terminal for the first time or you just want 
              quick reminders, Terminal Translator has you covered.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-2xl bg-surface border border-white/5 hover:border-neon-purple/30 transition-colors"
              >
                <div className="w-12 h-12 rounded-xl bg-neon-purple/10 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-neon-purple" />
                </div>
                <h3 className="font-heading font-semibold text-lg text-slate-100 mb-2">
                  {feature.title}
                </h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="font-heading text-3xl sm:text-4xl font-bold text-slate-100 mb-6">
            Ready to Stop Googling Error Messages?
          </h2>
          <p className="text-slate-400 mb-10 max-w-xl mx-auto">
            Download Terminal Translator and get instant explanations as you learn. 
            It's free, open source, and works offline.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <DownloadButton os={detectedOS} primary />
            <a 
              href="https://github.com/myiephero/yakkityyak"
              className="flex items-center gap-2 px-6 py-4 rounded-xl font-medium bg-surface border border-white/10 text-slate-200 hover:bg-surface-highlight transition-colors"
            >
              <Github className="w-5 h-5" />
              <span>View Source</span>
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/5">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Terminal className="w-5 h-5 text-neon-purple" />
              <span className="text-slate-400">Terminal Translator</span>
            </div>
            <p className="text-sm text-slate-500">
              Open source · MIT License · Made for beginners
            </p>
          </div>
        </div>
      </footer>

      <Toaster 
        position="bottom-right"
        theme="dark"
        toastOptions={{
          style: {
            background: '#1e293b',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            color: '#f8fafc',
          },
        }}
      />
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/*" element={<LandingPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
