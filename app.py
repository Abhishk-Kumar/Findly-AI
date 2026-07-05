"""
app.py
Streamlit frontend for the multi-agent research pipeline.

Run locally with:
    streamlit run app.py

Deploy for free on Streamlit Community Cloud (share.streamlit.io) -
see README.md for step-by-step instructions.
"""

import io
from datetime import datetime

import streamlit as st

from pipeline import execute_research_pipeline
from agents import llm

st.set_page_config(
    page_title="Research Agent",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom styling — dark, gradient, card-based UI
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, .hero-title { font-family: 'Sora', sans-serif; }

.hero-wrap {
    padding: 2.2rem 2.4rem;
    border-radius: 20px;
    margin-bottom: 1.6rem;
    background: radial-gradient(circle at 15% 20%, rgba(139,92,246,0.35), transparent 55%),
                radial-gradient(circle at 85% 0%, rgba(56,189,248,0.25), transparent 50%),
                linear-gradient(135deg, #16162a 0%, #0f0f17 100%);
    border: 1px solid rgba(139,92,246,0.25);
}
.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa 60%, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.hero-sub { color: #9d9db0; font-size: 1.02rem; }

.pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 6px;
    background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.35);
    color: #c4b5fd;
}

.glass-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.1rem 1.3rem;
}

div[data-testid="stButton"] button {
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.15s ease;
    border: 1px solid rgba(139,92,246,0.35);
}
div[data-testid="stButton"] button:hover {
    border-color: #a78bfa;
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(139,92,246,0.25);
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.7rem 0.8rem 0.4rem 0.8rem;
}

.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0 14px 0; }

.score-badge {
    font-size: 1.6rem;
    font-weight: 800;
    font-family: 'Sora', sans-serif;
}

.history-item {
    border-radius: 12px;
    padding: 8px 10px;
    margin-bottom: 6px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
}

