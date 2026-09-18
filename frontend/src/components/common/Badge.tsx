import React from 'react';
import type { PipelineStatus } from '../../types';

interface BadgeProps {
  status: PipelineStatus | string;
  className?: string;
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({ status, className = '', size = 'md' }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'completed':
      case 'scraped':
        return {
          bg: 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60',
          dot: 'bg-emerald-400',
          label: status === 'scraped' ? 'Scraped' : 'Completed',
          pulse: false,
        };
      case 'failed':
        return {
          bg: 'bg-rose-950/60 text-rose-400 border-rose-800/60',
          dot: 'bg-rose-400',
          label: 'Failed',
          pulse: false,
        };
      case 'queued':
        return {
          bg: 'bg-slate-900 text-slate-400 border-slate-700/60',
          dot: 'bg-slate-400',
          label: 'Queued',
          pulse: true,
        };
      case 'searching':
      case 'selecting_sources':
      case 'scraping':
      case 'analyzing':
      case 'writing':
      case 'critiquing':
      case 'revising':
        return {
          bg: 'bg-indigo-950/60 text-indigo-300 border-indigo-700/60',
          dot: 'bg-indigo-400',
          label: status.replace('_', ' '),
          pulse: true,
        };
      case 'discovered':
        return {
          bg: 'bg-cyan-950/60 text-cyan-300 border-cyan-800/60',
          dot: 'bg-cyan-400',
          label: 'Discovered',
          pulse: false,
        };
      case 'skipped':
        return {
          bg: 'bg-amber-950/60 text-amber-300 border-amber-800/60',
          dot: 'bg-amber-400',
          label: 'Skipped',
          pulse: false,
        };
      default:
        return {
          bg: 'bg-slate-900 text-slate-300 border-slate-700',
          dot: 'bg-slate-400',
          label: status,
          pulse: false,
        };
    }
  };

  const config = getStatusConfig();
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border capitalize ${config.bg} ${sizeClasses} ${className}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${config.dot} ${config.pulse ? 'animate-ping' : ''}`}
      />
      {config.label}
    </span>
  );
};
