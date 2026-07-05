# 🔎 AI Research Agent

A multi-agent research pipeline that searches the web, scrapes the most relevant source,
drafts a structured report, critiques its own work, and automatically rewrites the report
if the critique score is too low — all wrapped in a Streamlit UI.

## Why this project is interesting

Most "chat with a PDF" projects stop at retrieval. This one is a small **agentic system**:
multiple specialized agents/chains hand off state to one another, and the pipeline includes
a **self-correction loop** — the critic's own feedback is fed back into an editor chain, and
the report is re-scored before being shown to the user.

## Architecture

```
   topic
     │
     ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────┐     ┌────────────────┐
│  Search Agent    │ --> │ Scraping Agent   │ --> │ Writer Chain  │ --> │  Critic Chain  │
│  (Tavily tool)   │     │ (requests + BS4) │     │ (report LLM)  │     │ (scores /10)   │
└─────────────────┘     └──────────────────┘     └───────────────┘     └────────┬───────┘
                                                                                  │
                                                              score < 7?  ────────┤
                                                                    │             │
                                                                    ▼             ▼
                                                          ┌──────────────────┐   done
                                                          │ Reviser Chain    │
                                                          │ (rewrite + re-   │
                                                          │  score once)     │
                                                          └──────────────────┘
```

## Features

- **Two tool-using agents** (search + scraping) built with LangChain's `create_agent`
- **Self-critique loop**: a critic chain scores every report out of 10; if it scores below
  7, the report is automatically revised once against the critic's own feedback and re-scored
- **Retry logic** (via `tenacity`) around both agents to absorb transient API/network failures
- **Streamlit UI** with:
  - Live step-by-step progress while the pipeline runs
  - Score, word count, source count and elapsed-time metrics
  - Tabs for the final report, critic feedback, extracted sources, and raw agent output
  - Markdown and PDF export of the final report
  - A run history sidebar so past research sessions aren't lost
  - A "Ask about this report" follow-up Q&A box, answered strictly from the generated report

## Tech stack

| Layer        | Tool                                   |
|--------------|-----------------------------------------|
| LLM          | Groq (`llama-3.3-70b-versatile`)        |
| Orchestration| LangChain (`create_agent`, LCEL chains) |
| Search       | Tavily Search API                       |
| Scraping     | `requests` + `BeautifulSoup`            |
| Reliability  | `tenacity` (retry with backoff)         |
| Frontend     | Streamlit                               |
| PDF export   | ReportLab                                |

## Project structure

```
research-agent/
├── agents.py        # agents + LCEL chains (writer, critic, reviser)
├── tools.py          # web_search (Tavily) and scrape_url (requests + BS4) tools
├── pipeline.py       # orchestrates the full run, incl. retries + auto-revision loop
├── app.py            # Streamlit frontend
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Clone and install dependencies**

   ```bash
   git clone <your-repo-url>
   cd research-agent
   pip install -r requirements.txt
   ```

2. **Add your API keys**

   Copy `.env.example` to `.env` and fill in your keys:

   ```bash
   cp .env.example .env
   ```

   - `GROQ_API_KEY` — from [console.groq.com](https://console.groq.com)
   - `TAVILY_API_KEY` — from [app.tavily.com](https://app.tavily.com) (free tier is enough for demos)

3. **Run the CLI version** (matches the original pipeline script)

   ```bash
   python pipeline.py
   ```

4. **Run the Streamlit app**

   ```bash
   streamlit run app.py
   ```

## Deploying on Streamlit Community Cloud

1. Push this project to a public (or private) GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, select your repo/branch, and set the main file to `app.py`.
4. Under **Advanced settings → Secrets**, add:

   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   TAVILY_API_KEY = "your_tavily_api_key_here"
   ```

5. Click **Deploy**. Streamlit will install `requirements.txt` automatically and give you a
   public URL you can put straight on your resume/portfolio.

## Possible next steps

- Rebuild the pipeline as a LangGraph state graph so the auto-revision loop can run more
  than once, with an explicit exit condition instead of a single retry
- Add a vector store (Chroma/FAISS) to cache scraped content across topics and support
  follow-up research without re-scraping
- Support scraping and synthesizing multiple URLs instead of just the single best match
- Add authentication + a database (SQLite/Postgres) to persist history across sessions/users