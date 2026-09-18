import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bookmark, Trash2, ExternalLink, Quote, StickyNote } from 'lucide-react';
import { Button } from '../components/common/Button';
import { apiService } from '../services/api';
import type { BookmarkedFinding } from '../types';

export const BookmarksPage: React.FC = () => {
  const [bookmarks, setBookmarks] = useState<BookmarkedFinding[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchBookmarks();
  }, []);

  const fetchBookmarks = async () => {
    setIsLoading(true);
    try {
      const data = await apiService.listBookmarks();
      setBookmarks(data);
    } catch (err) {
      console.error('Failed to fetch bookmarks', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await apiService.deleteBookmark(id);
      setBookmarks(bookmarks.filter(b => b.id !== id));
    } catch (err) {
      console.error('Failed to delete bookmark', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white font-display">Bookmarked Findings</h1>
        <span className="text-sm text-slate-500 font-mono">
          {bookmarks.length} saved
        </span>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-500">Loading bookmarks...</div>
      ) : bookmarks.length === 0 ? (
        <div className="text-center py-16 glass-panel rounded-xl">
          <Bookmark className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">No bookmarks yet</p>
          <p className="text-sm text-slate-600 mt-1">
            Bookmark key quotes and findings while viewing reports or sources.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <AnimatePresence>
            {bookmarks.map((bm) => (
              <motion.div
                key={bm.id}
                layout
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="glass-panel rounded-xl p-5 hover:glass-panel-elevated transition-all"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2 text-xs text-indigo-400 font-mono">
                    <Quote className="w-3.5 h-3.5" />
                    {bm.topic}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(bm.id)}
                    className="text-rose-500 hover:text-rose-400 hover:bg-rose-900/20"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>

                <blockquote className="mt-3 text-sm text-slate-300 italic border-l-2 border-indigo-500/50 pl-4">
                  \"{bm.quote_text}\"
                </blockquote>

                {bm.section_title && (
                  <div className="mt-3 text-xs text-slate-500">
                    Section: <span className="text-slate-400">{bm.section_title}</span>
                  </div>
                )}

                {bm.notes && (
                  <div className="mt-2 flex items-start gap-2 text-xs text-amber-200/80 bg-amber-900/10 rounded-lg p-2.5">
                    <StickyNote className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                    {bm.notes}
                  </div>
                )}

                {bm.source_url && (
                  <a
                    href={bm.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-3 inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" />
                    {new URL(bm.source_url).hostname}
                  </a>
                )}

                <div className="mt-3 pt-2.5 border-t border-surface-border text-xs text-slate-600">
                  {new Date(bm.created_at).toLocaleString()}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};