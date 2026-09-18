import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ResearchRun(Base):
    __tablename__ = "research_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    topic = Column(String(500), nullable=False, index=True)
    depth = Column(String(50), nullable=False, default="Standard")
    tone = Column(String(50), nullable=False, default="Formal")
    quality_bar = Column(Integer, nullable=False, default=7)
    max_revisions = Column(Integer, nullable=False, default=3)

    status = Column(String(50), nullable=False, default="queued", index=True)
    current_step = Column(String(100), nullable=False, default="Initializing")
    progress_pct = Column(Integer, nullable=False, default=0)

    initial_score = Column(Integer, nullable=True)
    final_score = Column(Integer, nullable=True)
    revision_count = Column(Integer, nullable=False, default=0)

    draft_report = Column(Text, nullable=True)
    final_report = Column(Text, nullable=True)
    critique_feedback = Column(Text, nullable=True)
    initial_critique = Column(Text, nullable=True)
    synthesized_notes = Column(Text, nullable=True)
    raw_search_summary = Column(Text, nullable=True)

    error_message = Column(Text, nullable=True)
    total_words = Column(Integer, nullable=False, default=0)
    elapsed_seconds = Column(Float, nullable=False, default=0.0)
    step_timings = Column(JSON, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    sources = relationship(
        "ResearchSource",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="ResearchSource.created_at",
    )
    bookmarks = relationship(
        "BookmarkedFinding",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="BookmarkedFinding.created_at",
    )
    qa_messages = relationship(
        "QAMessage",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="QAMessage.created_at",
    )


class ResearchSource(Base):
    __tablename__ = "research_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("research_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(2048), nullable=False)
    title = Column(String(500), nullable=False, default="Untitled Source")
    domain = Column(String(255), nullable=False, default="")
    snippet = Column(Text, nullable=True)
    scraped_content = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="discovered")  # discovered, scraped, failed, skipped
    error_reason = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)
    char_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    run = relationship("ResearchRun", back_populates="sources")


class BookmarkedFinding(Base):
    __tablename__ = "bookmarked_findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("research_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(500), nullable=False)
    quote_text = Column(Text, nullable=False)
    section_title = Column(String(255), nullable=True)
    source_url = Column(String(2048), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    run = relationship("ResearchRun", back_populates="bookmarks")


class QAMessage(Base):
    __tablename__ = "qa_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("research_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    is_grounded = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    run = relationship("ResearchRun", back_populates="qa_messages")
