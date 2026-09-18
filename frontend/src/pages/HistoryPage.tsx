import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Clock, Trash2, Eye } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { apiService } from '../services/api';
import type { ResearchRunSummary } from '../types';

export const HistoryPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [runs, setRuns] = useState<ResearchRunSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchRuns = async () => {
    setIsLoading(true);
    try {
      const data = await apiService.listResearch({ search: searchQuery });
      setRuns(data);
    } catch (error) {
      console.error('Failed to fetch run history', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this run and all associated sources/bookmarks?')) return;
    try {
      await apiService.deleteResearch(id);
      setRuns(runs.filter(r => r.id !== id));
    } catch (err) {
      console.error('Failed to delete run', err);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white font-display">Research History</h1>

      <div className="flex gap-2">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search topics..."
          className="flex-1 px-4 py-2 rounded-lg bg-background border border-surface-border focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 text-white placeholder-slate-600 text-sm"
        />
        <Button onClick={fetchRuns} icon={<Search className="w-4 h-4" />}>
          Search
        </Button>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-500">Loading history...</div>
      ) : runs.length === 0 ? (
        <div className="text-center py-12 glass-panel rounded-xl">
          <Clock className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <p>No research runs found</p>
        </div>
      ) : (
        <div className="space-y-3">
          {runs.map((run, idx) => (
            <motion.div
              key={run.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.03 }}
              className="glass-panel p-5 rounded-xl hover:glass-panel-elevated transition-all group"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-white group-hover:text-indigo-300 transition-colors">
                    {run.topic}
                  </h3>
                  <div className="flex items-center gap-3 mt-2">
                    <Badge status={run.status} size="sm" />
                    <span className="text-xs text-slate-500">
                      {run.depth} • {run.tone}
                    </span>
                    {run.final_score && (
                      <span className="text-xs font-mono px-2 py-0.5 bg-emerald-900/30 text-emerald-400 rounded">
                        {run.final_score}/10
                      </span>
                    )}
                    <span className="text-xs text-slate-500 font-mono">
                      Rev: {run.revision_count}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm">
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(run.id)}
                    className="text-rose-500 hover:text-rose-400 hover:bg-rose-900/20"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-surface-border flex justify-between text-xs text-slate-500">
                <span>ID: {run.id}</span>
                <span>Words: {run.total_words} • Sources: {run.sources_count}</span>
                <span>{new Date(run.created_at).toLocaleString()}</span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};
