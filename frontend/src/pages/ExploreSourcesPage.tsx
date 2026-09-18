import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Globe, ChevronDown, ExternalLink } from 'lucide-react';
import { Badge } from '../components/common/Badge';
import { apiService } from '../services/api';
import type { ResearchRunSummary, SourceItem } from '../types';
import { cn } from '../lib/utils';

export const ExploreSourcesPage: React.FC = () => {
  const [runs, setRuns] = useState<ResearchRunSummary[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [expandedSource, setExpandedSource] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const runsData = await apiService.listResearch();
        setRuns(runsData);
        if (runsData.length > 0) {
          setSelectedRunId(runsData[0].id);
          const detail = await apiService.getResearch(runsData[0].id);
          setSources(detail.sources || []);
        }
      } catch (err) {
        console.error('Failed to load sources explorer', err);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const handleRunSelect = async (runId: string) => {
    setSelectedRunId(runId);
    setExpandedSource(null);
    try {
      const detail = await apiService.getResearch(runId);
      setSources(detail.sources || []);
    } catch (err) {
      console.error('Failed to load run detail', err);
    }
  };

  const filteredSources = sources.filter(s => s.run_id === selectedRunId);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white font-display">Source Explorer</h1>
        <div className="flex items-center gap-2">
          <select
            value={selectedRunId ?? ''}
            onChange={(e) => handleRunSelect(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-surface-raised border border-surface-border text-sm text-slate-300 focus:border-indigo-500"
          >
            {runs.map(r => (
              <option key={r.id} value={r.id}>
                {r.topic.slice(0, 40)}{r.topic.length > 40 ? '...' : ''}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-500">Loading sources...</div>
      ) : filteredSources.length === 0 ? (
        <div className="text-center py-16 glass-panel rounded-xl">
          <Globe className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">No sources for this run yet</p>
          <p className="text-sm text-slate-600 mt-1">
            Sources appear as the research pipeline searches and scrapes.
          </p>
        </div>
      ) : (
        <div className="glass-panel rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border text-left text-xs uppercase tracking-wider text-slate-500">
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Source</th>
                  <th className="px-4 py-3">Domain</th>
                  <th className="px-4 py-3 text-right">Rel.</th>
                  <th className="px-4 py-3 text-right">Chars</th>
                  <th className="px-4 py-3 text-right">Content</th>
                </tr>
              </thead>
              <tbody>
                {filteredSources.map((source) => {
                  const isExpanded = expandedSource === source.id;
                  return (
                    <React.Fragment key={source.id}>
                      <motion.tr
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className={cn(
                          'border-b border-surface-border/50 cursor-pointer hover:bg-surface-hover/60 transition-colors',
                          isExpanded && 'bg-surface-hover/40'
                        )}
                        onClick={() => setExpandedSource(isExpanded ? null : source.id)}
                      >
                        <td className="px-4 py-3">
                          <Badge status={source.status} size="sm" />
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <span className="text-slate-300 font-medium max-w-[280px] truncate">
                              {source.title || source.url}
                            </span>
                            {source.error_reason && (
                              <span className="text-xs text-rose-400 truncate max-w-[140px]">
                                {source.error_reason}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-slate-500 font-mono text-xs">
                          {source.domain}
                        </td>
                        <td className="px-4 py-3 text-right text-slate-400 font-mono">
                          {source.relevance_score != null ? `${source.relevance_score.toFixed(2)}` : '—'}
                        </td>
                        <td className="px-4 py-3 text-right text-slate-500 font-mono">
                          {source.char_count?.toLocaleString() ?? '0'}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <ChevronDown
                            className={cn(
                              'w-4 h-4 inline-block text-slate-400 transition-transform',
                              isExpanded && 'rotate-180'
                            )}
                          />
                        </td>
                      </motion.tr>

                      {isExpanded && (
                        <motion.tr
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                        >
                          <td colSpan={6} className="px-4 py-4 bg-surface-hover/30">
                            <div className="space-y-3">
                              {source.snippet && (
                                <div>
                                  <p className="text-xs uppercase tracking-wider text-slate-500 mb-1">
                                    Snippet
                                  </p>
                                  <p className="text-sm text-slate-300">{source.snippet}</p>
                                </div>
                              )}
                              <div>
                                <p className="text-xs uppercase tracking-wider text-slate-500 mb-1">
                                  Scraped Content
                                </p>
                                <p className="text-xs text-slate-400 font-mono whitespace-pre-wrap max-h-48 overflow-y-auto">
                                  {source.scraped_content
                                    ? source.scraped_content.slice(0, 1500) +
                                      (source.scraped_content.length > 1500 ? '...' : '')
                                    : 'No scraped content stored.'}
                                </p>
                              </div>
                              <div className="flex items-center gap-3">
                                <a
                                  href={source.url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300"
                                >
                                  <ExternalLink className="w-3 h-3" />
                                  Visit Source
                                </a>
                                <span className="text-xs text-slate-600 font-mono">
                                  {new Date(source.created_at).toLocaleString()}
                                </span>
                              </div>
                            </div>
                          </td>
                        </motion.tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};