import React from 'react';
import { Header } from './components/layout/Header';
import { DashboardPage } from './pages/DashboardPage';
import { NewResearchPage } from './pages/NewResearchPage';
import { HistoryPage } from './pages/HistoryPage';
import { BookmarksPage } from './pages/BookmarksPage';
import { ExploreSourcesPage } from './pages/ExploreSourcesPage';
import { ReportsPage } from './pages/ReportsPage';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState('dashboard');

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage />;
      case 'new':
        return <NewResearchPage />;
      case 'explore':
        return <ExploreSourcesPage />;
      case 'reports':
        return <ReportsPage />;
      case 'bookmarks':
        return <BookmarksPage />;
      case 'history':
        return <HistoryPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="min-h-screen bg-background text-slate-200">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="container mx-auto px-4 py-6">
        {renderPage()}
      </main>
      <footer className="mt-12 border-t border-surface-border py-6 text-center text-xs text-slate-500 font-mono">
        <div className="container mx-auto px-4">
          <p>Findly.AI • AI‑Driven Research Workspace v2.0 • Built with React + Vite + FastAPI + LangGraph</p>
          <p className="mt-1">Quality‑gate revision loop • SSRF‑protected scraping • Grounded Q&A • Portfolio‑grade UI</p>
        </div>
      </footer>
    </div>
  );
};

export default App;
