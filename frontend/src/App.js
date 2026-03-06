import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'sonner';

import { Navbar } from './components/Navbar';
import { TerminalInput } from './components/TerminalInput';
import { TranslationPanel } from './components/TranslationPanel';
import { GitAnalyzer } from './components/GitAnalyzer';
import { ModeToggle } from './components/ModeToggle';

import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('terminal');
  const [mode, setMode] = useState('beginner');
  const [isLoading, setIsLoading] = useState(false);
  const [translationResult, setTranslationResult] = useState(null);
  const [patternCount, setPatternCount] = useState(0);

  // Fetch knowledge base stats on mount
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/knowledge-base/stats`);
        setPatternCount(response.data.total_patterns);
      } catch (error) {
        console.error('Failed to fetch KB stats:', error);
      }
    };
    fetchStats();
  }, []);

  // Load saved mode preference
  useEffect(() => {
    const savedMode = localStorage.getItem('translator-mode');
    if (savedMode === 'beginner' || savedMode === 'familiar') {
      setMode(savedMode);
    }
  }, []);

  const handleModeChange = (newMode) => {
    setMode(newMode);
    localStorage.setItem('translator-mode', newMode);
    toast.success(`Switched to ${newMode === 'beginner' ? 'Beginner' : 'Familiar'} mode`);
  };

  const handleTranslate = async (text) => {
    setIsLoading(true);
    setTranslationResult(null);

    try {
      const response = await axios.post(`${API}/translate`, {
        text,
        mode
      });
      setTranslationResult(response.data);
      
      // Show toast based on source
      if (response.data.source === 'local') {
        toast.success(`Found in knowledge base (${response.data.lookup_time_ms?.toFixed(2)}ms)`);
      } else if (response.data.source === 'ai') {
        toast.success('Translated with AI');
      }
    } catch (error) {
      console.error('Translation error:', error);
      toast.error('Failed to translate. Please try again.');
      setTranslationResult({
        explanation: 'An error occurred while translating. Please check your connection and try again.',
        source: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-dark grid-pattern" data-testid="dashboard">
      <Navbar 
        activeTab={activeTab} 
        onTabChange={setActiveTab}
        patternCount={patternCount}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Mode Toggle */}
        <div className="flex justify-center mb-6">
          <ModeToggle mode={mode} onModeChange={handleModeChange} />
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'terminal' ? (
            <motion.div
              key="terminal"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
              style={{ minHeight: 'calc(100vh - 200px)' }}
            >
              {/* Terminal Input */}
              <div className="bg-surface/30 rounded-2xl p-6 border border-white/5">
                <TerminalInput
                  onTranslate={handleTranslate}
                  isLoading={isLoading}
                  mode={mode}
                />
              </div>

              {/* Translation Output */}
              <TranslationPanel
                result={translationResult}
                isLoading={isLoading}
              />
            </motion.div>
          ) : (
            <motion.div
              key="github"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="bg-surface/30 rounded-2xl p-6 border border-white/5"
              style={{ minHeight: 'calc(100vh - 200px)' }}
            >
              <GitAnalyzer mode={mode} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

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
        <Route path="/*" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
