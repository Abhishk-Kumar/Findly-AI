export type ResearchDepth = 'Quick' | 'Standard' | 'Deep';
export type ResearchTone = 'Formal' | 'Conversational' | 'Technical' | 'Executive';

export type PipelineStatus =
  | 'queued'
  | 'searching'
  | 'selecting_sources'
  | 'scraping'
  | 'analyzing'
  | 'writing'
  | 'critiquing'
  | 'revising'
  | 'completed'
  | 'failed';

export interface SourceItem {
  id: string;
  run_id: string;
  url: string;
  title: string;
  domain: string;
  snippet?: string;
  scraped_content?: string;
  status: 'discovered' | 'scraped' | 'failed' | 'skipped';
  error_reason?: string;
  relevance_score?: number;
  char_count: number;
  created_at: string;
}

export interface BookmarkedFinding {
  id: string;
  run_id: string;
  topic: string;
  quote_text: string;
  section_title?: string;
  source_url?: string;
  notes?: string;
  created_at: string;
}

export interface QAMessage {
  id: string;
  run_id: string;
  question: string;
  answer: string;
  is_grounded: boolean;
  created_at: string;
}

export interface ResearchRunSummary {
  id: string;
  topic: string;
  depth: ResearchDepth;
  tone: ResearchTone;
  quality_bar: number;
  status: PipelineStatus;
  current_step: string;
  progress_pct: number;
  initial_score?: number;
  final_score?: number;
  revision_count: number;
  total_words: number;
  elapsed_seconds: number;
  created_at: string;
  updated_at: string;
  sources_count: number;
}

export interface ResearchRunDetail {
  id: string;
  topic: string;
  depth: ResearchDepth;
  tone: ResearchTone;
  quality_bar: number;
  max_revisions: number;
  status: PipelineStatus;
  current_step: string;
  progress_pct: number;
  initial_score?: number;
  final_score?: number;
  revision_count: number;
  draft_report?: string;
  final_report?: string;
  critique_feedback?: string;
  initial_critique?: string;
  synthesized_notes?: string;
  raw_search_summary?: string;
  error_message?: string;
  total_words: number;
  elapsed_seconds: number;
  step_timings: Record<string, number>;
  created_at: string;
  updated_at: string;
  sources: SourceItem[];
  bookmarks: BookmarkedFinding[];
  qa_messages: QAMessage[];
}

export interface ResearchCreatePayload {
  topic: string;
  depth: ResearchDepth;
  tone: ResearchTone;
  quality_bar: number;
  max_revisions: number;
}

export interface DashboardStats {
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  avg_score: number;
  total_sources: number;
  total_bookmarks: number;
  avg_duration_seconds: number;
}

export interface ResearchStatusEvent {
  run_id: string;
  status: PipelineStatus;
  current_step: string;
  progress_pct: number;
  message?: string;
  timestamp: string;
  score?: number;
  revision_count?: number;
  step_timings?: Record<string, number>;
  error_message?: string;
}
