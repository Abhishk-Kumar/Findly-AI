import React from 'react';
import { Brain, Zap, Search, FileText, Bookmark, History } from 'lucide-react';
import { Button } from '../common/Button';
import { cn } from '../../lib/utils';

interface HeaderProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab = 'dashboard', onTabChange }) => {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Brain },
    { id: 'new', label: 'New Research', icon: Zap },
    { id: 'explore', label: 'Explore Sources', icon: Search },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'bookmarks', label: 'Bookmarks', icon: Bookmark },
    { id: 'history', label: 'History', icon: History },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-surface-border bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-indigo-600 to-cyan-500 opacity-70 blur-md" />
              <div className="relative flex items-center justify-center w-10 h-10 rounded-full bg-surface border border-surface-border">
                <Brain className="w-5 h-5 text-indigo-400" />
              </div>
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-white font-display">
                Findly<span className="text-indigo-400">.AI</span>
              </h1>
              <p className="text-xs text-slate-400 font-mono">
                AI‑Driven Research Workspace v2.0
              </p>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-0.5">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <Button
                  key={tab.id}
                  variant={isActive ? 'primary' : 'ghost'}
                  size="sm"
                  className={cn(
                    'rounded-lg font-medium transition-all',
                    isActive && 'shadow-glow-accent'
                  )}
                  onClick={() => onTabChange?.(tab.id)}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </Button>
              );
            })}
          </nav>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              className="text-xs font-mono"
              icon={<span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />}
            >
              Backend Online
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};
