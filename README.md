# Findly.AI – AI‑Driven Research Workspace v2.0

**Production‑grade autonomous research platform** powered by LangGraph state machines, multi‑source intelligence, quality‑gated revision loops, and a premium React UI.

*Transform a research question into a polished report in minutes—not days.*

## 🚀 Key Architecture

- **Backend**: FastAPI + LangGraph + SQLAlchemy async + Groq Llama‑3.3‑70B
- **Frontend**: React + Vite + TypeScript + Tailwind CSS + Framer Motion  
- **Orchestration**: 8‑node LangGraph StateGraph with conditional revision edges
- **Data Persistence**: SQLite (async) with full CRUD, bookmarks, Q&A history
- **Security**: SSRF‑protected scraper, URL scheme validation, API key sanitization

## ✨ Core Features

**🧠 Intelligent Research Pipeline**  
1. **Search** – Tavily‑powered multi‑source discovery  
2. **Select & Scrape** – BeautifulSoup + SSRF guard blocks private IPs  
3. **Analyze & Synthesize** – Groq Llama‑3.3‑70B processes sources  
4. **Write Draft** – Tonally‑adjusted (Formal/Technical/Conversational/Executive)  
5. **Critique** – AI critic scores draft (1‑10)  
6. **Quality Gate** – If score < `quality_bar` (default 7) and `revision_count < max_revisions` → revise  
7. **Finalize** – Export‑ready report with citations  

**⚙️ Production‑Ready Systems**  
- **Revision Loop** – Auto‑retry up to `max_revisions` (default 3)  
- **Streaming Status** – Server‑Sent Events (SSE) for real‑time progress  
- **Grounded Q&A** – Ask follow‑up questions anchored to scraped sources  
- **Bookmark Findings** – Save key quotes, export later  
- **PDF/Markdown Export** – One‑click downloads  

**🎨 Premium UI/UX**  
- Glass panels, gradient borders, custom scrollbars  
- Pipeline visualizer with real‑time status  
- Source explorer with scraped content preview  
- Dashboard with metrics (avg score, duration, runs)  
- Fully responsive, dark‑mode only  

## 📁 Project Structure

```
Findly‑AI/
├── backend/
│   ├── app/
│   │   ├── config.py              # Settings & CORS
│   │   ├── database/              # SQLAlchemy models, async session
│   │   ├── graph/                 # LangGraph StateGraph + nodes
│   │   ├── services/              # Tavily, scraper, LLM, research runner
│   │   ├── api/endpoints/         # REST + SSE endpoints
│   │   └── main.py                # FastAPI app + lifespan
│   └── tests/                     # 12 comprehensive pytest tests
├── frontend/
│   ├── src/
│   │   ├── components/            # Button, Badge, Header
│   │   ├── pages/                 # Dashboard, New Research, History, etc.
│   │   ├── services/api.ts        # Typed REST + SSE client
│   │   ├── types/index.ts         # TypeScript interfaces
│   │   └── lib/utils.ts           # Utility functions
│   └── public/                    # Icons, static assets
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project config
└── README.md                      # This file
```

## 🚦 Quick Start

### 1. Clone & Setup

```bash
git clone <repo-url>
cd Findly-AI

# Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 2. Configure API Keys

Create `.env` in project root:

```env
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

### 3. Start Services

**Backend** (FastAPI on http://localhost:8000):

```bash
source .venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload
```

**Frontend** (React on http://localhost:5173):

```bash
cd frontend
npm run dev
```

### 4. Test the System

1. Open http://localhost:5173  
2. Click **New Research**  
3. Enter topic: *"Neuromorphic Computing Architectures"*  
4. Select depth: *Standard*, tone: *Technical*  
5. Click **Start Research Run**  
6. Watch the pipeline progress via SSE  
7. When completed, view report, bookmark findings, export PDF  

## 🧪 Testing

All 12 backend tests pass:

```bash
cd backend
python -m pytest tests/ -v
```

Tests include:
- Graph workflow logic (quality gate, revision decisions)  
- Scraper security (SSRF blocks, scheme validation)  
- API endpoints (CRUD, SSE, bookmarks, stats)  
- Repository layer (async SQLAlchemy)  

## 🔧 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/research` | POST | Create new research run |
| `/api/research/{id}/stream` | GET | SSE stream of pipeline status |
| `/api/research/{id}/qa` | POST | Ask grounded follow‑up question |
| `/api/research/{id}/bookmarks` | POST | Bookmark a finding |
| `/api/bookmarks` | GET | List all bookmarks |
| `/api/stats` | GET | Dashboard metrics |
| `/api/research/{id}/export/pdf` | GET | Download PDF report |
| `/api/research/{id}/export/md` | GET | Download Markdown report |

## 🎯 Quality Gate & Revision Loop

The system's core intelligence:

```python
if score < quality_bar and revision_count < max_revisions:
    # Trigger revision → critique → rewrite
    state["revision_count"] += 1
    return "revise"
else:
    # Finalize report
    return "finalize"
```

**Default settings**: `quality_bar = 7`, `max_revisions = 3`

## 🛡️ Security

- **SSRF Protection**: Blocks `localhost`, `127.*`, `192.168.*`, `10.*`, `172.16.*`  
- **URL Scheme Validation**: Only `http://` and `https://` allowed  
- **API Key Sanitization**: Errors strip `gsk_`, `tvly-`, `Bearer ` prefixes  
- **CORS**: Configured for `localhost:5173` and `localhost:3000`  

## 📈 Dashboard Metrics

- Total runs / completed / failed  
- Average critic score (1‑10)  
- Average duration (seconds)  
- Total sources scraped  
- Total bookmarks saved  

## 🚀 Deployment Notes

**Backend**:
- Use `uvicorn` with `--workers` for production  
- Set `ENVIRONMENT=production` in `.env`  
- Consider PostgreSQL for `DATABASE_URL`  

**Frontend**:
- Build with `npm run build` (output in `dist/`)  
- Serve via Nginx, Vercel, Netlify, or similar  
- Set `VITE_API_BASE_URL` environment variable  

## 📄 License

MIT

---

**Findly.AI** transforms raw queries into polished intelligence—automating research while keeping the human in the loop.