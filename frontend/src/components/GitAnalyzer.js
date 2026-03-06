import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  GitBranch, 
  Star, 
  GitFork, 
  Eye, 
  AlertCircle, 
  Users, 
  Scale, 
  Calendar,
  ExternalLink,
  Search,
  Loader2,
  Check,
  X,
  Tag,
  FileText,
  MessageSquare
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StatCard = ({ icon: Icon, label, value, subValue, color = 'text-slate-400' }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className="stat-card bg-surface/50 border border-white/5 rounded-xl p-4"
    data-testid={`stat-${label.toLowerCase().replace(/\s/g, '-')}`}
  >
    <div className="flex items-start justify-between mb-2">
      <Icon className={`w-5 h-5 ${color}`} />
      {subValue && (
        <span className="text-xs text-slate-500">{subValue}</span>
      )}
    </div>
    <p className="text-2xl font-heading font-bold text-slate-100 mb-1">{value}</p>
    <p className="text-xs text-slate-500">{label}</p>
  </motion.div>
);

const QualityBadge = ({ tier, tierLabel, score }) => {
  const tierClasses = {
    excellent: 'tier-excellent',
    good: 'tier-good',
    fair: 'tier-fair',
    caution: 'tier-caution',
  };

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full ${tierClasses[tier] || tierClasses.fair}`}>
      <span className="font-medium">{tierLabel}</span>
      <span className="text-xs opacity-75">({score}/100)</span>
    </div>
  );
};

export const GitAnalyzer = ({ mode }) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (e) => {
    e?.preventDefault();
    if (!url.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API}/github/analyze`, {
        url: url.trim(),
        mode
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze repository');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleAnalyze(e);
    }
  };

  return (
    <div className="h-full flex flex-col" data-testid="git-analyzer">
      {/* URL Input Section */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <GitBranch className="w-6 h-6 text-neon-purple" />
          <h2 className="font-heading text-xl font-semibold text-slate-100">
            Git Repository Translator
          </h2>
        </div>
        <p className="text-sm text-slate-400 mb-6">
          Paste a GitHub repository URL to get a plain-English analysis with quality metrics
        </p>

        <form onSubmit={handleAnalyze} className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="https://github.com/owner/repository"
              className="w-full pl-12 pr-4 py-3 bg-surface border border-white/10 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-neon-purple/50 focus:border-neon-purple/50 transition-colors"
              data-testid="github-url-input"
              disabled={isLoading}
            />
          </div>
          <motion.button
            type="submit"
            disabled={!url.trim() || isLoading}
            className="px-6 py-3 bg-neon-purple rounded-xl font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed btn-hover-lift flex items-center gap-2"
            whileHover={{ scale: url.trim() && !isLoading ? 1.02 : 1 }}
            whileTap={{ scale: 0.98 }}
            data-testid="analyze-btn"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              'Analyze'
            )}
          </motion.button>
        </form>
      </div>

      {/* Results Section */}
      <div className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">
          {error && (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-neon-rose/10 border border-neon-rose/20 rounded-xl p-4 flex items-start gap-3"
              data-testid="error-message"
            >
              <AlertCircle className="w-5 h-5 text-neon-rose flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-neon-rose">Analysis Failed</p>
                <p className="text-sm text-slate-400 mt-1">{error}</p>
              </div>
            </motion.div>
          )}

          {isLoading && !result && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4"
            >
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-24 shimmer rounded-xl" />
                ))}
              </div>
              <div className="h-40 shimmer rounded-xl" />
            </motion.div>
          )}

          {result && (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              {/* Repo Header */}
              <div className="glass rounded-xl p-6" data-testid="repo-header">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    {result.owner?.avatar_url && (
                      <img
                        src={result.owner.avatar_url}
                        alt={result.owner.login}
                        className="w-12 h-12 rounded-full border-2 border-white/10"
                      />
                    )}
                    <div>
                      <h3 className="font-heading text-xl font-bold text-slate-100">
                        {result.repo?.full_name}
                      </h3>
                      <p className="text-sm text-slate-400">
                        {result.repo?.description || 'No description'}
                      </p>
                    </div>
                  </div>
                  <a
                    href={result.repo?.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-lg hover:bg-surface-highlight transition-colors"
                    data-testid="repo-link"
                  >
                    <ExternalLink className="w-5 h-5 text-slate-400" />
                  </a>
                </div>

                {/* Quality Assessment */}
                <div className="flex items-center gap-4">
                  <QualityBadge
                    tier={result.assessment?.tier}
                    tierLabel={result.assessment?.tier_label}
                    score={result.assessment?.score}
                  />
                  {result.repo?.language && (
                    <span className="px-3 py-1 bg-surface rounded-full text-xs text-slate-300">
                      {result.repo.language}
                    </span>
                  )}
                  {result.meta?.is_archived && (
                    <span className="px-3 py-1 bg-neon-amber/10 text-neon-amber rounded-full text-xs">
                      Archived
                    </span>
                  )}
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  icon={Star}
                  label="Stars"
                  value={result.stats?.stars_formatted}
                  color="text-neon-amber"
                />
                <StatCard
                  icon={GitFork}
                  label="Forks"
                  value={result.stats?.forks_formatted}
                  color="text-neon-green"
                />
                <StatCard
                  icon={Eye}
                  label="Watchers"
                  value={result.stats?.watchers_formatted}
                  color="text-neon-purple"
                />
                <StatCard
                  icon={AlertCircle}
                  label="Open Issues"
                  value={result.stats?.open_issues}
                  color="text-neon-rose"
                />
              </div>

              {/* Additional Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  icon={Users}
                  label="Contributors"
                  value={result.stats?.contributors_formatted}
                  color="text-slate-400"
                />
                <StatCard
                  icon={Scale}
                  label="License"
                  value={result.meta?.license || 'None'}
                  color="text-slate-400"
                />
                <StatCard
                  icon={Calendar}
                  label="Last Updated"
                  value={result.repo?.updated_at ? new Date(result.repo.updated_at).toLocaleDateString() : 'N/A'}
                  color="text-slate-400"
                />
                <StatCard
                  icon={Tag}
                  label="Latest Release"
                  value={result.meta?.latest_release?.tag || 'N/A'}
                  color="text-slate-400"
                />
              </div>

              {/* Features */}
              <div className="glass rounded-xl p-4">
                <p className="text-xs text-slate-500 mb-3">Features</p>
                <div className="flex flex-wrap gap-2">
                  {result.meta?.has_wiki && (
                    <span className="px-2.5 py-1 bg-surface rounded-lg text-xs text-slate-300 flex items-center gap-1.5">
                      <FileText className="w-3 h-3" /> Wiki
                    </span>
                  )}
                  {result.meta?.has_pages && (
                    <span className="px-2.5 py-1 bg-surface rounded-lg text-xs text-slate-300 flex items-center gap-1.5">
                      <ExternalLink className="w-3 h-3" /> Pages
                    </span>
                  )}
                  {result.meta?.has_discussions && (
                    <span className="px-2.5 py-1 bg-surface rounded-lg text-xs text-slate-300 flex items-center gap-1.5">
                      <MessageSquare className="w-3 h-3" /> Discussions
                    </span>
                  )}
                  {result.repo?.topics?.map((topic) => (
                    <span key={topic} className="px-2.5 py-1 bg-neon-purple/10 text-neon-purple rounded-lg text-xs">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>

              {/* Assessment Details */}
              {result.assessment && (
                <div className="glass rounded-xl p-6">
                  <h4 className="font-heading font-semibold text-slate-200 mb-4">Quality Assessment</h4>
                  
                  {result.assessment.reasons?.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs text-slate-500 mb-2">Positive Indicators</p>
                      <ul className="space-y-2">
                        {result.assessment.reasons.map((reason, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                            <Check className="w-4 h-4 text-neon-green flex-shrink-0 mt-0.5" />
                            {reason}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {result.assessment.warnings?.length > 0 && (
                    <div>
                      <p className="text-xs text-slate-500 mb-2">Considerations</p>
                      <ul className="space-y-2">
                        {result.assessment.warnings.map((warning, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                            <AlertCircle className="w-4 h-4 text-neon-amber flex-shrink-0 mt-0.5" />
                            {warning}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Summary */}
              <div className="glass rounded-xl p-6">
                <h4 className="font-heading font-semibold text-slate-200 mb-4">Summary</h4>
                <div className="markdown-content" data-testid="repo-summary">
                  <ReactMarkdown>{result.summary}</ReactMarkdown>
                </div>
              </div>
            </motion.div>
          )}

          {!result && !isLoading && !error && (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex flex-col items-center justify-center text-center py-16"
            >
              <div className="w-20 h-20 rounded-full bg-surface flex items-center justify-center mb-6">
                <GitBranch className="w-10 h-10 text-neon-purple/50" />
              </div>
              <h3 className="font-heading text-xl font-semibold text-slate-300 mb-3">
                Analyze Any Repository
              </h3>
              <p className="text-sm text-slate-500 max-w-md mb-6">
                Paste a GitHub URL above to get detailed metrics, quality assessment, and a plain-English explanation of what the repository is about.
              </p>
              <div className="flex flex-wrap justify-center gap-2 text-xs text-slate-600">
                <span className="px-3 py-1.5 bg-surface rounded-lg">Stars & Forks</span>
                <span className="px-3 py-1.5 bg-surface rounded-lg">License Info</span>
                <span className="px-3 py-1.5 bg-surface rounded-lg">Activity Status</span>
                <span className="px-3 py-1.5 bg-surface rounded-lg">Quality Score</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default GitAnalyzer;
