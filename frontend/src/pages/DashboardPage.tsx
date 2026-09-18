import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, Search, Clock, FileText, Sparkles, TrendingUp, BarChart, Zap, Users, Globe, BookOpen } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { apiService } from '../services/api';
import type { ResearchRunSummary, DashboardStats } from '../types';
import { cn } from '../lib/utils';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentRuns, setRecentRuns] = useState<ResearchRunSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [statsData, runsData] = await Promise.all([
          apiService.getStats(),
          apiService.listResearch({ limit: 5 }),
        ]);
        setStats(statsData);
        setRecentRuns(runsData);
      } catch (error) {
        console.error('Failed to fetch dashboard data', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const statCards = [
    {
      title: 'Total Runs',
      value: stats?.total_runs ?? 0,
      icon: FileText,
      color: 'from-indigo-600 to-indigo-800',
      bg: 'bg-indigo-900/20',
    },
    {
      title: 'Completed',
      value: stats?.completed_runs ?? 0,
      icon: TrendingUp,
      color: 'from-emerald-600 to-emerald-800',
      bg: 'bg-emerald-900/20',
    },
    {
      title: 'Avg Score',
      value: stats?.avg_score ? stats.avg_score.toFixed(1) : '—',
      icon: BarChart,
      color: 'from-cyan-600 to-cyan-800',
      bg: 'bg-cyan-900/20',
    },
    {
      title: 'Avg Duration',
      value: stats?.avg_duration_seconds ? `${(stats.avg_duration_seconds / 60).toFixed(1)}m` : '—',
      icon: Clock,
      color: 'from-amber-600 to-amber-800',
      bg: 'bg-amber-900/20',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-2xl border border-surface-border bg-gradient-to-br from-surface-raised to-background p-8 shadow-elevated"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-indigo-500/5 to-cyan-500/5 blur-3xl" />
        <div className="relative flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <h1 className="text-3xl font-bold text-white font-display mb-2">
              AI‑Driven Research, <span className="text-indigo-400">Elevated</span>
            </h1>
            <p className="text-slate-400 max-w-2xl">
              Findly orchestrates multi‑source research with quality‑gate revision loops,
              grounded Q&A, and export‑ready reports—powered by LangGraph state machines.
              Zero boilerplate, premium UI.
            </p>
            <div className="flex flex-wrap gap-3 mt-6">
              <Button variant="primary" icon={<Sparkles className="w-4 h-4" />}>
                New Research Run
              </Button>
              <Button variant="outline" icon={<BookOpen className="w-4 h-4" />}>
                Read Docs
              </Button>
            </div>
          </div>
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Globe className="w-4 h-4" />
              <span>Tavily Search • Groq LLama‑3.3‑70B • BeautifulSoup</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Zap className="w-4 h-4" />
              <span>SSRF‑Protected Scraper • Quality Gate ≥7 • Max 3 Revisions</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Users className="w-4 h-4" />
              <span>React + Vite + TypeScript • Tailwind • Framer Motion</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, idx) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            className={cn(
              'rounded-xl border border-surface-border p-5 shadow-card',
              card.bg
            )}
          >
            <div className="flex items-center justify-between mb-3">
              <card.icon className="w-5 h-5 text-slate-400" />
              <div className={`h-0.5 w-12 rounded-full bg-gradient-to-r ${card.color}`} />
            </div>
            <p className="text-sm text-slate-400">{card.title}</p>
            <p className="text-2xl font-bold text-white mt-1">{card.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Recent Runs */}
      <div className="rounded-xl border border-surface-border bg-surface-raised/60 shadow-card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Recent Research Runs
          </h2>
          <Button variant="ghost" size="sm" icon={<ChevronRight className="w-4 h-4" />}>
            View All
          </Button>
        </div>

        {isLoading ? (
          <div className="text-center py-8 text-slate-500">Loading runs...</div>
        ) : recentRuns.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <Search className="w-12 h-12 mx-auto mb-4 opacity-40" />
            <p>No research runs yet. Start a new one!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recentRuns.map((run) => (
              <motion.div
                key={run.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="group glass-panel hover:glass-panel-elevated p-4 rounded-lg transition-all cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-white group-hover:text-indigo-300 transition-colors">
                      {run.topic}
                    </h3>
                    <div className="flex items-center gap-3 mt-1">
                      <Badge status={run.status} size="sm" />
                      <span className="text-xs text-slate-500">
                        {run.depth} • {run.tone}
                      </span>
                      {run.final_score && (
                        <span className="text-xs font-mono px-2 py-0.5 bg-emerald-900/30 text-emerald-400 rounded">
                          Score: {run.final_score}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-slate-400">
                      {new Date(run.created_at).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {run.total_words} words • {run.sources_count} sources
                    </p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-surface-border">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Revision #{run.revision_count}</span>
                    <span>Elapsed: {run.elapsed_seconds}s</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
