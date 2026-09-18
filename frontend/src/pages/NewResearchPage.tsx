import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ArrowRight, CheckCircle2 } from 'lucide-react';
import { Button } from '../components/common/Button';
import { apiService } from '../services/api';
import type { ResearchCreatePayload, ResearchDepth, ResearchTone } from '../types';
import { cn } from '../lib/utils';

const DEPTHS: { value: ResearchDepth; label: string; desc: string }[] = [
  { value: 'Quick', label: 'Quick Scan', desc: '3 sources, Fast mode' },
  { value: 'Standard', label: 'Standard', desc: '6 sources, Balanced quality' },
  { value: 'Deep', label: 'Deep Dive', desc: '12 sources, Strict revision' },
];

const TONES: { value: ResearchTone; label: string; icon: string }[] = [
  { value: 'Formal', label: 'Formal', icon: '📄' },
  { value: 'Conversational', label: 'Conversational', icon: '💬' },
  { value: 'Technical', label: 'Technical', icon: '⚙️' },
  { value: 'Executive', label: 'Executive', icon: '📊' },
];

export const NewResearchPage: React.FC = () => {
  const [topic, setTopic] = useState('');
  const [depth, setDepth] = useState<ResearchDepth>('Standard');
  const [tone, setTone] = useState<ResearchTone>('Formal');
  const [qualityBar, setQualityBar] = useState(7);
  const [maxRevisions, setMaxRevisions] = useState(3);
  const [isLoading, setIsLoading] = useState(false);
  const [submittedId, setSubmittedId] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsLoading(true);
    try {
      const payload: ResearchCreatePayload = {
        topic: topic.trim(),
        depth,
        tone,
        quality_bar: qualityBar,
        max_revisions: maxRevisions,
      };
      const run = await apiService.createResearch(payload);
      setSubmittedId(run.id);
    } catch (err) {
      console.error('Failed to start research', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl font-bold text-white font-display mb-2">
          <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 text-transparent bg-clip-text">
            Launch New Research
          </span>
        </h1>
        <p className="text-slate-400">
          Configure your run. The system will search, scrape, analyze, critique, and revise until the quality gate is met.
        </p>
      </motion.div>

      <AnimatePresence mode="wait">
        {submittedId ? (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-surface border border-emerald-800/50 rounded-2xl p-8 text-center shadow-glow-accent"
          >
            <CheckCircle2 className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">Research Started!</h2>
            <p className="text-slate-400 mb-6">
              Run ID: <span className="font-mono text-indigo-400">{submittedId}</span>
            </p>
            <div className="flex items-center justify-center gap-3">
              <Button
                variant="primary"
                icon={<ArrowRight className="w-4 h-4" />}
                onClick={() => setSubmittedId(null)}
              >
                Start Another
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  /* Navigate to run detail */
                }}
              >
                View Progress
              </Button>
            </div>
          </motion.div>
        ) : (
          <motion.form
            key="form"
            onSubmit={handleSubmit}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-surface-raised/60 border border-surface-border rounded-2xl p-8 shadow-elevated space-y-8"
          >
            {/* Topic */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-300">
                Research Topic <span className="text-rose-400">*</span>
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., Neuromorphic Computing Architectures for Edge AI"
                className="w-full px-4 py-3 rounded-lg bg-background border border-surface-border focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 text-white placeholder-slate-600 transition-all"
                required
              />
            </div>

            {/* Depth */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-slate-300">
                Research Depth
              </label>
              <div className="grid grid-cols-3 gap-3">
                {DEPTHS.map((d) => (
                  <button
                    key={d.value}
                    type="button"
                    onClick={() => setDepth(d.value)}
                    className={cn(
                      'p-4 rounded-xl border text-left transition-all',
                      depth === d.value
                        ? 'bg-indigo-900/20 border-indigo-500/50 shadow-glow-accent'
                        : 'bg-background border-surface-border hover:border-slate-600'
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-white">{d.label}</span>
                      {depth === d.value && (
                        <CheckCircle2 className="w-4 h-4 text-indigo-400" />
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{d.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Tone */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-slate-300">
                Output Tone
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {TONES.map((t) => (
                  <button
                    key={t.value}
                    type="button"
                    onClick={() => setTone(t.value)}
                    className={cn(
                      'flex items-center gap-2 p-3 rounded-lg border text-sm transition-all',
                      tone === t.value
                        ? 'bg-cyan-900/20 border-cyan-500/50 text-white'
                        : 'bg-background border-surface-border text-slate-400 hover:border-slate-600'
                    )}
                  >
                    <span>{t.icon}</span>
                    <span>{t.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Sliders */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-300">
                  Quality Bar: <span className="text-indigo-400 font-mono">{qualityBar}</span>/10
                </label>
                <input
                  type="range"
                  min={5}
                  max={10}
                  value={qualityBar}
                  onChange={(e) => setQualityBar(parseInt(e.target.value))}
                  className="w-full h-2 rounded-full appearance-none cursor-pointer bg-surface-border accent-indigo-500"
                />
                <div className="flex justify-between text-xs text-slate-500 px-1">
                  <span>Lenient (5)</span>
                  <span>Strict (10)</span>
                </div>
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-300">
                  Max Revisions: <span className="text-amber-400 font-mono">{maxRevisions}</span>
                </label>
                <input
                  type="range"
                  min={1}
                  max={5}
                  value={maxRevisions}
                  onChange={(e) => setMaxRevisions(parseInt(e.target.value))}
                  className="w-full h-2 rounded-full appearance-none cursor-pointer bg-surface-border accent-amber-500"
                />
                <div className="flex justify-between text-xs text-slate-500 px-1">
                  <span>1 (Fast)</span>
                  <span>5 (Thorough)</span>
                </div>
              </div>
            </div>

            {/* Submit */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              disabled={!topic.trim()}
              className="w-full justify-center"
              icon={!isLoading ? <Sparkles className="w-4 h-4" /> : undefined}
            >
              {isLoading ? 'Starting Research...' : 'Start Research Run'}
            </Button>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  );
};
