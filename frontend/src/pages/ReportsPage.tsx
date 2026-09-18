import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Download } from 'lucide-react';
import { Badge } from '../components/common/Badge';
import { apiService } from '../services/api';
import type { ResearchRunSummary, ResearchRunDetail } from '../types';
import { cn } from '../lib/utils';

export const ReportsPage: React.FC = () => {
  const [runs, setRuns] = useState<ResearchRunSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ResearchRunDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  // const [bookmarkNotice, setBookmarkNotice] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiService.listResearch();
        const completed = data.filter(r => r.status === 'completed');
        setRuns(completed);
        if (completed.length > 0) {
          setSelectedId(completed[0].id);
        }
      } catch (err) {
        console.error('Failed to load reports', err);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    const loadDetail = async () => {
      setIsDetailLoading(true);
      try {
        const d = await apiService.getResearch(selectedId);
        setDetail(d);
      } catch (err) {
        console.error('Failed to load report detail', err);
      } finally {
        setIsDetailLoading(false);
      }
    };
    loadDetail();
  }, [selectedId]);

  // Bookmarking functionality (commented for now)
  // const handleBookmark = async (quote: string) => {
  //   if (!selectedId || !quote.trim()) return;
  //   try {
  //     await apiService.bookmarkFinding(selectedId, {
  //       quote_text: quote.slice(0, 500),
  //       section_title: 'Report',
  //     });
  //     setBookmarkNotice('Bookmarked!');
  //     setTimeout(() => setBookmarkNotice(null), 2000);
  //   } catch (err) {
  //     console.error('Failed to bookmark', err);
  //   }
  // };

  const reportMarkdown = detail?.final_report || detail?.draft_report || '';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white font-display">Generated Reports</h1>
        {detail && selectedId && (
          <div className="flex items-center gap-2">
            <a
              href={apiService.getExportPdfUrl(selectedId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-surface-raised border border-surface-border text-slate-300 hover:border-indigo-500/60 hover:text-white transition-all"
            >
              <Download className="w-3.5 h-3.5" /> PDF
            </a>
            <a
              href={apiService.getExportMarkdownUrl(selectedId)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-surface-raised border border-surface-border text-slate-300 hover:border-cyan-500/60 hover:text-white transition-all"
            >
              <Download className="w-3.5 h-3.5" /> Markdown
            </a>
          </div>
        )}
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-500">Loading reports...</div>
      ) : runs.length === 0 ? (
        <div className="text-center py-16 glass-panel rounded-xl">
          <FileText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">No completed reports yet</p>
          <p className="text-sm text-slate-600 mt-1">
            Reports appear once research runs pass the quality gate.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Run list */}
          <div className="space-y-2">
            {runs.map((run) => (
              <button
                key={run.id}
                onClick={() => setSelectedId(run.id)}
                className={cn(
                  'w-full text-left p-4 rounded-xl border transition-all',
                  selectedId === run.id
                    ? 'bg-indigo-900/20 border-indigo-500/50 shadow-glow-accent'
                    : 'bg-surface-raised border-surface-border hover:border-slate-600'
                )}
              >
                <p className="text-sm font-medium text-white line-clamp-2">{run.topic}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge status="completed" size="sm" />
                  {run.final_score && (
                    <span className="text-xs font-mono px-2 py-0.5 bg-emerald-900/30 text-emerald-400 rounded">
                      {run.final_score}/10
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  {run.total_words} words
                </p>
              </button>
            ))}
          </div>

          {/* Report viewer */}
          <div className="lg:col-span-3">
            <AnimatePresence mode="wait">
              <motion.div
                key={selectedId}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="glass-panel rounded-xl p-6 shadow-elevated"
              >
                {isDetailLoading ? (
                  <div className="text-center py-12 text-slate-500">Loading report...</div>
                ) : detail ? (
                  <div>
                    <div className="flex items-center justify-between mb-4 pb-4 border-b border-surface-border">
                      <h2 className="text-lg font-bold text-white font-display">
                        {detail.topic}
                      </h2>
                      <div className="flex items-center gap-3">
                        {detail.final_score && (
                          <span className="text-xs font-mono px-2.5 py-1 bg-emerald-900/30 text-emerald-400 rounded-full">
                            Score {detail.final_score}/10
                          </span>
                        )}
                        <span className="text-xs text-slate-500">
                          Revisions: {detail.revision_count}
                        </span>
                      </div>
                    </div>

                    {reportMarkdown ? (
                      <div className="max-h-[60vh] overflow-y-auto pr-2 markdown-content">
                        {reportMarkdown.split('\n\n').map((block, idx) => {
                          const isHeading = /^#{1,3}\s/.test(block);
                          const isList = /^[-*]\s/.test(block);
                          if (isHeading) {
                            const level = block.match(/^#{1,3}/)?.[0].length ?? 1;
                            const text = block.replace(/^#{1,3}\s/, '');
                            const textClass = level === 1 ? 'text-xl' : level === 2 ? 'text-lg' : 'text-base';
                            return (
                              <h2 key={idx} className={cn('font-bold text-white mt-6 mb-2', textClass)}>
                                {text}
                              </h2>
                            );
                          }
                          if (isList) {
                            const items = block
                              .split('\n')
                              .filter(l => /^[-*]\s/.test(l))
                              .map(l => l.replace(/^[-*]\s/, ''));
                            return (
                              <ul key={idx} className="list-disc pl-5 mb-4 text-slate-300 space-y-1">
                                {items.map((item, i) => (
                                  <li key={i}>{item}</li>
                                ))}
                              </ul>
                            );
                          }
                          return (
                            <p key={idx} className="text-sm text-slate-300 leading-relaxed mb-4">
                              {block.replace(/^#+\s/, '')}
                            </p>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="text-center py-12 text-slate-500">
                        No report content available for this run.
                      </div>
                    )}

                    {/* Bookmark selection from report (commented for now) */}
                    {/* {bookmarkNotice && (
                      <div className="mt-4 text-xs text-emerald-400 font-mono">
                        ✓ {bookmarkNotice}
                      </div>
                    )} */}
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500">Select a report to view</div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  );
};