.diff-original { color: #f87171; text-decoration: line-through; opacity: 0.7; }
.diff-revised { color: #34d399; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of {topic, state, timestamp}
if "active_result" not in st.session_state:
    st.session_state.active_result = None
if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""

SAMPLE_TOPICS = [
    "Impact of quantum computing on cryptography",
    "Rise of small language models in 2026",
    "AI regulation trends in the EU",
    "Future of humanoid robotics",
]


def generate_pdf(topic: str, report_text: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import cm

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], spaceAfter=20)

    story = [Paragraph(f"Research Report: {topic}", title_style), Spacer(1, 12)]
    for para in report_text.split("\n"):
        clean = para.strip()
        if clean:
            story.append(Paragraph(clean, styles["BodyText"]))
            story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def score_color(score: int) -> str:
    if score >= 8:
        return "#34d399"
    if score >= 5:
        return "#fbbf24"
    return "#f87171"


def render_gauge(score: int):
    import plotly.graph_objects as go

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": " / 10", "font": {"size": 30, "color": score_color(score)}},
        gauge={
            "axis": {"range": [0, 10], "tickcolor": "#666"},
            "bar": {"color": score_color(score)},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 5], "color": "rgba(248,113,113,0.15)"},
                {"range": [5, 8], "color": "rgba(251,191,36,0.15)"},
                {"range": [8, 10], "color": "rgba(52,211,153,0.15)"},
            ],
        },
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e7e7f0"},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔎 Research Agent")
    st.caption("Multi-agent web research, writing and self-critique pipeline.")

    st.markdown("---")
    st.markdown("##### ⚙️ Report settings")
    depth = st.select_slider("Depth", options=["Quick", "Standard", "Deep"], value="Standard")
    tone = st.radio("Tone", ["Formal", "Conversational"], horizontal=True)
    quality_bar = st.slider(
        "Auto-revise if critic score is below", min_value=4, max_value=9, value=7,
        help="If the critic scores the report below this, it's automatically rewritten once."
    )

    st.markdown("---")
    st.markdown("##### 🕘 History")
    if not st.session_state.history:
        st.caption("No research runs yet.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            s = item["state"]["final_score"]
            st.markdown(
                f"<div class='history-item'>"
                f"<b>{item['topic'][:34]}</b><br>"
                f"<span style='color:{score_color(s)}'>● {s}/10</span> · "
                f"<span style='color:#8a8aa0;font-size:0.8rem'>{item['timestamp']}</span>"
                f"</div>", unsafe_allow_html=True,
            )
            if st.button("Open", key=f"hist_open_{i}", use_container_width=True):
                st.session_state.active_result = item
        if st.button("🗑️ Clear history", use_container_width=True):
            st.session_state.history = []
            st.session_state.active_result = None
            st.rerun()

# ---------------------------------------------------------------------------
# Hero + input
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">AI Research Agent</div>
    <div class="hero-sub">Searches the web, scrapes real sources, drafts a report, critiques itself —
    and rewrites the report automatically if it's not good enough.</div>
    <div style="margin-top:12px;">
        <span class="pill">🕵️ Search Agent</span>
        <span class="pill">🕸️ Scraping Agent</span>
        <span class="pill">✍️ Writer Chain</span>
        <span class="pill">🧐 Critic Chain</span>
        <span class="pill">🔁 Self-revision loop</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("**Try a sample topic:**")
chip_cols = st.columns(len(SAMPLE_TOPICS))
for col, sample in zip(chip_cols, SAMPLE_TOPICS):
    with col:
        if st.button(sample, key=f"chip_{sample}", use_container_width=True):
            st.session_state.topic_input = sample
            st.rerun()

col1, col2 = st.columns([4, 1])
with col1:
    topic = st.text_input(
        "Research topic", key="topic_input",
        placeholder="e.g. Impact of quantum computing on cryptography",
        label_visibility="collapsed",
    )
with col2:
    run_clicked = st.button("🚀 Start Research", use_container_width=True, type="primary")

if run_clicked and topic.strip():
    steps = ["Searching the web", "Scraping relevant sources", "Drafting the report",
              "Getting critic feedback", "Auto-revising if needed"]

    with st.status("Running the research pipeline...", expanded=True) as status:
        status_box = status

        def progress_callback(step, total, label):
            status_box.update(label=f"Step {step}/{total}: {label}")
            st.write(f"✅ {label}")

        try:
            result = execute_research_pipeline(
                topic.strip(),
                progress_callback=progress_callback,
                depth=depth,
                tone=tone,
                quality_bar=quality_bar,
            )
            status.update(label="Done!", state="complete", expanded=False)
            entry = {
                "topic": topic.strip(),
                "state": result,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.session_state.history.append(entry)
            st.session_state.active_result = entry
            st.toast(f"Research complete — scored {result['final_score']}/10", icon="🎉")
        except Exception as e:
            status.update(label="Failed", state="error", expanded=True)
            st.error(f"⚠️ {e}")
elif run_clicked:
    st.warning("Please enter a topic first.")

# ---------------------------------------------------------------------------
# Results display
# ---------------------------------------------------------------------------
active = st.session_state.active_result
if active:
    state = active["state"]

    st.markdown("---")
    gauge_col, metric_col = st.columns([1, 3])
    with gauge_col:
        render_gauge(state["final_score"])
    with metric_col:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Sources found", len(state.get("sources", [])))
        m2.metric("Report words", len(state["report"].split()))
        m3.metric("Time taken", f"{state.get('elapsed_seconds', 0)}s")
        m4.metric("Auto-revised", "Yes" if state.get("revised") else "No")
        if state.get("step_timings"):
            st.caption(
                " · ".join(f"{k}: {v}s" for k, v in state["step_timings"].items())
            )

    tab_names = ["📄 Report", "🧐 Critic Feedback", "🔗 Sources", "🧪 Raw Agent Output", "💬 Ask about this report"]
    if state.get("revised"):
        tab_names.insert(2, "🔁 Before / After")
    tabs = st.tabs(tab_names)
    tab_map = dict(zip(tab_names, tabs))

    with tab_map["📄 Report"]:
        st.markdown(f"<div class='glass-card'>{state['report']}</div>", unsafe_allow_html=True)
        st.markdown("")
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                "⬇️ Download as Markdown",
                data=state["report"],
                file_name=f"{active['topic'][:40].replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with dl2:
            try:
                pdf_bytes = generate_pdf(active["topic"], state["report"])
                st.download_button(
                    "⬇️ Download as PDF",
                    data=pdf_bytes,
                    file_name=f"{active['topic'][:40].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.caption(f"PDF export unavailable: {e}")

    with tab_map["🧐 Critic Feedback"]:
        if state.get("revised"):
            st.caption("Feedback on the FINAL (revised) report:")
        st.markdown(state["feedback"])
        if state.get("revised"):
            with st.expander("Original critic feedback (before revision)"):
                st.markdown(state["initial_feedback"])

    if "🔁 Before / After" in tab_map:
        with tab_map["🔁 Before / After"]:
            st.caption(
                f"Initial score was {state['initial_score']}/10 (below the "
                f"{state['quality_bar']}/10 bar), so the report was auto-revised."
            )
            b1, b2 = st.columns(2)
            with b1:
                st.markdown("**Before**")
                st.markdown(f"<div class='glass-card diff-original'>{state['original_report']}</div>", unsafe_allow_html=True)
            with b2:
                st.markdown("**After**")
                st.markdown(f"<div class='glass-card diff-revised'>{state['report']}</div>", unsafe_allow_html=True)

    with tab_map["🔗 Sources"]:
        if state.get("sources"):
            for url in state["sources"]:
                st.markdown(f"- [{url}]({url})")
        else:
            st.caption("No sources extracted.")

    with tab_map["🧪 Raw Agent Output"]:
        with st.expander("Search agent output"):
            st.text(state["search_results"])
        with st.expander("Scraping agent output"):
            st.text(state["scraped_content"])

    with tab_map["💬 Ask about this report"]:
        st.caption("Ask a follow-up question grounded in the generated report.")
        question = st.text_input("Your question", key="followup_question")
        if st.button("Ask", key="ask_button") and question.strip():
            with st.spinner("Thinking..."):
                try:
                    answer = llm.invoke(
                        f"Answer the question using ONLY the report below. "
                        f"If the report doesn't contain the answer, say so.\n\n"
                        f"Report:\n{state['report']}\n\nQuestion: {question}"
                    )
                    st.markdown(answer.content)
                except Exception as e:
                    st.error(
                        "⚠️ Couldn't reach the model. If this mentions an API key or a "
                        f"401 error, check GROQ_API_KEY in your .env / secrets.\n\n{e}"
                    )
else:
    st.info("Pick a sample topic above or type your own, then click **Start Research**.")