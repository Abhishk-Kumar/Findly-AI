import axios from 'axios';
import type {
  ResearchCreatePayload,
  ResearchRunDetail,
  ResearchRunSummary,
  DashboardStats,
  BookmarkedFinding,
  QAMessage,
  ResearchStatusEvent,
} from '../types';

const API_BASE_URL = import.meta.env.Frontend_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const apiService = {
  // Research Runs
  async createResearch(payload: ResearchCreatePayload): Promise<ResearchRunDetail> {
    const res = await client.post<ResearchRunDetail>('/research', payload);
    return res.data;
  },

  async getResearch(id: string): Promise<ResearchRunDetail> {
    const res = await client.get<ResearchRunDetail>(`/research/${id}`);
    return res.data;
  },

  async listResearch(params?: { search?: string; status?: string; limit?: number; offset?: number }): Promise<ResearchRunSummary[]> {
    const res = await client.get<ResearchRunSummary[]>('/research', { params });
    return res.data;
  },

  async deleteResearch(id: string): Promise<void> {
    await client.delete(`/research/${id}`);
  },

  // Grounded Q&A
  async askQuestion(runId: string, question: string): Promise<QAMessage> {
    const res = await client.post<QAMessage>(`/research/${runId}/qa`, { question });
    return res.data;
  },

  async getQAHistory(runId: string): Promise<QAMessage[]> {
    const res = await client.get<QAMessage[]>(`/research/${runId}/qa`);
    return res.data;
  },

  // Bookmarking Findings
  async bookmarkFinding(
    runId: string,
    payload: { quote_text: string; section_title?: string; source_url?: string; notes?: string }
  ): Promise<BookmarkedFinding> {
    const res = await client.post<BookmarkedFinding>(`/research/${runId}/bookmarks`, payload);
    return res.data;
  },

  async listBookmarks(search?: string): Promise<BookmarkedFinding[]> {
    const res = await client.get<BookmarkedFinding[]>('/bookmarks', { params: { search } });
    return res.data;
  },

  async deleteBookmark(bookmarkId: string): Promise<void> {
    await client.delete(`/bookmarks/${bookmarkId}`);
  },

  // Dashboard Metrics
  async getStats(): Promise<DashboardStats> {
    const res = await client.get<DashboardStats>('/stats');
    return res.data;
  },

  // Exports
  getExportPdfUrl(runId: string): string {
    return `${API_BASE_URL}/api/research/${runId}/export/pdf`;
  },

  getExportMarkdownUrl(runId: string): string {
    return `${API_BASE_URL}/api/research/${runId}/export/md`;
  },

  // SSE Stream Listener
  subscribeToEvents(
    runId: string,
    onEvent: (event: ResearchStatusEvent) => void,
    onError?: (err: any) => void
  ): () => void {
    const eventSource = new EventSource(`${API_BASE_URL}/api/research/${runId}/stream`);

    eventSource.onmessage = (event) => {
      try {
        const data: ResearchStatusEvent = JSON.parse(event.data);
        onEvent(data);
        if (data.status === 'completed' || data.status === 'failed') {
          eventSource.close();
        }
      } catch (err) {
        console.error('Failed to parse SSE payload', err);
      }
    };

    eventSource.onerror = (err) => {
      if (onError) onError(err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  },
};
